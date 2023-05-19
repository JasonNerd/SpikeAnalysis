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
        self.setInitConfig()
        self.onRangeFlushed()
        self.pushButton.clicked.connect(self.onRangeFlushed)
    # 设定 editLimit
    def editLimit(self):
        regNum = QtCore.QRegularExpression("\d+")
        self.lineEditAStaO.setValidator(QtGui.QRegularExpressionValidator(regNum))
        self.lineEditAstoO.setValidator(QtGui.QRegularExpressionValidator(regNum))
        self.labelData.setText(self.dataset_name)
    # 设定初始值: 下拉列表, start_offset, stop_offset
    def setInitConfig(self):
        self.comboBox.addItems(self.align_tlist)
        self.comboBox.setCurrentIndex(1)
        self.lineEditAStaO.setText("250")
        self.lineEditAstoO.setText("249")
    # 划分实验数据
    def splitTrialData(self):
        align_t = self.comboBox.currentText()
        align_start = self.lineEditAStaO.text()
        align_stop = self.lineEditAstoO.text()
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
    # 设置画布, 绘制直方图
    def clearCanvas(self):
        ch_cnt = self.verticalLayout.count()
        ch_list = list(range(ch_cnt))
        for i in ch_list:
            self.verticalLayout.itemAt(i).widget().deleteLater()
    def plotDistribution(self):
        # 1. 从实验维度进行平均
        print(self.trial_arr.shape)
        trial_mean = self.trial_arr.mean(axis=0) # spike_num x time_steps
        # 2. 找出 每个 channel 所有具有发射 的时刻
        dataPlot = []
        for i in range(trial_mean.shape[0]):
            lauchT = []
            print(i, end=": ")
            for j in range(trial_mean.shape[1]):
                if trial_mean[i, j] > 0.02: # 认为在 时间槽j 处 通道i 具有脉冲发射
                    lauchT.append(j)
                    # print(j, end=", ")
            dataPlot.append(lauchT)
        # 3. 作栅格图
        sc = MplCanvas(self.verticalLayoutWidget, width=4.8, height=3.6, dpi=100)
        sc.axes.eventplot(dataPlot, linelengths=0.7, colors="#4f404b")
        sc.axes.set_title(f"Spike rasters aligned to {self.comboBox.currentText()}(trial averaged)")
        sc.axes.set_xlabel("time sequence (ms/bin)")
        sc.axes.set_ylabel(f"{trial_mean.shape[0]} Channels")
        toolbar = NavigationToolbar(sc, self.verticalLayoutWidget)
        # 先清空布局中的控件
        self.clearCanvas()
        self.verticalLayout.addWidget(toolbar)
        self.verticalLayout.addWidget(sc)
    
    # 刷新参数
    def onRangeFlushed(self):
        self.splitTrialData()
        self.plotDistribution()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(720, 480)
        MainWindow.setStyleSheet("color: rgb(57, 53, 98);\n"
"background-color: rgb(246, 242, 255);")
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.labelData = QtWidgets.QLabel(parent=self.centralwidget)
        self.labelData.setGeometry(QtCore.QRect(20, 20, 341, 32))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.labelData.setFont(font)
        self.labelData.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.labelData.setObjectName("labelData")
        self.labelAt = QtWidgets.QLabel(parent=self.centralwidget)
        self.labelAt.setGeometry(QtCore.QRect(20, 70, 81, 20))
        font = QtGui.QFont()
        font.setFamily("Cambria Math")
        font.setPointSize(12)
        self.labelAt.setFont(font)
        self.labelAt.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.labelAt.setObjectName("labelAt")
        self.labelAStaO = QtWidgets.QLabel(parent=self.centralwidget)
        self.labelAStaO.setGeometry(QtCore.QRect(250, 70, 144, 20))
        font = QtGui.QFont()
        font.setFamily("Cambria Math")
        font.setPointSize(12)
        self.labelAStaO.setFont(font)
        self.labelAStaO.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.labelAStaO.setObjectName("labelAStaO")
        self.lineEditAStaO = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEditAStaO.setGeometry(QtCore.QRect(400, 70, 72, 22))
        font = QtGui.QFont()
        font.setFamily("Cambria Math")
        font.setPointSize(11)
        self.lineEditAStaO.setFont(font)
        self.lineEditAStaO.setText("")
        self.lineEditAStaO.setObjectName("lineEditAStaO")
        self.labelAStoO = QtWidgets.QLabel(parent=self.centralwidget)
        self.labelAStoO.setGeometry(QtCore.QRect(480, 70, 144, 20))
        font = QtGui.QFont()
        font.setFamily("Cambria Math")
        font.setPointSize(12)
        self.labelAStoO.setFont(font)
        self.labelAStoO.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.labelAStoO.setObjectName("labelAStoO")
        self.lineEditAstoO = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEditAstoO.setGeometry(QtCore.QRect(630, 70, 72, 22))
        font = QtGui.QFont()
        font.setFamily("Cambria Math")
        font.setPointSize(11)
        self.lineEditAstoO.setFont(font)
        self.lineEditAstoO.setText("")
        self.lineEditAstoO.setObjectName("lineEditAstoO")
        self.comboBox = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(110, 70, 131, 22))
        self.comboBox.setObjectName("comboBox")
        self.pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(600, 10, 100, 42))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(80, 110, 571, 341))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.labelData.setText(_translate("MainWindow", "database"))
        self.labelAt.setText(_translate("MainWindow", "Align_time:"))
        self.labelAStaO.setText(_translate("MainWindow", "Align_Start_Offeset:"))
        self.labelAStoO.setText(_translate("MainWindow", "Align_Stop_Offeset:"))
        self.pushButton.setText(_translate("MainWindow", "刷新"))

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5., height=4., dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)