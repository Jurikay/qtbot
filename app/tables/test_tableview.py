# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import pandas as pd

from app.table_items import CoinDelegate
from app.workers import Worker
from app.init import val
import app

class TestTableView(QtWidgets.QTableView):
    """
    A simple table to demonstrate the QComboBox delegate.
    """
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.my_model = MyTableModel(self)
        self.mw = app.mw
        self.threadpool = app.threadpool

        self.name = "TestTableView"
        self.setItemDelegate(CoinDelegate(self))


    def setup(self):

        # self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setDefaultSectionSize(50)
        self.horizontalHeader().resizeSection(0, 35)
        self.horizontalHeader().resizeSection(1, 135)
        self.horizontalHeader().resizeSection(2, 35)

        dataFrame = self.get_coin_frame()

        self.my_model.update(dataFrame)

        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.my_model)

        self.setModel(self.my_model)
        self.setSortingEnabled(True)
        # self.my_model.sort(0, 0)
        self.mw.new_coin_table = True
        # btn = QtWidgets.QPushButton("TEST")

        # self.setIndexWidget(self.my_model.index(0, 4), btn)
        # self.my_model.sort(0, 1)

    def get_coin_frame(self):
        all_coins = dict()
        for pair in val["tickers"]:
            if "USDT" not in pair:
                coin = str(val["tickers"][pair]["symbol"]).replace("BTC", "")
                last_price = val["tickers"][pair]["lastPrice"]
                pric_per = float(val["tickers"][pair]["priceChangePercent"])
                vol = (val["tickers"][pair]["quoteVolume"])

                # btn = QtWidgets.QPushButton("Trade " + str(coin))
                btn = "BTN"

                all_coins[coin] = [coin, last_price, pric_per, vol, btn]


        df = pd.DataFrame(all_coins).transpose()
        # df = pd.DataFrame(val["tickers"]).transpose()[["symbol", "lastPrice"]]
        return df

    def coin_update(self):
        
        dataFrame = self.get_coin_frame()


        # dataFrame = self.get_coin_frame()

        self.my_model.layoutAboutToBeChanged.emit()

        self.my_model.datatable = (dataFrame)


        if self.my_model.order_col != 0 or self.my_model.order_dir != 0:
            # print(str(self.my_model.order_col))
            # print(str(self.my_model.order_dir))
            self.my_model.sort(self.my_model.order_col, self.my_model.order_dir)

        
        # self.my_model.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
        self.my_model.layoutChanged.emit()




    def get_data_frame(self):

        df = pd.DataFrame({'Name': ['a', 'b', 'c', 'd'],
                           'First': [2.3, 5.4, 3.1, 7.7],
                           'Last': [23.4, 11.2, 65.3, 88.8],
                           'Class': [1, 1, 2, 1],
                           'Valid': [True, True, True, False]})
        return df


    def append_row(self):
        # self.beginInsertRows()
        # self.beginInsertColumns()

        self.my_model.datatable.append([1, 2, 3, 4])

        # self.endInsertRows()
        # self.endInsertColumns()
        self.my_model.layoutChanged.emit()


class MyTableModel(QtCore.QAbstractTableModel):
    header_labels = ['Column 1', 'Column 2', 'Column 3', 'Column 4', "Col 5"]

    def __init__(self, parent=None, *args):
        super(MyTableModel, self).__init__()
        self.datatable = None
        self.setHeaderData
        self._sortBy = []
        self._sortDirection = []
        self._filters = {}

        self.order_col = 0
        self.order_dir = 0

        self.initially_sorted = False

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        # print("headerData")
        try:
            if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
                # return self.header_labels[section]
                return self.datatable.columns.values[section]


            elif role == QtCore.Qt.InitialSortOrderRole:
                # set initial sort order of specific columns (sections)
                if section > 0:
                    return QtCore.QVariant(QtCore.Qt.DescendingOrder)
                else:
                    return QtCore.QVariant(QtCore.Qt.AscendingOrder)

            return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)
        except Exception as e:
            print(str(e))


    def update(self, dataIn):
        # print('Updating Model')
        self.datatable = dataIn
        # print('Datatable : {0}'.format(self.datatable))


    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.columns.values)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        # print 'Data Call'
        # print index.column(), index.row()
        i = index.row()
        j = index.column()
        if role == QtCore.Qt.DisplayRole:
            
            if j > 0:
                return QtCore.QVariant(self.datatable.iloc[i, j])
            else:
                return QtCore.QVariant(str(self.datatable.iloc[i, j]))
            # return '{0}'.format(self.datatable.iloc[i, j])
        elif role == QtCore.Qt.InitialSortOrderRole:
            # print("SORT ORDER CHECK")
            return QtCore.QVariant(QtCore.Qt.AscendingOrder)

        else:
            return QtCore.QVariant()

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled


    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        try:
            # print("sort: " + str(Ncol) + " " + str(order))
            self.layoutAboutToBeChanged.emit()
            self.datatable = self.datatable.sort_values(self.datatable.columns[Ncol], ascending=not order)
            self.layoutChanged.emit()

            # jirrik: save order dir, order col
            self.order_col = Ncol
            self.order_dir = order
        except Exception as e:
            print(e)

    # def updateDisplay(self):

    #     dfDisplay = self.datatable

    #     # Filtering
    #     cond = pd.Series(True, index=dfDisplay.index)
    #     for column, value in self._filters.items():
    #         cond = cond & \
    #             (dfDisplay[column].str.lower().str.find(str(value).lower()) >= 0)
    #     dfDisplay = dfDisplay[cond]

    #     # Sorting
    #     if len(self._sortBy) != 0:
    #         dfDisplay.sort_values(by=self._sortBy,
    #                               ascending=self._sortDirection,
    #                               inplace=True)

    #     # Updating
    #     self.datatable = dfDisplay

    # def appendR(self):
    #     print("add")
    #     self.layoutAboutToBeChanged.emit()
    #     newdf = pd.DataFrame({'Name': ['a', 'b', 'c', 'd'],
    #                        'First': [2.3, 5.4, 0.1, 1117.7],
    #                        'Last': [23.4, 0.12, 0.00003, 88.8],
    #                        'Class': [1, 5, 2, 1],
    #                        'Valid': [False, True, True, False]})
    #     # self.updateDisplay()
    #     self.update(newdf)

    #     self.layoutChanged.emit()
    #     self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

    # def real_append(self):
    #     self.layoutAboutToBeChanged.emit()
    #     df = self.datatable
    #     new_df = pd.DataFrame({'Lul': [False, True, True, False]})
    #     df.concat(new_df)
    #     self.update(new_df)

    #     self.layoutChanged.emit()
    #     self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

    def new_append(self):
        self.layoutAboutToBeChanged.emit()

        self.insertRow(0)
        # self.item(0, 0).setText("new insert")

        self.layoutChanged.emit()
