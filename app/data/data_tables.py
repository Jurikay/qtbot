# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import app
import pandas as pd


class DataOpenOrders(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.my_model = OpenOrdersModel(self)
        self.data_dict = None
        self.df = None
        self.mw = app.mw

    def setup(self):
        print("DATA OPEN ORDER SETUP")

        self.update()
        self.setSortingEnabled(True)
        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.my_model)

        self.setModel(self.proxy_model)
        
    def update(self):
        self.my_model.modelAboutToBeReset.emit()
        self.data_dict = self.mw.user_data.open_orders
        df = pd.DataFrame.from_dict(self.data_dict, orient='index')
        self.df = df[["time", "symbol", "type", "side", "price", "origQty", "executedQty"]]
        self.my_model.update(self.df)
        self.my_model.modelReset.emit()

class OpenOrdersModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None, *args):
        super(OpenOrdersModel, self).__init__()
        self.mw = app.mw
        self.datatable = None

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Set header data."""
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                # return self.headers[section]
                return self.datatable.columns[section]


    def update(self, dataIn):
        self.datatable = dataIn


    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.index)


    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.columns.values)


    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            if index.isValid():
                return str(self.datatable.iloc[index.row(), index.column()])