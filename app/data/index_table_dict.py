# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
from datetime import datetime

import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import app
from app.colors import Colors
from app.init import val
import time
import numpy as np
import pandas as pd


class IndexDictView(QtWidgets.QTableView):
    """View to display historical price data."""

    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)

        self.my_model = IndexDictModel(self)
        self.mw = app.mw


        self.setMouseTracking(True)
        self.setSortingEnabled(True)
        self.proxy_model = QtCore.QSortFilterProxyModel()
        # self.setItemDelegate(HistoricDelegate(self))
        # self.setup()
        # self.clicked.connect(self.cell_clicked)


    def get_values(self):
        list_data = list()
        for coin in val["tickers"].items():
            row = list()
            for value in coin[1].items():
                row.append(value[1])
            list_data.append(row)
        return list_data

    def setup(self):
        """Setup the view."""



        self.update_model_data()


        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.my_model)

        self.setModel(self.proxy_model)

        # self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        # self.verticalHeader().setDefaultSectionSize(15)

        # self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        # self.horizontalHeader().setDefaultSectionSize(75)
        self.emitChange()
        self.mw.dict_update = True


    def emitChange(self):
        """Make QT redraw the table once it's model has changed."""
        # there might be a less expensive way
        self.my_model.modelReset.emit()


    def update_model_data(self):
        self.proxy_model.layoutAboutToBeChanged.emit()
        start_time = time.time()

        self.list_data = self.get_values()
        
        self.my_model.update(self.list_data)
        stop_time = time.time()
        time_delta = stop_time - start_time
        print(time_delta)
        self.proxy_model.layoutChanged.emit()
        

class IndexDictModel(QtCore.QAbstractTableModel):
    """Model containing global trade history values."""

    def __init__(self, parent=None, *args):
        super(IndexDictModel, self).__init__()
        self.headers = ["coin", "price", "volume", "asd", "def"]
        self.mw = app.mw
        self.model_data = None
        # self.blockSignals(True)


    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Set header data."""
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.headers[section]

    def columnCount(self, parent=None):
        """Return model column count."""
        return len(self.headers)

    def rowCount(self, parent):
        """Return model row count."""
        try:
            return len(self.model_data)
        except TypeError:
            return 0

    def update(self, new_data):
        """Update model data. Does not create a copy."""
        print("update")

        # self.layoutAboutToBeChanged.emit()
        self.model_data = new_data
        # self.layoutChanged.emit()

    def data(self, index, role):
        """Return model data by index."""
        if role == QtCore.Qt.DisplayRole:
            if index.isValid():
            # if index.column() == 0:
                
                # print("update", index.row(), index.column())
                # self.dataChanged.emit(index.row(), index.column())
                # self.layoutChanged.emit()
                return str(self.model_data[index.row()][index.column()])

            # except Exception as e:
            #     print("error", e)
            #     return QtCore.QVariant()
            # else:
                # formatted = '{number:.{digits}f}'.format(number=float(self.model_data[index.row()][index.column()]), digits=8)
                # return QtCore.QVariant(formatted)
    
            # print("CELL VALUE: ", self.model_data[index.row()][index.column()])
            # return(QtCore.QVariant(self.model_data[index.row()][index.column()]))
        else:
            # print("else")
            return QtCore.QVariant()