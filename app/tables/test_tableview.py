# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import pandas as pd


class TestTableView(QtWidgets.QTableView):
    """
    A simple table to demonstrate the QComboBox delegate.
    """
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.my_model = MyTableModel(self)

    def setup(self):

        dataFrame = self.get_data_frame()

        self.my_model.update(dataFrame)


        self.my_model.setHeaderData(0, QtCore.Qt.Horizontal, "Hallo test")
        self.my_model.setHeaderData(1, QtCore.Qt.Horizontal, "Nummer 2")
        # self.my_model.headerDataChanged()
        self.setModel(self.my_model)
        self.setSortingEnabled(True)


    def get_data_frame(self):
        df = pd.DataFrame({'Name': ['a', 'b', 'c', 'd'],
                           'First': [2.3, 5.4, 3.1, 7.7],
                           'Last': [23.4, 11.2, 65.3, 88.8],
                           'Class': [1, 1, 2, 1],
                           'Valid': [True, True, True, False]})
        return df


    def append_row(self):
        self.beginInsertRows()
        self.beginInsertColumns()

        self.my_model.datatable.append([1, 2, 3, 4])

        self.endInsertRows()
        self.endInsertColumns()
        # self.my_model.dataChanged()


class MyTableModel(QtCore.QAbstractTableModel):
    header_labels = ['Column 1', 'Column 2', 'Column 3', 'Column 4', "Col 5"]

    def __init__(self, parent=None, *args):
        super(MyTableModel, self).__init__()
        self.datatable = None
        self.setHeaderData
        self._sortBy = []
        self._sortDirection = []
        self._filters = {}


    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        try:
            if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
                # return self.header_labels[section]
                return self.datatable.columns.values[section]
            return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)
        except Exception as e:
            print(str(e))


    def update(self, dataIn):
        print('Updating Model')
        self.datatable = dataIn
        print('Datatable : {0}'.format(self.datatable))


    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.columns.values)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        # print 'Data Call'
        # print index.column(), index.row()
        if role == QtCore.Qt.DisplayRole:
            i = index.row()
            j = index.column()
            return QtCore.QVariant(str(self.datatable.iloc[i, j]))
            # return '{0}'.format(self.datatable.iloc[i, j])
        else:
            return QtCore.QVariant()

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled


    def sort(self, col, order=QtCore.Qt.AscendingOrder):

        # Storing persistent indexes
        self.layoutAboutToBeChanged.emit()
        oldIndexList = self.persistentIndexList()
        oldIds = self.datatable.index.copy()

        # Sorting data
        column = self.datatable.columns[col]
        ascending = (order == QtCore.Qt.AscendingOrder)
        if column in self._sortBy:
            i = self._sortBy.index(column)
            self._sortBy.pop(i)
            self._sortDirection.pop(i)
        self._sortBy.insert(0, column)
        self._sortDirection.insert(0, ascending)
        self.updateDisplay()

        # Updating persistent indexes
        newIds = self.datatable.index
        newIndexList = []
        for index in oldIndexList:
            id = oldIds[index.row()]
            newRow = newIds.get_loc(id)
            newIndexList.append(self.index(newRow, index.column(), index.parent()))
        self.changePersistentIndexList(oldIndexList, newIndexList)
        self.layoutChanged.emit()
        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

    def updateDisplay(self):

        dfDisplay = self.datatable

        # Filtering
        cond = pd.Series(True, index=dfDisplay.index)
        for column, value in self._filters.items():
            cond = cond & \
                (dfDisplay[column].str.lower().str.find(str(value).lower()) >= 0)
        dfDisplay = dfDisplay[cond]

        # Sorting
        if len(self._sortBy) != 0:
            dfDisplay.sort_values(by=self._sortBy,
                                    ascending=self._sortDirection,
                                    inplace=True)

        # Updating
        self.datatable = dfDisplay