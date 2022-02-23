# -*- coding: utf-8 -*-
"""
@Time ： 2022/1/11 14:30
@Auth ： 吕伟康
@File ：MYplotweight.py
"""
# -*- coding: utf-8 -*-
"""
@Time ： 2021/9/2 15:38
@Auth ： 吕伟康
@File ：MYplotweight.py
"""
from PyQt5.QtCore import Qt
from pyqtgraph import PlotWidget
from PyQt5.QtGui import QKeySequence

class MYPlotWidget(PlotWidget):


    def keyPressEvent(self, ev):
       if ev.key() == 16777249:
           self.plotItem.vb.setMouseMode(3 if self.plotItem.vb.state['mouseMode'] == 1 else 1)

    def wheelEvent(self, a0) -> None:
        # if not self.mouse:
        #     return
        # print('ssssssss')
        super(MYPlotWidget, self).wheelEvent(a0)


    def mouseMoveEvent(self, ev):
        self.mouse = True
        super(MYPlotWidget, self).mouseMoveEvent(ev)

    def mousePressEvent(self, ev):
        self.mouse = False
        super(MYPlotWidget, self).mousePressEvent(ev)




