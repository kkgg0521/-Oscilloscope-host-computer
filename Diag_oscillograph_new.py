# -*- coding: utf-8 -*-
"""
@Time ： 2022/1/11 14:29
@Auth ： 吕伟康
@File ：Diag_oscillograph_new.py
"""
# -*- coding: utf-8 -*-
"""
@Time ： 2021/8/17 10:27
@Auth ： 吕伟康
@File ：Diag_oscillator_new.py
"""
import time

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QThread
# from PyQt5.QtGui import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QHeaderView, QFileDialog
import sys
import numpy as np
from pyqtgraph import PlotCurveItem, InfiniteLine
import pyqtgraph as pg

import Diag_oscillograph_new_ui
import Diag_oscillgraph_lineconfig
from Diag_oscillgraph_circleconfig import CircleConfigTableModel, \
    CircleConfigTableDelegate
from Diag_oscillgraph_lineconfig import ConfigTableDelegate

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
# 鼠标交互 左键放大
pg.setConfigOption('leftButtonPan', False)

pg.setConfigOption('antialias', True)
# pg.setConfigOption('useOpenGL',True)
# pg.setConfigOption('mouseRateLimit',100 )
pg.setConfigOption('exitCleanup',True)

class Diag_oscillograph_new(QMainWindow, Diag_oscillograph_new_ui.Ui_MainWindow):
    plotrefresh = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super(Diag_oscillograph_new, self).__init__(parent)
        self.setupUi(self)


        self.data = np.zeros(shape=(1999999, 9))
        for index, i in enumerate(self.data):
            i[8] = index
        self.data[1, 8] = 1
        self.data_len_array = np.ones(shape=8, dtype=int)
        '''x 轴显示'''
        self.showminx = 0
        self.showmaxx = 6000
        '''y 轴显示'''
        self.showminy = -2
        self.showmaxy = 2
        self.lastshowminx = 0
        self.lastshowmaxx = 6000
        self.lastshowminy = -2
        self.lastshowmaxy = 2

        self.oscilloscope_widget.setLimits(minXRange=10, maxXRange=100000000000, maxYRange=100000000000)

        self.cofigmodel = Diag_oscillgraph_lineconfig.ConfigTableModel(self)
        self.tableView_ConfigTable.setModel(self.cofigmodel)
        self.doag = Diag_oscillgraph_lineconfig.ConfigTableDelegate()
        self.tableView_ConfigTable.setItemDelegate(self.doag)


        self.circlemodel = CircleConfigTableModel(self)
        self.tableView_circle.setModel(self.circlemodel)
        self.circle_Delegate = CircleConfigTableDelegate(self)
        self.tableView_circle.setItemDelegate(self.circle_Delegate)
        self.tableView_circle.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView_circle.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)


        self.oscilloscope_init()
        self.data_for_draw = []

        self.pushButtonupdata.clicked.connect(self.startorstop)
        self.isstart = False

        self.pushButton_all.clicked.connect(self.show_all_plot)
        self.pushButton_AutoRange.clicked.connect(self.AutoRange)

        self.checkBox_xline.clicked.connect(self.put_Xline)
        self.checkBox_yline.clicked.connect(self.put_Yline)

        '''刷新方式注释为定时器刷新, 未注释为线程刷新-危险操作'''
        self.Plotrefreshtime = QTimer()
        self.Plotrefreshtime.timeout.connect(self.updata)
        self.Plotrefreshthund = Plotrefreshthread(self)
        self.plotrefresh.connect(self.updata)

        self.add_xline()

        self.oscilloscope_widget.sigRangeChanged.connect(self.updateRegion)

        self.pushButton_refreshview.clicked.connect(self.changeView)
        self.pushButton_last_position.clicked.connect(self.lastposition)

        self.checkBox_time.clicked.connect(self.time_resh)

        self.pushButton_clear_all_data.clicked.connect(self.dataclear)

        self.checkBox_kadun.clicked.connect(self.kadun)
        self.checkBox_shownc.clicked.connect(self.shownctableview)
        self.tableView_nc.hide()



        '''精确点位置'''
        # self.setMouseTracking(True)
        self.oscilloscope_widget.scene().sigMouseMoved.connect(self.onMouseMoved)
        self.checkBox_precise_point_position.clicked.connect(self.startmousemove)
        self.mouse_line()
        '''链接模块部分'''
        self.collect_data_th = collectthread(self)
        # self.check_draw_corur()
        self.value_index = []
        # self.V3()

        self.pushButton.clicked.connect(self.savedata)


    def savedata(self):
        self.savepath = QFileDialog.getSaveFileName(self, "保存文件夹",'*.csv' )[0]
        if self.savepath == '':
            pass
        else:
            np.savetxt(self.savepath, self.data, fmt='%d',delimiter=',')

    def close_collect_thread(self):
        self.thunkquit()


    def AutoRange(self):
        '''区分巡圆 和普通模式, 普通模式直接显示全图显示功能'''
        self.oscilloscope_widget.enableAutoRange()


    def startmousemove(self):
        # self.setMouseTracking(self.checkBox_precise_point_position.isChecked())
        if self.checkBox_precise_point_position.isChecked():
            # self.oscilloscope_widget.plotItem.vb.setMouseMode(3)
            self.oscilloscope_widget.addItem(self.mouse_line_x, ignoreBounds=True)
            self.oscilloscope_widget.addItem(self.mouse_line_y, ignoreBounds=True)
        else:
            # self.oscilloscope_widget.plotItem.vb.setMouseMode(1)
            self.oscilloscope_widget.removeItem(self.mouse_line_x)
            self.oscilloscope_widget.removeItem(self.mouse_line_y)

    def onMouseMoved(self, evt):
        if self.oscilloscope_widget.plotItem.vb.mapSceneToView(evt):
            point = self.oscilloscope_widget.plotItem.vb.mapSceneToView(evt)
            self.lineEdit_point_position_x.setText(str(round(point.x(),2)))
            self.lineEdit_lineEdit_point_position_y.setText(str(round(point.y(),2)))

            if 0 < int(point.x()) < np.min(self.data_len_array):
                for i in range(8):
                    self.cofigmodel._data[i, 5] = int(point.x())
                    self.cofigmodel._data[i, 6] = self.data[int(point.x()), i] * self.cofigmodel._data[i, 3] + \
                                                  self.cofigmodel._data[i, 4]
                self.cofigmodel.modelReset()

            if self.checkBox_precise_point_position.isChecked():
                self.mouse_line_x.setPos(point.x())
                self.mouse_line_y.setPos(point.y())

    def shownctableview(self):
        if self.checkBox_shownc.isChecked():
            self.tableView_nc.show()
        else:
            self.tableView_nc.hide()

    def showEvent(self, a0) -> None:
        if self.isVisible():
            self.check_draw_corur()
        # self.cofigmodel.modelReset()

    def kadun(self):

        if self.checkBox_kadun.isChecked():
            self.spinBox_kdun.setEnabled(False)
            self.spinBox_Peak_points.setEnabled(False)
        else:
            self.spinBox_kdun.setEnabled(True)
            self.spinBox_Peak_points.setEnabled(True)

    def V3(self):
        '''脱离注释掉此函数'''
        self.checkBox_cnc.clicked.connect(self.startorclosecnc)
        self.checkBox_collection.clicked.connect(self.collect_data_from_cnc)
        self.checkBox_xcircle.clicked.connect(self.twodata)
        self.xcircle = self.oscilloscope_widget.plot(title='circle')
        self.xcircle.opts['pen'] = pg.mkPen(QColor('red'), width=2)
        self.xcircle_2 = self.oscilloscope_widget.plot(title='circle_2')
        self.xcircle_2.opts['pen'] = pg.mkPen(QColor('blue'), width=2)

        self.pushButton_circle_xtoy.clicked.connect(self.changgeview)
        self.xtoy = True

    def show_all_plot(self):

        maxnum = np.max(self.data, axis=0)
        minnum = np.min(self.data, axis=0)
        del_lis = []
        for index, val in enumerate(self.cofigmodel.show_flag):
            maxnum[index] = maxnum[index] * int(self.cofigmodel._data[index][3]) + int(self.cofigmodel._data[index][4])
            minnum[index] = minnum[index] * int(self.cofigmodel._data[index][3]) + int(self.cofigmodel._data[index][4])
            if not val:
                del_lis.append(index)

        if not del_lis:
            maxnum = np.max(np.delete(maxnum, del_lis))
            minnum = np.min(np.delete(minnum, del_lis))
        else:
            maxnum = np.max(maxnum)
            minnum = np.min(minnum)

        self.oscilloscope_widget.setYRange(minnum, maxnum, padding=0.1)  # Y区间
        leng = np.max(self.data_len_array)
        self.oscilloscope_widget.setXRange(leng - self.spinBox_time_limt.value(), leng, padding=0.1)

    def changgeview(self):

        self.xtoy = not self.xtoy
        if self.xtoy:
            self.lineEdit_ciecle_x.setText(self.cursor_list[self.xcircle_Y_index].title)
            self.lineEdit_ciecle_y.setText(self.cursor_list[self.xcircle_X_index].title)
        else:
            self.lineEdit_ciecle_x.setText(self.cursor_list[self.xcircle_X_index].title)
            self.lineEdit_ciecle_y.setText(self.cursor_list[self.xcircle_Y_index].title)

    def collect_data_from_cnc(self):
        if self.checkBox_collection.isChecked():
            self.tunkstart()
        else:
            self.thunkquit()

    def twodata(self):
        if list(self.cofigmodel.show_flag).count(1) == 2:
            self.tableView_ConfigTable.setEnabled(not self.tableView_ConfigTable.isEnabled())
            if not self.tableView_ConfigTable.isEnabled():
                '''巡圆开启'''
                first = 0
                for i, val in enumerate(self.cofigmodel.show_flag):
                    if val == 1:
                        if not first:
                            self.xcircle_X_index = i
                            first = first + 1
                        else:
                            self.xcircle_Y_index = i

                self.xcircle_enable(True)
            else:
                '''巡圆关闭'''
                self.xcircle_enable(False)

        else:
            self.checkBox_xcircle.setChecked(False)

    def xcircle_enable(self, able):
        self.oscilloscope_widget.setAspectLocked(able)
        self.pushButton_circle_xtoy.setEnabled(able)
        self.doubleSpinBox_xcircle_coefficient.setEnabled(able)
        self.doubleSpinBox_xcircle_coefficient_y.setEnabled(able)
        self.doubleSpinBox_xcircle_intercept.setEnabled(able)
        self.doubleSpinBox_xcircle_intercept_y.setEnabled(able)
        self.combox_xcircle_choosecorcle.setEnabled(able)
        self.pushButton_surechange_xcircle.setEnabled(able)

        if able:
            '''两天线'''
            self.cursor_list[self.xcircle_X_index].hide()
            self.cursor_list[self.xcircle_Y_index].hide()
            '''巡圆线'''
            self.xcircle.show()
            self.xcircle_2.show()
            '''显示名称'''
            self.lineEdit_ciecle_x.setText(self.cursor_list[self.xcircle_X_index].title)
            self.lineEdit_ciecle_y.setText(self.cursor_list[self.xcircle_Y_index].title)
            # self.line_cursor.hide()
        else:
            self.cursor_list[self.xcircle_X_index].show()
            self.cursor_list[self.xcircle_Y_index].show()
            self.xcircle.hide()
            self.xcircle_2.hide()
            # self.line_cursor.show()

    def Xcircle_start(self, able):
        if 1 in able:
            self.oscilloscope_widget.setAspectLocked(True)
            if able[0]:
                self.xcircle.show()
                for i,value in enumerate(self.cursor_list):
                    if value.title == self.circlemodel.circlr_line_name[0]:
                        self.circle_x_index = i
                    if value.title == self.circlemodel.circlr_line_name[1]:
                        self.circle_y_index = i
            if able[1]:
                self.xcircle_2.show()
                for i,value in enumerate(self.cursor_list):
                    if value.title == self.circlemodel.circlr_line_name_2[0]:
                        self.circle_2_x_index = i
                    if value.title == self.circlemodel.circlr_line_name_2[1]:
                        self.circle_2_y_index = i

        else:
            self.oscilloscope_widget.setAspectLocked(False)
            self.xcircle.hide()
            self.xcircle_2.hide()

    def tunkstart(self):
        print('采集线程开启！')
        self.collect_data_th.runningflag = True
        self.collect_data_th.start()

    def thunkquit(self):

        self.collect_data_th.runningflag = False
        # self.collect_data_th.terminate()

    def dataclear(self):

        self.data.fill(0)
        for index, i in enumerate(self.data):
            i[8] = index
        self.data_len_array.fill(0)

    def oscilloscope_init(self):
        # self.oscilloscope_widget.setMouseMode(self.oscilloscope_widget.RectMode)
        self.oscilloscope_widget.setMenuEnabled(False)
        self.oscilloscope_widget.hideButtons()

        self.oscilloscope_widget.setYRange(self.showminy, self.showmaxy, padding=0)  # Y区间
        self.oscilloscope_widget.setXRange(self.showminx, self.showmaxx, padding=0)
        '''显示区间'''
        self.doubleSpinBox_xmin.setValue(self.showminx)
        self.doubleSpinBox_xmax.setValue(self.showmaxx)
        self.doubleSpinBox_ymin.setValue(self.showminy)
        self.doubleSpinBox_ymax.setValue(self.showmaxy)
        '''网格'''
        self.oscilloscope_widget.showGrid(x=True, y=True)

        '''进行线'''
        self.line_cursor = InfiniteLine(angle=90,
                                        movable=False,
                                        pen="#0000FF",
                                        label='{value}')
        self.line_cursor.setPen(color="#0000FF", width=2)
        self.line_cursor_local = 0
        self.oscilloscope_widget.addItem(self.line_cursor, ignoreBounds=True)
        self.line_cursor.hide()

        self.create_cursor_list()

    def changecolor(self, row, color):
        self.cursor_list[row].opts['pen'] = pg.mkPen(QColor(color), width=2)

    def changeshowcusor(self, row, statue):
        if statue:
            self.cursor_list[row].show()
        else:
            self.cursor_list[row].hide()

    def create_cursor_list(self):
        self.cursor_list = []
        for i in range(8):
            self.cursor_list.append(self.oscilloscope_widget.plot())
            self.cursor_list[i].opts['pen'] = pg.mkPen(QColor(self.cofigmodel.colors[i]), width=2)

    def lastposition(self):
        self.oscilloscope_widget.setYRange(self.lastshowminy, self.lastshowmaxy, padding=0)  # Y区间
        self.oscilloscope_widget.setXRange(self.lastshowminx, self.lastshowmaxx, padding=0)
        self.pushButton_last_position.setEnabled(False)

    def updateRegion(self, a, lineshow):
        if not self.pushButton_last_position.isEnabled():
            self.pushButton_last_position.setEnabled(True)

        self.lastshowminx = self.showminx
        self.lastshowmaxx = self.showmaxx
        self.lastshowminy = self.showmaxx
        self.lastshowmaxy = self.showmaxy

        self.showminx = self.oscilloscope_widget.viewRect().bottomLeft().x()
        self.showmaxx = self.oscilloscope_widget.viewRect().bottomRight().x()
        self.showminy = self.oscilloscope_widget.viewRect().topRight().y()
        self.showmaxy = self.oscilloscope_widget.viewRect().bottomLeft().y()

        if self.checkBox_shownowview.isChecked():
            self.doubleSpinBox_xmin.setValue(self.showminx)
            self.doubleSpinBox_xmax.setValue(self.showmaxx)
            self.doubleSpinBox_ymin.setValue(self.showminy)
            self.doubleSpinBox_ymax.setValue(self.showmaxy)

        if self.checkBox_kadun.isChecked():
            Limitofnumberofpoints = int(abs(self.showmaxx - self.showminx))
            self.spinBox_kdun.setValue(
                Limitofnumberofpoints if Limitofnumberofpoints < self.spinBox_Peak_points.value() else self.spinBox_Peak_points.value())  # 卡顿动态调节

    def now_local(self, data):
        maxnum = np.max(data, axis=0)
        minnum = np.min(data, axis=0)
        del_lis = []
        for index, val in enumerate(self.cofigmodel.show_flag):
            if not val:
                del_lis.append(index)

        if not del_lis:
            maxnum = np.max(np.delete(maxnum, del_lis))
            minnum = np.min(np.delete(minnum, del_lis))
        else:
            maxnum = np.max(maxnum)
            minnum = np.min(minnum)

        self.oscilloscope_widget.setYRange(minnum, maxnum, padding=0.1)  # Y区间

    def startorstop(self):
        self.isstart = not self.isstart
        if self.isstart:
            self.checkBox_PLotthunrefresh.setEnabled(False)
            self.pushButtonupdata.setText('stop')
            if self.checkBox_PLotthunrefresh.isChecked():
                self.Plotrefreshthund.Plotrunning = True
                self.Plotrefreshthund.start()
            else:
                self.Plotrefreshtime.start(100)
        else:
            self.checkBox_PLotthunrefresh.setEnabled(True)
            self.pushButtonupdata.setText('start')
            if self.checkBox_PLotthunrefresh.isChecked():
                self.Plotrefreshthund.Plotrunning = False
                # self.Plotrefreshthund.terminate()
            else:
                self.Plotrefreshtime.stop()

    def time_resh(self):
        if self.checkBox_time.isChecked():
            # self.oscilloscope_widget.setLimits(maxXRange=6000)
            # self.oscilloscope_widget.enableAutoRange(axis='x', enable=1, x= 6000)
            self.show_all_plot()
            self.spinBox_time_limt.setEnabled(False)
            self.pushButton_refreshview.setEnabled(False)
        else:
            self.oscilloscope_widget.setLimits(maxXRange=10000000000)
            self.pushButton_refreshview.setEnabled(True)
            self.spinBox_time_limt.setEnabled(True)

    def updata(self):
        if self.checkBox_xcircle.isChecked():
            self.data_xcircle = self.data.copy()[1:np.min(self.data_len_array), :]
            self.data_xcircle = self.data_xcircle[::len(self.data_xcircle)//200]
            if self.xtoy:
                self.data_circlex = self.data_xcircle[:,
                                    self.xcircle_X_index] * self.doubleSpinBox_xcircle_coefficient.value() + self.doubleSpinBox_xcircle_intercept.value()
                self.data_circley = self.data_xcircle[:,
                                    self.xcircle_Y_index] * self.doubleSpinBox_xcircle_coefficient_y.value() + self.doubleSpinBox_xcircle_intercept_y.value()
            else:
                self.data_circlex = self.data_xcircle[:,
                                    self.xcircle_Y_index] * self.doubleSpinBox_xcircle_coefficient.value() + self.doubleSpinBox_xcircle_intercept.value()
                self.data_circley = self.data_xcircle[:,
                                    self.xcircle_X_index] * self.doubleSpinBox_xcircle_coefficient_y.value() + self.doubleSpinBox_xcircle_intercept_y.value()

            self.xcircle.setData(x=self.data_circlex, y=self.data_circley)
        elif 1 in self.circlemodel.show_circleflag:
            self.data_xcircle = self.data.copy()[1:np.min(self.data_len_array)-3, :] # -3 摇摆位
            self.data_xcircle = self.data_xcircle[-self.spinBox_xcircle_showpoints.value():,:]
            if self.circlemodel.show_circleflag[0]:
                self.data_circlex = self.data_xcircle[:,
                                    self.circle_x_index] * self.circlemodel._data[0, 4] + self.circlemodel._data[0, 5]
                self.data_circley = self.data_xcircle[:,
                                    self.circle_y_index] * self.doubleSpinBox_xcircle_coefficient_y.value() + self.doubleSpinBox_xcircle_intercept_y.value()
                self.xcircle.setData(x=self.data_circlex, y=self.data_circley)
            if self.circlemodel.show_circleflag[1]:
                self.data_circlex = self.data_xcircle[:,
                                    self.circle_2_x_index] * self.circlemodel._data[1, 4] + self.circlemodel._data[1, 5]
                self.data_circley = self.data_xcircle[:,
                                    self.circle_2_y_index] * self.doubleSpinBox_xcircle_coefficient_y.value() + self.doubleSpinBox_xcircle_intercept_y.value()
                self.xcircle_2.setData(x=self.data_circlex, y=self.data_circley)
        else:

            self.data_for_draw = self.data[
                                 0 if self.showminx < 0 else int(self.showminx):1 if self.showmaxx < 1 else
                                 int(self.showmaxx + 5) if int(self.showmaxx + 5) < np.min(self.data_len_array) else
                                 np.min(self.data_len_array), :].copy()

            '''显示运算'''
            self.data_for_draw = self.showfunc(self.data_for_draw)
            '''偏移运算'''
            self.data_for_draw = self.func_curcer(self.data_for_draw)
            self.line_cursor_local = np.max(self.data_len_array) - 1
            # self.line_cursor.setPos(self.line_cursor_local)
            if self.checkBox_time.isChecked():
                self.oscilloscope_widget.setXRange(self.line_cursor_local - self.spinBox_time_limt.value() // 2,
                                                   self.line_cursor_local + self.spinBox_time_limt.value() // 2)

            else:
                pass
            for i, cursor in enumerate(self.cursor_list):
                if self.cofigmodel.show_flag[i]:
                    cursor.setData(x=self.data_for_draw[:, 8],
                                   y=self.data_for_draw[:, i])

    def showfunc(self, num):
        # print(len(num))

        a = int(abs(self.showminx - self.showmaxx) // self.spinBox_kdun.value())
        # print(len(num[::a + 1]))
        return num[::a + 1]

    def func_curcer(self, data_numpy):
        # 显示区域偏移计算
        for num, val in enumerate(self.cofigmodel.show_flag):
            if val:
                data_numpy[:, num] = data_numpy[:, num] * int(self.cofigmodel._data[num][3]) + int(
                    self.cofigmodel._data[num][4])
        return data_numpy

    def changeView(self):


        self.showminx = self.doubleSpinBox_xmin.value()
        self.showmaxx = self.doubleSpinBox_xmax.value()
        self.showminy = self.doubleSpinBox_ymin.value()
        self.showmaxy = self.doubleSpinBox_ymax.value()
        self.oscilloscope_widget.setXRange(self.showminx, self.showmaxx, padding=0)
        self.oscilloscope_widget.setYRange(self.showminy, self.showmaxy, padding=0)

    '''鼠标位置线'''

    def mouse_line(self):
        self.mouse_line_x = InfiniteLine(angle=90,
                                         movable=False,
                                         pen="#808A87",
                                         label='{value}', )
        self.mouse_line_y = InfiniteLine(angle=0,
                                         movable=False,
                                         pen="#808A87",
                                         label='{value}', )

    '''测距线'''
    def add_xline(self):
        label_dict = {"position": 0.5,
                      "color": "#808A87",
                      "movable": True,
                      "fill": (200, 200, 200, 50)}
        self.line_x1 = InfiniteLine(angle=90,
                                    movable=True,
                                    pen="#808A87",
                                    label='{value}',
                                    labelOpts=label_dict)
        self.line_x2 = InfiniteLine(angle=90,
                                    movable=True,
                                    pen="#808A87",
                                    label='{value}',
                                    labelOpts=label_dict)
        self.line_y1 = InfiniteLine(angle=0,
                                    movable=True,
                                    pen="#808A87",
                                    label='{value}',
                                    labelOpts=label_dict)
        self.line_y2 = InfiniteLine(angle=0,
                                    movable=True,
                                    pen="#808A87",
                                    label='{value}',
                                    labelOpts=label_dict)

        self.line_x1.sigPositionChanged.connect(self.move_line_slot)
        self.line_x2.sigPositionChanged.connect(self.move_line_slot)
        self.line_y1.sigPositionChanged.connect(self.move_line_slot)
        self.line_y2.sigPositionChanged.connect(self.move_line_slot)

    def move_line_slot(self):
        if self.checkBox_xline.isChecked():
            self.lineEdit_x1.setText(str(round(self.line_x1.value(), 3)))
            self.lineEdit_x2.setText(str(round(self.line_x2.value(), 3)))
            self.lineEdit_xline.setText(str(round(abs(self.line_x1.value() - self.line_x2.value()), 3)))

        if self.checkBox_yline.isChecked():
            self.lineEdit_y1.setText(str(round(self.line_y1.value(), 3)))
            self.lineEdit_y2.setText(str(round(self.line_y2.value(), 3)))
            self.lineEdit_yline.setText(str(round(abs(self.line_y1.value() - self.line_y2.value()), 3)))

    def put_Xline(self):
        """放置line"""
        if self.checkBox_xline.isChecked():
            self.line_x1.setPos((self.showmaxx + self.showminx) / 2)
            self.line_x1.setPen(color="#808A87", style=Qt.DashLine)
            self.oscilloscope_widget.addItem(self.line_x1, ignoreBounds=True)

            self.line_x2.setPos((self.showmaxx + self.showminx) / 2)
            self.line_x2.setPen(color="#808A87", style=Qt.DashLine)
            self.oscilloscope_widget.addItem(self.line_x2, ignoreBounds=True)
        else:
            self.line_x1.setValue(0)
            self.oscilloscope_widget.removeItem(self.line_x1)
            self.line_x2.setValue(0)
            self.oscilloscope_widget.removeItem(self.line_x2)

    def put_Yline(self):
        if self.checkBox_yline.isChecked():
            self.line_y1.setPos((self.showmaxy + self.showminy) / 2)
            self.line_y1.setPen(color="#808A87", style=Qt.DashLine)
            self.oscilloscope_widget.addItem(self.line_y1, ignoreBounds=True)

            self.line_y2.setPos((self.showmaxy + self.showminy) / 2)
            self.line_y2.setPen(color="#808A87", style=Qt.DashLine)
            self.oscilloscope_widget.addItem(self.line_y2, ignoreBounds=True)
        else:
            self.line_y1.setValue(0)
            self.oscilloscope_widget.removeItem(self.line_y1)
            self.line_y2.setValue(0)
            self.oscilloscope_widget.removeItem(self.line_y2)


class collectthread(QThread):
    def __init__(self, parent=None):
        super(collectthread, self).__init__(parent)

        self.runningflag = True

    def run(self):
        while self.runningflag:
            break_flag = False
            for j in range(100000000000000000000000000):
                for i, val in enumerate(self.parent().cofigmodel.show_flag):
                    if cncAPI.oscilloscopePeek(i):
                        self.parent().data[self.parent().data_len_array[i], i] = cncAPI.oscilloscopeRead(i)
                        self.parent().data_len_array[i] = self.parent().data_len_array[i] + 1
                        if np.max(self.parent().data_len_array) >1999999:
                            self.parent().dataclear()
                    else:
                        if self.parent().data_len_array[i] == np.min(self.parent().data_len_array):
                            break_flag = True
                            break
                if break_flag:
                    break_flag = False
                    break
            QThread.msleep(10)


class Plotrefreshthread(QThread):
    def __init__(self, parent=None):
        super(Plotrefreshthread, self).__init__(parent)
        self.Plotrunning = True

    def run(self):
        while self.Plotrunning:
            self.parent().plotrefresh.emit(True)
            QThread.msleep(100)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Diag_oscillograph_new()

    w.show()
    sys.exit(app.exec_())