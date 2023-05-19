from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow
from primary import primary
from nlb_tools.nwb_interface import NWBDataset
from spikeplot import distributeHist, spikeRaster, rasterTrail
from handtracjectory import trajectory
import sys

# python .\main.py 
class Ui_MainWindow(QMainWindow):
    dataset_path_dicts = {
        "mc_maze": "../../nwbdatasets/000128/sub-Jenkins/",
        "mc_maze_large": "../../nwbdatasets/000138/sub-Jenkins/",
        "mc_maze_medium": "../../nwbdatasets/000139/sub-Jenkins/",
        "mc_maze_small": "../../nwbdatasets/000140/sub-Jenkins/",
        "mc_rtt": "../../nwbdatasets/000129/sub-Indy/",
        "area2_bump": "../../nwbdatasets/000127/sub-Han",
        "dmfc_rsg": "../../nwbdatasets/000130/sub-Haydn/",
    }
    data_args_dict = {
        "dataset_name": None,
        "spike_data_raw": None,
        "trial_info": None
    }
    retained_attrs = ["start_time", "target_on_time", "go_cue_time", "move_onset_time", "end_time"]
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.setWindowFlags(QtCore.Qt.WindowType.MSWindowsFixedSizeDialogHint)  # 只显示最小化和关闭按钮按键
        self.setupUi(self)
        self.dataset_name = None
        self.dataset = None
        self.trial_info = None
        self.spike_data_raw = None
        if self.loadArgsDict("mc_maze_small"):   # 展示默认数据集
            print(self.spike_data_raw.shape)
            self.m = primary.Ui_MainWindow(**self.data_args_dict)
            self.setCentralWidget(self.m)
        self.menu.triggered[QtGui.QAction].connect(self.onMenuDatasetLoad)
        self.menu_2.triggered[QtGui.QAction].connect(self.onSpikePlot)
        self.menu_3.triggered[QtGui.QAction].connect(self.onHandVel)

    # 依据 dataset_name, 加载数据
    def loadArgsDict(self, dataset_name):
        self.dataset_name = dataset_name
        self.data_load()
        self.load_spike_data()
        self.load_trial_info()
        if self.trial_info is not None and self.spike_data_raw is not None:
            self.data_args_dict["dataset_name"] = self.dataset_name
            self.data_args_dict["trial_info"] = self.trial_info
            self.data_args_dict["spike_data_raw"] = self.spike_data_raw
            return True
        return False
    # 读取原始数据
    def data_load(self):
        self.dataset = NWBDataset(self.dataset_path_dicts[self.dataset_name])
    # 过滤 trial_info
    def load_trial_info(self):
        trial_info = self.dataset.trial_info
        self.trial_info =  trial_info[trial_info["split"]!="test"][self.retained_attrs]
    # 过滤 spike_data_raw
    def load_spike_data(self):
        # 数据部分
        trial_data = self.dataset.data.copy()
        ### 注意列名为 MultiIndex, 先转为扁平列名 Index
        trial_data.columns = [(str(col[0])+'_'+str(col[1])) for col in trial_data.columns.values]
        ### 选出列名包含 spikes 的列
        self.spike_data_raw = trial_data[[col for col in trial_data.columns if "spikes" in col]]
        ### 重命名列, 转置, 删除 Nan 值(时间维)
        self.spike_data_raw.columns = ["Neuron"+str(i).zfill(3) for i in range(self.spike_data_raw.shape[1])]
        self.spike_data_raw = self.spike_data_raw.T
        self.spike_data_raw.dropna(axis=1, inplace=True)
    # 菜单 -- 数据集切换
    def onMenuDatasetLoad(self, act):
        if act.text() == "mc_maze":
            self.loadArgsDict("mc_maze")
            self.m = primary.Ui_MainWindow(**self.data_args_dict)
            self.setCentralWidget(self.m)
        elif act.text() == "mc_maze_large":
            self.loadArgsDict("mc_maze_large")
            self.m = primary.Ui_MainWindow(**self.data_args_dict)
            self.setCentralWidget(self.m)
        elif act.text() == "mc_maze_medium":
            self.loadArgsDict("mc_maze_medium")
            self.m = primary.Ui_MainWindow(**self.data_args_dict)
            self.setCentralWidget(self.m)
        # elif act.text() == "MC_RTT":
        #     # self.dataset_name = "mc_rtt"
        #     pass
        # elif act.text() == "Area2_Bump":
        #     # self.dataset_name = "area2_bump"
        #     pass
        # elif act.text() == "DMFC_RSG":
        #     # self.dataset_name = "dmfc_rsg"
        #     pass
        else:
            self.loadArgsDict("mc_maze_small")
            self.m = primary.Ui_MainWindow(**self.data_args_dict)
            self.setCentralWidget(self.m)
    # 菜单 -- 锋值活动
    def onSpikePlot(self, act):
        if act.text() == "Spiking Rates Distribution":
            self.m = distributeHist.Ui_MainWindow(**self.data_args_dict)
            self.setCentralWidget(self.m)
        elif act.text() == "Spike Rasters(Trial averged)":
            self.m = spikeRaster.Ui_MainWindow(**self.data_args_dict)
            self.setCentralWidget(self.m)
        elif act.text() == "Spike Rasters(Neuron split)":
            self.m = rasterTrail.Ui_MainWindow(**self.data_args_dict)
            self.setCentralWidget(self.m)
    # 菜单 -- 手部运动
    def onHandVel(self, act):
        if act.text() == "Trajectory":
            self.data_args_dict["dataset"] = self.dataset
            self.m = trajectory.Ui_MainWindow(**self.data_args_dict)
            self.setCentralWidget(self.m)
        else:
            pass
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(720, 500)
        font = QtGui.QFont()
        font.setFamily("Cambria Math")
        font.setPointSize(11)
        MainWindow.setFont(font)
        MainWindow.setStyleSheet("color: rgb(57, 53, 98);\n"
"background-color: rgb(246, 242, 255);")
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 720, 24))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        font.setBold(False)
        self.menubar.setFont(font)
        self.menubar.setStyleSheet("background-color: rgb(206, 171, 199);")
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(parent=self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(parent=self.menubar)
        self.menu_2.setObjectName("menu_2")
        self.menu_3 = QtWidgets.QMenu(parent=self.menubar)
        self.menu_3.setObjectName("menu_3")
        MainWindow.setMenuBar(self.menubar)
        self.actionOpen_directory = QtGui.QAction(parent=MainWindow)
        self.actionOpen_directory.setObjectName("actionOpen_directory")
        self.actionSpiking_Rates_Distribution = QtGui.QAction(parent=MainWindow)
        self.actionSpiking_Rates_Distribution.setObjectName("actionSpiking_Rates_Distribution")
        self.actionSpike_Rasters = QtGui.QAction(parent=MainWindow)
        self.actionSpike_Rasters.setObjectName("actionSpike_Rasters")
        self.actionMC_Maze_L = QtGui.QAction(parent=MainWindow)
        self.actionMC_Maze_L.setObjectName("actionMC_Maze_L")
        self.actionMC_Maze_M = QtGui.QAction(parent=MainWindow)
        self.actionMC_Maze_M.setObjectName("actionMC_Maze_M")
        self.actionMC_RTT = QtGui.QAction(parent=MainWindow)
        self.actionMC_RTT.setObjectName("actionMC_RTT")
        # self.actionArea2_Bump = QtGui.QAction(parent=MainWindow)
        # self.actionArea2_Bump.setObjectName("actionArea2_Bump")
        # self.actionDMFC_RSG = QtGui.QAction(parent=MainWindow)
        # self.actionDMFC_RSG.setObjectName("actionDMFC_RSG")
        self.actionMC_Maze_S = QtGui.QAction(parent=MainWindow)
        self.actionMC_Maze_S.setObjectName("actionMC_Maze_S")
        self.actionTrajectory = QtGui.QAction(parent=MainWindow)
        self.actionTrajectory.setObjectName("actionTrajectory")
        self.actionSipkeNeuron = QtGui.QAction(parent=MainWindow)
        self.actionSipkeNeuron.setObjectName("actionSipkeNeuron")
        
        self.menu.addAction(self.actionOpen_directory)
        self.menu.addAction(self.actionMC_Maze_L)
        self.menu.addAction(self.actionMC_Maze_M)
        self.menu.addAction(self.actionMC_Maze_S)
        # self.menu.addAction(self.actionMC_RTT)
        # self.menu.addAction(self.actionArea2_Bump)
        # self.menu.addAction(self.actionDMFC_RSG)
        self.menu_2.addAction(self.actionSpiking_Rates_Distribution)
        self.menu_2.addAction(self.actionSpike_Rasters)
        self.menu_2.addAction(self.actionSipkeNeuron)
        self.menu_3.addAction(self.actionTrajectory)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.menu_3.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menu.setTitle(_translate("MainWindow", "数据集"))
        self.menu_2.setTitle(_translate("MainWindow", "锋值活动"))
        self.menu_3.setTitle(_translate("MainWindow", "手部运动"))
        self.actionOpen_directory.setText(_translate("MainWindow", "mc_maze"))
        self.actionSpiking_Rates_Distribution.setText(_translate("MainWindow", "Spiking Rates Distribution"))
        self.actionSpike_Rasters.setText(_translate("MainWindow", "Spike Rasters(Trial averged)"))
        self.actionSipkeNeuron.setText(_translate("MainWindow", "Spike Rasters(Neuron split)"))
        self.actionMC_Maze_L.setText(_translate("MainWindow", "mc_maze_large"))
        self.actionMC_Maze_M.setText(_translate("MainWindow", "mc_maze_medium"))
        # self.actionMC_RTT.setText(_translate("MainWindow", "MC_RTT"))
        # self.actionArea2_Bump.setText(_translate("MainWindow", "Area2_Bump"))
        # self.actionDMFC_RSG.setText(_translate("MainWindow", "DMFC_RSG"))
        self.actionMC_Maze_S.setText(_translate("MainWindow", "mc_maze_small"))
        self.actionTrajectory.setText(_translate("MainWindow", "Trajectory"))
