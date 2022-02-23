# -*- coding: utf-8 -*-
"""
@Time ： 2022/1/11 14:28
@Auth ： 吕伟康
@File ：Diag_oscillgraph_lineconfig.py
"""
# -*- coding: utf-8 -*-
"""
@Time ： 2021/8/19 16:17
@Auth ： 吕伟康
@File ：Diag_oscillgraph_lineconfig.py
"""
import numpy as np
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import *
# 翻译
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QColor, QStandardItemModel, QPixmap, QIcon



_translate = QtCore.QCoreApplication.translate


class ConfigTableModel(QtCore.QAbstractTableModel):

    def __init__(self, parent=None):
        super(ConfigTableModel, self).__init__(parent)
        self._data = np.zeros(shape=(8, 7))
        self._data[:, 3] = 1

        self.headers = ['TRUE', 'Source', 'Color', 'Zoom ', 'offset', 'Current X', 'Current Y']
        self.show_flag = np.zeros(shape=(8))
        self.show_flag[0] = 1
        self.colors = ["#FF0000", "#FAA460", "#FFFF00", "#008000", "#C0C0C0", "#0000FF", "#9400D3", "#000000"]
    def modelReset(self):
        self.beginResetModel()
        self.endResetModel()

    def rowCount(self, parent) -> int:
        '''设置行数'''
        return 8

    def columnCount(self, parent) -> int:
        '''设置列数'''
        return len(self.headers)

    def headerData(self, section: int, orientation, role: int = ...):
        '''设置表头'''
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.headers[section]
            else:
                return super().headerData(section, orientation, role)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        '''编辑表格内容是限制 编辑容'''

        if index.column() == 0:
            self.show_flag[index.row()] = 0 if self.show_flag[index.row()] else 1
            self.parent().changeshowcusor(index.row(), self.show_flag[index.row()])
            return True
        if index.column() == 2:
            self.colors[index.row()] = value
            self.parent().changecolor(index.row(), value)
            return True
        if index.column() in [3, 4]:
            self._data[index.row()][index.column()] = value
            return True

    def data(self, index, role: int = ...):
        '''显示数据 color zoom offset 不显示'''
        if role == Qt.DisplayRole:
            if index.column() not in [0, 1, 2]:
                return str(self._data[index.row()][index.column()])

            if index.column() == 1:
                return self.parent().cursor_list[index.row()].title

        if role == Qt.CheckStateRole and index.column() == 0:
            return Qt.Checked if self.show_flag[index.row()] else Qt.Unchecked
        if role == Qt.BackgroundColorRole and index.column() == 2:
            return QColor(self.colors[index.row()])
        if role == Qt.EditRole and index.column() in [3, 4]:
            return index.data(Qt.DisplayRole)

        #     print(index.data())
        #     return QColor(self.col)

    def flags(self, index):
        ''' 第一列 和最后X y 无法修改'''
        # if index.column() == 0:
        #     return super().flags(index)
        if index.column() in [0,5,6]:
            return super().flags(index) | Qt.ItemIsUserCheckable
        return super().flags(index) | Qt.ItemIsEditable


class ConfigTableDelegate(QtWidgets.QItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)

    # def paint(self, painter, option, index) -> None:
    # if option.state & QtWidgets.QStyle.State_HasFocus:
    #     option.state = option.state ^ QtWidgets.QStyle.State_HasFocus
    # super().paint(painter, option, index)

    def createEditor(self, parent, option, index: QtCore.QModelIndex):
        '''设置表格控件'''
        # if index.column() == 0:
        #     checkbox = QtWidgets.QCheckBox(parent)
        #     return None
        if index.column() in [3, 4]:
            return self.Doublespinbox_set(parent)
        if index.column() == 2:
            return self.ComboBox_set(parent)
        return super(ConfigTableDelegate, self).createEditor(parent, option, index)

    def Doublespinbox_set(self, parent):
        '''设置 zoom offset 控件'''
        Doublespinbox = QtWidgets.QDoubleSpinBox(parent)
        return Doublespinbox

    def ComboBox_set(self, parent):
        '''设置 颜色选择下拉框'''
        ComboBox = QtWidgets.QComboBox(parent)
        ComboBox.setStyleSheet("color:#f5f5f5")
        ComboBox.setModel(Combox())
        return ComboBox


class Combox(QAbstractItemModel):

    def __init__(self):
        super(Combox, self).__init__()
        # 颜色字典与前面表格 统一
        colors = ["#FF0000", "#FAA460", "#FFFF00", "#008000", "#C0C0C0", "#0000FF", "#9400D3", "#000000"]
        colorsname = [_translate("OscillConfigTable", "Red"),
                      _translate("OscillConfigTable", "Orange"),
                      _translate("OscillConfigTable", "Yellow"),
                      _translate("OscillConfigTable", "Green"),
                      _translate("OscillConfigTable", "Gray"),
                      _translate("OscillConfigTable", "Blue"),
                      _translate("OscillConfigTable", "Purple"),
                      _translate("OscillConfigTable", "Black")]
        self.col = dict(zip(colorsname, colors))
        self._data = colorsname

    def data(self, index: QModelIndex, role=None):  # real signature unknown; restored from __doc__
        """ data(self, QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any """
        '''显示颜色及背景颜色'''

        if index.column() == 0 and role == Qt.BackgroundRole:
            return QColor(self.col[self._data[index.row()]])
        if index.column() == 0 and role == QtCore.Qt.DisplayRole:
            return self._data[index.row()]

    def rowCount(self, parent) -> int:
        '''设置行数'''
        return len(self._data)

    def columnCount(self, parent) -> int:
        '''设置列数'''
        return 1

    def index(self, row, column, parentIndex):
        if not self.hasIndex(row, column, parentIndex):
            return QModelIndex()
        else:
            return self.createIndex(row, column)

    def parent(self, index: QModelIndex = None):
        return QModelIndex()
