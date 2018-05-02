# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
# import PyQt5.QtGui as QtGui
import pandas as pd
# import re

from app.table_items import CoinDelegate
# from app.workers import Worker
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
        # self.threadpool = app.threadpool

        self.name = "TestTableView"
        self.setItemDelegate(CoinDelegate(self))
        self.setMouseTracking(True)


    def setup(self):

        # self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setDefaultSectionSize(50)
        # self.horizontalHeader().resizeSection(0, 35)
        # self.horizontalHeader().resizeSection(1, 135)
        # self.horizontalHeader().resizeSection(2, 35)
        

        dataFrame = self.get_coin_frame()

        self.my_model.update(dataFrame)

        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.my_model)
        self.proxy_model.setDynamicSortFilter(False)
        self.proxy_model.setFilterCaseSensitivity(False)
        self.proxy_model.setSortLocaleAware(True)
        self.proxy_model.setRecursiveFilteringEnabled(False)


        self.setModel(self.my_model)
        self.setSortingEnabled(True)
        # self.my_model.sort(0, 0)
        self.mw.new_coin_table = True
        # btn = QtWidgets.QPushButton("TEST")

        # self.setIndexWidget(self.my_model.index(0, 4), btn)
        # self.my_model.sort(0, 1)
        self.setColumnWidth(0, 30)
        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 100)

    def leaveEvent(self, event):
        app.main_app.restoreOverrideCursor()

    def get_coin_frame(self):
        all_coins = dict()
        for pair in val["tickers"]:
            if "USDT" not in pair:
                coin = str(val["tickers"][pair]["symbol"]).replace("BTC", "")
                last_price = val["tickers"][pair]["lastPrice"]
                pric_per = float(val["tickers"][pair]["priceChangePercent"])
                vol = float(val["tickers"][pair]["quoteVolume"])

                # btn = QtWidgets.QPushButton("Trade " + str(coin))
                # btn = "BTN"

                all_coins[coin] = [coin, coin, last_price, float(pric_per), vol, coin]


        df = pd.DataFrame(all_coins).transpose()
        # df = pd.DataFrame(val["tickers"]).transpose()[["symbol", "lastPrice"]]
        return df

    def coin_update(self):
        
        dataFrame = self.get_coin_frame()


        # dataFrame = self.get_coin_frame()

        # self.my_model.layoutAboutToBeChanged.emit()

        self.my_model.datatable = dataFrame


        # if self.my_model.order_col != 0 or self.my_model.order_dir != 0:
        self.my_model.sort(self.my_model.order_col, self.my_model.order_dir)

        # self.my_model.layoutChanged.emit()
        # self.my_model.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
        




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

    def search_edited(self, searchText=None):
        self.my_model.setFilter(searchText=searchText)


class MyTableModel(QtCore.QAbstractTableModel):
    header_labels = ['Icon', 'Pair', 'Price', '24h Change', "24h volume", "1m volume", "5m volume", "15m volume", "1h volume", "5m change", "15m change", "1h change"]

    def __init__(self, parent=None, *args):
        super(MyTableModel, self).__init__()
        self.mw = app.mw
        self.datatable = None
        self.setHeaderData
        self._sortBy = []
        self._sortDirection = []
        self._filters = {}
        # self.totRows = len(self.datatable)

        self.order_col = 0
        self.order_dir = 0

        self.initially_sorted = False
        self.searchText = None

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        # print("headerData")
        try:
            if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
                return self.header_labels[section]
                # return self.datatable.columns.values[section]


            elif role == QtCore.Qt.InitialSortOrderRole:
                # set initial sort order of specific columns (sections)
                if section > 0:
                    return QtCore.QVariant(QtCore.Qt.DescendingOrder)
                else:
                    return QtCore.QVariant(QtCore.Qt.AscendingOrder)

            return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)
        except Exception as e:
            print("HEADER DATA: " + str(e))


    def update(self, dataIn):
        # print('Updating Model')
        self.datatable = dataIn
        # print('Datatable : {0}'.format(self.datatable))


    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.columns.values)

    def data(self, index, role):
        # print 'Data Call'
        if role == QtCore.Qt.DisplayRole:

            i = index.row()
            j = index.column()
            if j < 2 or j > 4:
                return QtCore.QVariant(str(self.datatable.iloc[i, j]))
            else:
                return QtCore.QVariant(float(self.datatable.iloc[i, j]))
                
        else:
            return QtCore.QVariant()

    def insertRows(self, row, item, column=1, index=QtCore.QModelIndex()):
        self.beginInsertRows(QtCore.QModelIndex(), row, row + 1)
        self.datatable.append(item)
        self.endInsertRows()


    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled




        # self.current_items = [item for item in self.datatable.index if searchText in item]

        # self.datatable = self.current_items

        

        self.layoutChanged.emit()


    def setFilter(self, searchText=None):
        print("Set filter")
        if searchText:
            for row in range(self.rowCount()):
                print("filter" + str(row))
                self.mw.test_table_view.setRowHidden(row, False)
                if str(searchText.upper()) in str(self.datatable.iloc[row, 0]):
                    self.mw.test_table_view.setRowHidden(row, False)
                else:
                    self.mw.test_table_view.setRowHidden(row, True)
                    print("hide: " + str(searchText) + " and " + str(self.datatable.iloc[row, 0]))
            
        else:
            for row in range(self.rowCount()):
                self.mw.test_table_view.setRowHidden(row, False)

        self.searchText = searchText



    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        # try:
        print("sort: " + str(Ncol) + " " + str(order))
        self.modelAboutToBeReset.emit()
        if Ncol > 0:
            # self.setFilter(searchText="")

            # self.layoutAboutToBeChanged.emit()
            
            try:
                self.datatable = self.datatable.sort_values(self.datatable.columns[Ncol], ascending=not order)
            except TypeError as e:
                print("Sort error: " + str(e) + " " + str(Ncol))        

            # jirrik: save order dir, order col
            self.order_col = Ncol
            self.order_dir = order


            self.setFilter(searchText=self.searchText)

            # self.layoutChanged.emit()
        self.modelReset.emit()
        # except Exception as e:
        #     print(e)

    # def getRows(self, regexp):
    #     out = []
    #     col = self.datatable.columns.get_loc(0)
    #     for row in range(self.rowCount()):
    #         check = self.data(self.index(row, col))
    #         match = re.match(regexp, check)
    #         if match:
    #             out.append(row)
    #     return out

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
