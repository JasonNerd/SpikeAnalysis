"""
这里使用另一个视角画栅格图
self.trial_arr = trial_num x spike_num x time_steps
对于每一个 spike (axis=1), 画出一幅图:
上方是栅格图, 横轴 time_steps, 纵轴 trial_num
下方是PSTH, 横轴 time_steps, 纵轴 spike_num(trial sumed)
"""
import sys
sys.path.append("../")
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class Ui_MainWindow(QMainWindow):
    align_tlist = ["target_on_time", "go_cue_time", "move_onset_time"]
    def __init__(self, **data):
        super(Ui_MainWindow, self).__init__()
        try:
            self.dataset_name = data["dataset_name"]
            # 注意这里进行了转置, 使得 index(行) 变为 time 维, 方便切分时间段
            self.spike_data_raw = data["spike_data_raw"].T
            self.trial_info = data["trial_info"]
        except Exception as e:
            print(e)
        self.setupUi(self)
        self.editLimit()
        self.trial_arr = None
        self.splitTrialData()
        # print("split data to (trial_num x spike_num x time_steps)")
        self.psth = None
        self.calPSTH()
        self.labelData.setText(self.dataset_name)
        # print("sum data to (spike_num x time_steps)")
        self.raster = None
        self.calRaster()
        # print("raster data as (spike_num x trial_num x time_step_n)")
        self.setNeuronID()
        self.lineEdit.editingFinished.connect(self.setNeuronID)
    # 划分实验数据
    def splitTrialData(self):
        align_t = "go_cue_time"
        align_start = 250
        align_stop = 249
        n_trial = self.trial_info.shape[0]  # 实验次数
        n_channel = self.spike_data_raw.shape[1]    # 通道数
        if align_start != "" and align_stop != "":
            align_range = (-int(align_start), int(align_stop))
            start_offset, end_offset = pd.to_timedelta(align_range, unit='ms')
            self.n_time = align_range[1]-align_range[0]+1    # 时间步数
            self.trial_arr = np.zeros((n_trial, n_channel, self.n_time))  # n_trial, n_channel, n_time 三维数据
            for i in range(n_trial):
                t = self.trial_info.iloc[i][align_t]
                self.trial_arr[i] = self.spike_data_raw.loc[t+start_offset: t+end_offset].T.values
            return True
        return False
    def calRaster(self):
        # self.trial_arr = trial_num x spike_num x time_steps
        self.raster = []  # spike_num x [trial_num x spike_cnt(i)]
        trial_num = self.trial_arr.shape[0]
        spike_num = self.trial_arr.shape[1]
        time_steps = self.trial_arr.shape[2]
        # print(self.trial_arr.shape)
        for i in range(spike_num):
            spi_o = [] # i 号神经元, 在历次实验中 所有具有脉冲发射的时刻
            for j in range(trial_num):
                spij_o = []     # 记录了 i 号神经元, 在第 j 号实验中 所有具有脉冲发射的时刻
                for k in range(time_steps):
                    if self.trial_arr[j, i, k] > 0:    # 对于 i 号神经元, 在第 j 号实验中 的 第 k 个时刻具有脉冲
                        spij_o.append(k)
                spi_o.append(spij_o)
            self.raster.append(spi_o)
    def setNeuronID(self):
        neuronID = int(self.lineEdit.text())
        self.plotNeuronPSTH(neuronID)

    def calPSTH(self):
        self.psth = self.trial_arr.sum(axis=0) # spike_num x time_steps [i, j] -> spike_num
        spike_num = self.psth.shape[0]
        time_steps = self.psth.shape[1]
        self.psth2 = []
        for i in range(spike_num):
            h_tsn = []
            for j in range(time_steps):
                for r in range(int(self.psth[i, j])):
                    h_tsn.append(j)
            self.psth2.append(h_tsn)

    def smooth_kernel(self):
        return np.array([0.03, 0.05, 0.08, 0.1, 0.11, 0.13, 0.13, 0.11, 0.1, 0.08, 0.05, 0.03])
    # 绘制某一神经元的数据
    def plotNeuronPSTH(self, neuronID):
        if neuronID >= self.trial_arr.shape[1]:
            return
        sc = MplCanvas(self.verticalLayoutWidget, width=10, height=5, dpi=100)
        toolbar = NavigationToolbar(sc, self.verticalLayoutWidget)
        kernel = self.smooth_kernel()
        sc.rasterPlot.eventplot(self.raster[neuronID], colors="#4f404b")
        psth_data = np.convolve(self.psth[neuronID].copy(), kernel, mode="same")
        sc.psthPlot.plot(list(range(len(psth_data))), psth_data)
        sc.psthPlot.hist(self.psth2[neuronID], facecolor="#4f404b", bins=50)
        print(psth_data)
        sc.rasterPlot.set_title(f"Rasters and PSTH of Neuron {neuronID}")
        sc.rasterPlot.set_ylabel(f"Totally {self.trial_arr.shape[0]} Trials.")
        sc.psthPlot.set_ylabel(f"psth of neuron {neuronID}.")
        # 先清空布局中的控件
        self.clearCanvas()
        self.verticalLayout.addWidget(toolbar)
        self.verticalLayout.addWidget(sc)
        
    def editLimit(self):
        regNum = QtCore.QRegularExpression("\d+")
        self.lineEdit.setValidator(QtGui.QRegularExpressionValidator(regNum))
        self.lineEdit.setPlaceholderText("神经元编号")
        self.lineEdit.setText("0")
    # 设置画布, 绘制直方图
    def clearCanvas(self):
        ch_cnt = self.verticalLayout.count()
        ch_list = list(range(ch_cnt))
        for i in ch_list:
            self.verticalLayout.itemAt(i).widget().deleteLater()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(720, 480)
        MainWindow.setStyleSheet("color: rgb(57, 53, 98);\n"
"background-color: rgb(246, 242, 255);")
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.labelData = QtWidgets.QLabel(parent=self.centralwidget)
        self.labelData.setGeometry(QtCore.QRect(360, 20, 341, 32))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.labelData.setFont(font)
        self.labelData.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.labelData.setObjectName("labelData")
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 70, 671, 381))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lineEdit = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(100, 20, 181, 31))
        font = QtGui.QFont()
        font.setFamily("Cambria Math")
        font.setPointSize(12)
        self.lineEdit.setFont(font)
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.labelData.setText(_translate("MainWindow", "database"))

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.rasterPlot, self.psthPlot = fig.subplots(2, 1)    # 表示将画布分为 2x1的网格, 并把 返回画布网格对象
        super(MplCanvas, self).__init__(fig)