# -*- coding: utf-8 -*-
"""
@Time ： 2022/1/11 14:30
@Auth ： 吕伟康
@File ：matplotlib_widget.py
"""
# -*- coding: utf-8 -*-
"""
@Time ： 2021/12/15 10:52
@Auth ： 吕伟康
@File ：matplotlib_widget.py
"""
import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar

from gui.Widget.Diag_oscillograph_new.Figure import MyMplCanvas


class MatPlotLibWidget(QWidget):
    def __init__(self, parent=None):
        super(MatPlotLibWidget, self).__init__(parent)
        self.init()
        time_test = QTimer(self)
        time_test.timeout.connect(self.updatanarray)
        # time_test.start(500)

        self.a = [1,2,3]
    def updatanarray(self):
        '''数据源 '''
        self.set_narry_xdata(self.a)
        self.set_narry_ydata(self.a)

    def init(self):
        self.layout = QVBoxLayout(self)
        self.mpl = MyMplCanvas(self, width=5, height=4, dpi=100)
        self.mpl_ntb = NavigationToolbar(self.mpl, self)
        self.layout.addWidget(self.mpl)
        self.layout.addWidget(self.mpl_ntb)

    def set_narry_xdata(self, newvalue):
        self.mpl.set_narry_xdata(newvalue)

    def set_narry_ydata(self, newvalue):
        self.mpl.set_narry_ydata(newvalue)

    def close_updata(self):
        self.mpl.close_updata()

    def start_updata(self):
        '''开启刷新'''
        self.mpl.start_updata()