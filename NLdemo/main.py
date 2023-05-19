# spikes: 锋值数据
# heldout_spikes: 锋值数据(测试数据集中该部分未知, 是预测目标)
# python -m PyQt6.uic.pyuic uis\stu.ui -o temp.py
# from nlb_tools.nwb_interface import NWBDataset
# from nlb_tools.make_tensors import make_train_input_tensors, make_eval_input_tensors
# from nlb_tools.make_tensors import make_eval_target_tensors, save_to_h5
# from nlb_tools.evaluation import evaluate
# from sklearn.linear_model import PoissonRegressor
# import scipy.signal as signal
# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd
import sys
from PyQt6 import QtWidgets
import appexec

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = appexec.Ui_MainWindow()
    ui.show()
    sys.exit(app.exec())
