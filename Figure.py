# -*- coding: utf-8 -*-
"""
@Time ： 2022/1/11 14:29
@Auth ： 吕伟康
@File ：Figure.py
"""
# -*- coding: utf-8 -*-
"""
@Time ： 2021/12/15 10:56
@Auth ： 吕伟康
@File ：Figure.py
"""
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        plt.rcParams['font.family'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axis = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.create_updata()

        self.narry_xdata = np.array([1,2,3])
        self.narry_ydata = np.array([1,2,3])



    def set_narry_xdata(self, newvalue):
        self.narry_xdata = np.array(newvalue)

    def set_narry_ydata(self, newvalue):
        self.narry_ydata = np.array(newvalue)

    def start_updata(self):
        '''开启刷新'''
        self.updata.start(100)

    def close_updata(self):
        '''关闭刷新'''
        self.updata.stop()

    def create_updata(self):
        '''创建刷新定时器'''
        self.updata = QTimer(self)
        self.updata.timeout.connect(self.updata_axis)

    def updata_axis(self):
        '''绘制图形'''
        self.axis.cla()
        self.axis.plot( self.narry_xdata, self.narry_ydata, 'r')
        self.draw()


