import sys
sys.path.append("../")
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QTableWidgetItem, QAbstractItemView, QHeaderView
from PyQt6.QtWidgets import QMainWindow
## 组件映射表
# lineEdit_2: neurons
# lineEdit_3: time_start
# lineEdit_4: time_end
# label_10: channel
# label_11: spike_cnt
# pushButton: 实验平均
# pushButton_2: 单次实验
# label_5: trial_num
# label_7: ch_cnt
# label_9: time_cnt
# label_12: database


class Ui_MainWindow(QMainWindow):
    # table 展示数据范围
    neurons = 20
    time_start = 0
    time_end = 20
    def __init__(self, **data):
        super(Ui_MainWindow, self).__init__()
        try:
            self.dataset_name = data["dataset_name"]
            self.spike_data_raw = data["spike_data_raw"]
            self.trial_info = data["trial_info"]
        except Exception as e:
            print(e)
        self.setupUi(self)
        self.editLimit()
        self.labelFlush()
        self.flush_table()
        self.pushButton.clicked.connect(self.onTableFlushed)
        self.tableWidget.itemClicked.connect(self.onClickTable)

    def labelFlush(self):
        self.label_12.setText("数据集: "+self.dataset_name)
        self.lineEdit_2.setText(str(self.neurons))
        self.lineEdit_3.setText(str(self.time_start))
        self.lineEdit_4.setText(str(self.time_end))
        self.label_5.setText(str(self.trial_info.shape[0]))
        self.label_7.setText(str(self.spike_data_raw.shape[0]))
        self.label_9.setText(str(self.spike_data_raw.shape[1]))
        self.label_10.setText(str("channel"))
        self.label_11.setText(str("spike-cnt"))
    # 设定 editLimit
    def editLimit(self):
        regNum = QtCore.QRegularExpression("\d+")
        self.lineEdit_2.setValidator(QtGui.QRegularExpressionValidator(regNum))
        self.lineEdit_3.setValidator(QtGui.QRegularExpressionValidator(regNum))
        self.lineEdit_4.setValidator(QtGui.QRegularExpressionValidator(regNum))
    # 点击刷新按钮刷新表单数据
    def onTableFlushed(self):
        self.neurons = int(self.lineEdit_2.text())
        self.time_start = int(self.lineEdit_3.text())
        self.time_end = int(self.lineEdit_4.text())
        self.flush_table()
    # 点击列表的某一项
    def onClickTable(self, item):
        r = item.row()
        ch_name = self.tableWidget.verticalHeaderItem(r).text()
        self.label_10.setText(ch_name)
        spike_tt_cnt = self.spike_data_raw.loc[ch_name].sum()
        self.label_11.setText(str(spike_tt_cnt))
    # 刷新表单数据
    def flush_table(self):
        # 1. 计算 行数 和 列数
        time_steps = self.time_end - self.time_start
        self.tableWidget.setRowCount(self.neurons)
        self.tableWidget.setColumnCount(time_steps)
        # 2. 设置 表头(行\列)
        hz_header = [str(self.time_start+i).zfill(5) for i in range(time_steps)]
        vt_header = self.spike_data_raw.index[: self.neurons]
        self.tableWidget.setHorizontalHeaderLabels(hz_header)
        self.tableWidget.setVerticalHeaderLabels(vt_header)
        # 3. 填充数据
        for i in range(self.neurons):
            for j in range(time_steps):
                d = self.spike_data_raw.iloc[i, self.time_start+j]
                item = QTableWidgetItem(str(d))
                self.tableWidget.setItem(i, j, item)
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(720, 480)
        MainWindow.setStyleSheet("color: rgb(57, 53, 98);\n"
"background-color: rgb(246, 242, 255);")
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(90, 60, 81, 20))
        font = QtGui.QFont()
        font.setFamily("Cambria Math")
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.lineEdit_2 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(170, 60, 72, 20))
        font = QtGui.QFont()
        font.setFamily("Cambria Math")
        font.setPointSize(11)
        self.lineEdit_2.setFont(font)
        self.lineEdit_2.setText("")
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.label_5 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(110, 440, 60, 32))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.tableWidget = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(30, 89, 631, 351))
        font = QtGui.QFont()
        font.setFamily("Cambria")
        font.setPointSize(10)
        self.tableWidget.setFont(font)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(50)
        self.tableWidget.verticalHeader().setDefaultSectionSize(30)
        self.label_3 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(250, 60, 81, 20))
        font = QtGui.QFont()
        font.setFamily("Cambria Math")
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.lineEdit_3 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit_3.setGeometry(QtCore.QRect(330, 60, 72, 20))
        font = QtGui.QFont()
        font.setFamily("Cambria Math")
        font.setPointSize(11)
        self.lineEdit_3.setFont(font)
        self.lineEdit_3.setText("")
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.label_6 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(280, 440, 80, 32))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_6.setFont(font)
        self.label_6.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.label_10 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(480, 10, 80, 32))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_10.setFont(font)
        self.label_10.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_10.setObjectName("label_10")
        self.label_13 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_13.setGeometry(QtCore.QRect(420, 60, 81, 20))
        font = QtGui.QFont()
        font.setFamily("Cambria Math")
        font.setPointSize(12)
        self.label_13.setFont(font)
        self.label_13.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_13.setObjectName("label_13")
        self.label_8 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(520, 440, 80, 32))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_8.setFont(font)
        self.label_8.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(390, 10, 75, 32))
        self.pushButton.setObjectName("pushButton")
        self.label_7 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(360, 440, 60, 32))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_7.setFont(font)
        self.label_7.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.lineEdit_4 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit_4.setGeometry(QtCore.QRect(500, 60, 72, 20))
        font = QtGui.QFont()
        font.setFamily("Cambria Math")
        font.setPointSize(11)
        self.lineEdit_4.setFont(font)
        self.lineEdit_4.setText("")
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.label_4 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(30, 440, 60, 32))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.label_9 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(600, 440, 60, 32))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_9.setFont(font)
        self.label_9.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.label_12 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_12.setGeometry(QtCore.QRect(30, 10, 341, 32))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_12.setFont(font)
        self.label_12.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_12.setObjectName("label_12")
        self.label_11 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(580, 10, 80, 32))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_11.setFont(font)
        self.label_11.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_11.setObjectName("label_11")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_2.setText(_translate("MainWindow", "neurons:"))
        self.label_5.setText(_translate("MainWindow", "trial_num"))
        self.label_3.setText(_translate("MainWindow", "time_start:"))
        self.label_6.setText(_translate("MainWindow", "spike通道数"))
        self.label_10.setText(_translate("MainWindow", "Name"))
        self.label_13.setText(_translate("MainWindow", "time_end:"))
        self.label_8.setText(_translate("MainWindow", "总时间步数"))
        self.pushButton.setText(_translate("MainWindow", "刷新"))
        self.label_7.setText(_translate("MainWindow", "ch_cnt"))
        self.label_4.setText(_translate("MainWindow", "实验次数"))
        self.label_9.setText(_translate("MainWindow", "time_cnt"))
        self.label_12.setText(_translate("MainWindow", "database"))
        self.label_11.setText(_translate("MainWindow", "spike_cnt"))
