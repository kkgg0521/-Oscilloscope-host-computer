# -*- coding: utf-8 -*-
"""
@Time ： 2022/1/11 14:28
@Auth ： 吕伟康
@File ：Diag_oscillgraph_circleconfig.py
"""

import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QAbstractItemModel, QModelIndex
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class CircleConfigTableModel(QtCore.QAbstractTableModel):

    def __init__(self, parent=None):
        super(CircleConfigTableModel, self).__init__(parent)
        self.headers = ['组别', 'X', 'Y', '颜色', 'Zoom ', 'offset', 'Current X', 'Current Y']
        self.colors = ["#FF0000", "#FAA460", "#FFFF00", "#008000", "#C0C0C0", "#0000FF", "#9400D3", "#000000"]
        self._data = np.zeros(shape=(2, 8))
        self._data[:, 4] = 1
        self.show_circleflag = [0, 0]
        self.circlr_line_name = ['', '']
        self.circlr_line_name_2 = ['', '']

    def modelReset(self):
        self.beginResetModel()
        self.endResetModel()

    def rowCount(self, parent) -> int:
        '''设置行数'''
        return 2

    def columnCount(self, parent) -> int:
        '''设置列数'''
        return 8

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
            if index.row() == 0:
                if self.circlr_line_name[0] == '' or self.circlr_line_name[1]=='':
                    return False
            else:
                if self.circlr_line_name_2[0] == '' or self.circlr_line_name_2[1] == '':
                    return False
            self.show_circleflag[index.row()] = 0 if self.show_circleflag[index.row()] else 1
            self.parent().Xcircle_start(self.show_circleflag)
            return True
        if index.column() in [1, 2]:
            if index.row() == 0:
                self.circlr_line_name[index.column() - 1] = value
                return True
            else:
                self.circlr_line_name_2[index.column() - 1] = value
                return True
        if index.column() == 3:
            self.colors[index.row()] = value
            # self.parent().changecolor(index.row(), value)
            return True
        if index.column() in [4, 5]:
            self._data[index.row()][index.column()] = value
            return True
        pass

    def data(self, index, role: int = ...):
        '''显示数据 color zoom offset 不显示'''
        if role == Qt.BackgroundColorRole and index.column() == 3:
            return QColor(self.colors[index.row()])
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return '{}'.format(['第一组', '第二组'][index.row()])
            if index.column() in [1, 2] :
                if index.row() == 0:
                    return self.circlr_line_name[index.column() - 1]
                else:
                    return self.circlr_line_name_2[index.column() - 1]
            if index.column() not in [0, 1, 2, 3]:
                return str(self._data[index.row()][index.column()])

        if role == Qt.EditRole and index.column() in [4, 5]:
            return index.data(Qt.DisplayRole)

        if role == Qt.CheckStateRole and index.column() == 0:
            return Qt.Checked if self.show_circleflag[index.row()] else Qt.Unchecked

    def flags(self, index):
        ''' 第一列 和最后X y 无法修改'''
        # if index.column() == 0:
        #     return super().flags(index)
        if index.column() in [0]:
            return super().flags(index) | Qt.ItemIsUserCheckable
        return super().flags(index) | Qt.ItemIsEditable


class CircleConfigTableDelegate(QtWidgets.QItemDelegate):

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
        if index.column() in [4, 5]:
            return self.Doublespinbox_set(parent)
        if index.column() == 3:
            return self.ComboBox_set(parent)
        if index.column() in [1, 2]:
            ComboBox = QtWidgets.QComboBox(parent)
            for i in self.parent().cursor_list:
                ComboBox.addItem(i.title)
            return ComboBox
        return super(CircleConfigTableDelegate, self).createEditor(parent, option, index)

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
        colorsname = ["Red",
                      "Orange",
                      "Yellow",
                      "Green",
                      "Gray",
                      "Blue",
                      "Purple",
                      "Black"]
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
