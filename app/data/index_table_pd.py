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


class IndexPdView(QtWidgets.QTableView):
    """View to display historical price data."""

    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)

        self.my_model = IndexPdModel(self)
        self.mw = app.mw


        self.setMouseTracking(True)
        self.setSortingEnabled(True)
        self.proxy_model = QtCore.QSortFilterProxyModel()
        # self.setItemDelegate(HistoricDelegate(self))
        # self.setup()
        # self.clicked.connect(self.cell_clicked)


    def get_values(self):
        return pd.DataFrame(val["tickers"]).transpose()[["symbol", "lastPrice", "priceChangePercent", "quoteVolume"]]

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
        self.mw.pd_update = True


    def emitChange(self):
        """Make QT redraw the table once it's model has changed."""
        # there might be a less expensive way
        self.proxy_model.modelReset.emit()


    def update_model_data(self):
        self.my_model.layoutAboutToBeChanged.emit()

        # self.proxy_model.modelAboutToBeReset.emit()

        self.my_model.update(self.get_values())

        # self.my_model.sort(self.my_model.order_col, self.my_model.order_dir)
        self.my_model.layoutChanged.emit()
        # self.proxy_model.modelReset.emit()


class IndexPdModel(QtCore.QAbstractTableModel):
    """Model containing global trade history values."""

    def __init__(self, parent=None, *args):
        super(IndexPdModel, self).__init__()
        self.headers = ["coin", "price", "volume", "asd", "def"]
        self.mw = app.mw
        self.model_data = None

        self.order_col = 0
        self.order_dir = True
        # self.blockSignals(True)


    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Set header data."""
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                # return self.headers[section]
                return self.model_data.columns[section]


    def columnCount(self, parent=None):
        """Return model column count."""
        return len(self.model_data.columns.values)

    def rowCount(self, parent):
        """Return model row count."""
        return len(self.model_data.index)


    def update(self, new_data):
        """Update model data. Does not create a copy."""
        self.model_data = new_data

    def data(self, index, role):
        """Return model data by index."""
        if role == QtCore.Qt.DisplayRole:
            if index.isValid():
                if index.column() < 1:
                    return str(self.model_data.iloc[index.row(), index.column()])
                else:
                    return float(self.model_data.iloc[index.row(), index.column()])


    def sort(self, Ncol=0, order=True):
        """Sort table by given column number."""
        self.modelAboutToBeReset.emit()
        if Ncol > 0:
            try:
                self.model_data = self.model_data.sort_values(self.model_data.columns[Ncol], ascending=not order)
            except TypeError as e:
                print("Sort error: " + str(e) + " " + str(Ncol))        

            # jirrik: save order dir, order col
            self.order_col = Ncol
            self.order_dir = order


            # self.setFilter(searchText=self.searchText)
            self.modelAboutToBeReset.emit()
            # self.layoutChanged.emit()
        self.modelReset.emit()
