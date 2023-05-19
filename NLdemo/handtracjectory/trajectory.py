import sys
sys.path.append("../")
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow
import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNet, Ridge, Lasso
from sklearn.model_selection import GridSearchCV
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class Ui_MainWindow(QMainWindow):
    def __init__(self, **data):
        super(Ui_MainWindow, self).__init__()
        try:
            self.dataset = data["dataset"]
            self.dataset_name = data["dataset_name"]
        except Exception as e:
            print(e)
        self.setupUi(self)
        self.initConfig()
        # self.handVelDecoding()
        self.plotTrajectory()

    def initConfig(self):
        self.labelData.setText(self.dataset_name)
    # def handVelDecoding(self):
    #     # self.dataset.resample(5)
    #     self.dataset.smooth_spk(50, name='smth_50')
    #     trial_data = self.dataset.make_trial_data(align_field='move_onset_time', align_range=(-130, 370))
    #     lagged_trial_data = self.dataset.make_trial_data(align_field='move_onset_time', align_range=(-50, 450))
    #     rates = trial_data.spikes_smth_50.to_numpy()
    #     vel = lagged_trial_data.hand_vel.to_numpy()
    #     gscv = GridSearchCV(ElasticNet(), {'alpha': np.logspace(-4, 0, 5)})
    #     gscv.fit(rates, vel)
    #     pred_vel = gscv.predict(rates)
    #     pred_vel_df = pd.DataFrame(pred_vel, index=lagged_trial_data.clock_time, columns=pd.MultiIndex.from_tuples([('pred_vel', 'x'), ('pred_vel', 'y')]))
    #     self.dataset.data = pd.concat([self.dataset.data, pred_vel_df], axis=1)
    
    def plotTrajectory(self):
        conds = self.dataset.trial_info.set_index(['trial_type', 'trial_version']).index.unique().tolist()
        cond = conds[23]
        mask = np.all(self.dataset.trial_info[['trial_type', 'trial_version']] == cond, axis=1)
        trial_data = self.dataset.make_trial_data(align_field='move_onset_time', align_range=(-50, 450), ignored_trials=(~mask))
        sc = MplCanvas(self.verticalLayoutWidget, width=10, height=5, dpi=100)
        toolbar = NavigationToolbar(sc, self.verticalLayoutWidget)
        t = np.arange(-50, 450, self.dataset.bin_width)
        for _, trial in trial_data.groupby('trial_id'):
            # True and predicted x velocity
            sc.axes[0].plot(t, trial.hand_vel.x, linewidth=0.7, color='black')
            # sc.axes[1][0].plot(t, trial.pred_vel.x, linewidth=0.7, color='blue')
            # True and predicted y velocity
            sc.axes[1].plot(t, trial.hand_vel.y, linewidth=0.7, color='black')
            # sc.axes[1][1].plot(t, trial.pred_vel.y, linewidth=0.7, color='blue')
            # True and predicted trajectories
            true_traj = np.cumsum(trial.hand_vel.to_numpy(), axis=0) * self.dataset.bin_width / 1000
            # pred_traj = np.cumsum(trial.pred_vel.to_numpy(), axis=0) * self.dataset.bin_width / 1000
            sc.axes[2].plot(true_traj[:, 0], true_traj[:, 1], linewidth=0.7, color='black')
            # sc.axes[1][2].plot(pred_traj[:, 0], pred_traj[:, 1], linewidth=0.7, color='blue')
        # Set up shared axes
        for i in range(1):
            sc.axes[0].set_xlim(-50, 450)
            sc.axes[1].set_xlim(-50, 450)
            # sc.axes[i][2].set_xlim(-180, 180)
            sc.axes[2].set_ylim(-130, 130)
        # Add labels
        sc.axes[0].set_title('X velocity (mm/s)')
        sc.axes[1].set_title('Y velocity (mm/s)')
        sc.axes[2].set_title('Reach trajectory')
        self.verticalLayout.addWidget(toolbar)
        self.verticalLayout.addWidget(sc)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(720, 480)
        MainWindow.setStyleSheet("color: rgb(57, 53, 98);\n"
"background-color: rgb(246, 242, 255);")
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.labelData = QtWidgets.QLabel(parent=self.centralwidget)
        self.labelData.setGeometry(QtCore.QRect(180, 20, 341, 32))
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
        self.axes = fig.subplots(1, 3)    # 表示将画布分为2x3的网格, 并把 返回画布网格对象
        super(MplCanvas, self).__init__(fig)