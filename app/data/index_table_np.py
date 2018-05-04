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

import numpy as np
import pandas as pd

class HistoricArray():
    """Class that holds a 2d-array containing ticker data."""
    def __init__(self):

        self.mw = app.mw
        dtypes = [("second", "U10")]


        dtypes.append(("coin", "U10"))
        for i in range(19):
            
            dtypes.append(("col " + str(i + 1), "f8"))

        historic_array = np.empty((124), dtype=dtypes)
        # print(historic_array["coin"][0])
        
        # Build a numpy array from the tickers dict
        # tickers = self.getTickers()
        ticker_data = self.getTickers()


        for i, tick in enumerate(ticker_data):
            print("i", i)
            print("tick", tick)
            # print("#####")
            # print(historic_array[i]["title"])
            for j in enumerate(tick):
                print("J", j[0])
                try:
                    historic_array[i][j] = j[1][1]
                except Exception as e:
                    print(e)


        self.array = historic_array
        print(self.array)
        print("ARRAY:!!")
        # print(self.array["coin"])
        # print(historic_array)
        # print(historic_array["coin"][0])

        # print("SHAPE")
        # print(len(historic_array))
        # print(historic_array.shape)
        # print(np.shape(historic_array))

        # print(len(historic_array[0]))


    def get_values(self):
        list_data = list()
        for coin in val["tickers"].items():
            row = list()
            for value in coin[1].items():
                row.append(value[1])
            list_data.append(row)
        return list_data

    def getTickers(self):
        """Make an initial API call to get ticker data."""
        # self.client = self.mw.api_manager.client
        # print(val["tickers"])
        ticker = self.get_values()
        # print(str(ticker))
        all_tickers = list()
        btc_pairs = 0
        for ticker_data in ticker:
            if "BTC" in ticker_data[0]:
                btc_pairs += 1
            #     # print(str(ticker_data))
                all_tickers.append(ticker_data)
                # print(str(ticker_data))

        return all_tickers






class IndexView(QtWidgets.QTableView):
    """View to display historical price data."""

    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)

        self.my_model = IndexModel(self)
        self.mw = app.mw


        self.setMouseTracking(True)
        self.setSortingEnabled(True)
        self.setItemDelegate(HistoricDelegate(self))
        # self.setup()
        # self.clicked.connect(self.cell_clicked)



    def setup(self):
        """Setup the view."""
        self.np_array = HistoricArray()
        self.array_data = self.np_array.array
        self.my_model.update(self.array_data)


        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.my_model)

        self.setModel(self.proxy_model)

        self.mw.np_update = True
        # self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        # self.verticalHeader().setDefaultSectionSize(15)

        # self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        # self.horizontalHeader().setDefaultSectionSize(75)
        self.emitChange()

    def emitChange(self):
        """Make QT redraw the table once it's model has changed."""
        # there might be a less expensive way
        self.my_model.modelReset.emit()


    def update_model_data(self):
        self.my_model.update(self.array_data)     


class IndexModel(QtCore.QAbstractTableModel):
    """Model containing global trade history values."""

    def __init__(self, parent=None, *args):
        super(IndexModel, self).__init__()
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
        self.model_data = new_data

    def data(self, index, role):
        """Return model data by index."""
        if role == QtCore.Qt.DisplayRole and index.isValid():
            if index.column() == 0:
                return QtCore.QVariant(str(self.model_data[index.row()][index.column()]))

            else:
                formatted = '{number:.{digits}f}'.format(number=float(self.model_data[index.row()][index.column()]), digits=8)
                return QtCore.QVariant(formatted)
    
            # print("CELL VALUE: ", self.model_data[index.row()][index.column()])
            # return(QtCore.QVariant(self.model_data[index.row()][index.column()]))
        else:
            return QtCore.QVariant()


class HistoricDelegate(QtWidgets.QStyledItemDelegate):
    """Class to define a custom item style."""

    def __init__(self, parent):
        super(HistoricDelegate, self).__init__(parent)
        self.parent = parent
        self.mw = app.mw

    def initStyleOption(self, option, index):
        """Set style options based on index column."""

        if index.column() == 0:
            option.text = index.data().replace("BTC", "") + " / BTC"

        # elif index.column() == 1:
        #     option.text = '{number:,.{digits}f}'.format(number=float(index.data()), digits=val["assetDecimals"])

        # elif index.column() == 2:
        #     option.text = str(datetime.fromtimestamp(int(str(self.parent.my_model.model_data[index.row()][3])[:-3])).strftime('%H:%M:%S.%f')[:-7])

        else:
            super(HistoricDelegate, self).initStyleOption(option, index)


    def paint(self, painter, option, index):
        """Reimplemented custom paint method."""
        painter.save()
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        # font = QtGui.QFont()
        
        painter.setPen(QtGui.QColor(Colors.color_lightgrey))
        painter.drawText(option.rect, QtCore.Qt.AlignRight, options.text)


       


        # if index.column() == 0:
        #     if self.parent.my_model.model_data[index.row()][2] is True:

        #         if option.state & QtWidgets.QStyle.State_MouseOver:
        #             painter.setPen(QtGui.QColor("#ff58a8"))
        #             font.setBold(True)
        #         else:
        #             painter.setPen(QtGui.QColor(Colors.color_pink))
        #     else:

        #         if option.state & QtWidgets.QStyle.State_MouseOver:
        #             painter.setPen(QtGui.QColor("#aaff00"))
        #             font.setBold(True)
        #         else:
        #             painter.setPen(QtGui.QColor(Colors.color_green))
        #     painter.setFont(font)
        #     painter.drawText(option.rect, QtCore.Qt.AlignRight, options.text)

        # elif index.column() == 1:
        #     if option.state & QtWidgets.QStyle.State_MouseOver:
        #         painter.setPen(QtGui.QColor(QtCore.Qt.white))
        #         font.setBold(True)
        #     else:
        #         painter.setPen(QtGui.QColor(Colors.color_lightgrey))
        #     painter.setFont(font)
        #     painter.drawText(option.rect, QtCore.Qt.AlignRight, options.text)

        # elif index.column() == 2:
        #     painter.setPen(QtGui.QColor(Colors.color_grey))
        #     painter.drawText(option.rect, QtCore.Qt.AlignHCenter, options.text)

        painter.restore()
