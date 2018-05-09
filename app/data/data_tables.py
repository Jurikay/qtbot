# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import app
import pandas as pd
from datetime import datetime
from app.colors import Colors


class DataOpenOrders(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.my_model = OpenOrdersModel(self)
        self.data_dict = None
        self.df = None
        self.mw = app.mw
        self.setItemDelegate(OpenOrdersDelegate(self))
        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.setSortingEnabled(True)
        self.clicked.connect(self.cell_clicked)


    def setup(self):

        try:
            self.update()
        except (AttributeError, KeyError) as e:
            print("UPDATE ERROR!", e)
            return



        if self.my_model.rowCount():

            self.proxy_model.setSourceModel(self.my_model)
            self.setModel(self.proxy_model)


            self.set_widths()

            self.sortByColumn(0, QtCore.Qt.DescendingOrder)
        else:
            print("NO ROWS")


    def update(self):

        self.my_model.modelAboutToBeReset.emit()
        self.df = self.mw.user_data.create_dataframe()
        self.my_model.update(self.df)

        self.my_model.modelReset.emit()

    def set_widths(self):
        self.horizontalHeader().setDefaultSectionSize(50)
        self.setColumnWidth(0, 130)
        self.setColumnWidth(1, 130)
        self.setColumnWidth(2, 60)
        self.setColumnWidth(3, 60)
        for i in range(4, 9):
            self.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

    def cell_clicked(self, index):
        """Change pair or cancel order"""
        if index.column() == 9:

            row = index.row()

            # check proxy model data to account for
            # sort order and or filter
            model = self.proxy_model

            id_index = model.index(row, 8)
            pair_index = model.index(row, 1)
            order_id = model.data(id_index, QtCore.Qt.DisplayRole)
            pair = model.data(pair_index, QtCore.Qt.DisplayRole)

            self.mw.api_manager.cancel_order_byId(order_id, pair)

        elif index.column() == 1:
            pair = index.data()
            coin = pair.replace("BTC", "")
            self.mw.gui_manager.change_to(coin)


class OpenOrdersModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None, *args):
        super(OpenOrdersModel, self).__init__()
        self.mw = app.mw
        self.datatable = None
        self.header_data = ["Date & Time", "Pair", "Type", "Side", "Price", "Quantity", "Filled %", "Total", "id", "cancel"]

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Set header data."""
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                # return self.headers[section]
                # return self.datatable.columns[section]
                return self.header_data[section]


    def update(self, dataIn):
        self.datatable = dataIn


    def rowCount(self, parent=QtCore.QModelIndex()):
        if isinstance(self.datatable, pd.DataFrame):
            return len(self.datatable.index)
        else:
            return 0

    def columnCount(self, parent=QtCore.QModelIndex()):
        if isinstance(self.datatable, pd.DataFrame):
            return len(self.datatable.columns.values)
        else:
            return 0

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if index.isValid():
                return str(self.datatable.iloc[index.row(), index.column()])


class OpenOrdersDelegate(QtWidgets.QStyledItemDelegate):
    """Class to define the style of index values."""

    def __init__(self, parent):
        super(OpenOrdersDelegate, self).__init__(parent)
        self.parent = parent
        self.mw = app.mw

        self.center = int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.left = int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.right = int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    def initStyleOption(self, option, index):
        """Set style options based on index column."""
        if index.column() == 0:
            option.text = str(datetime.fromtimestamp(int(str(index.data())[:-3])).strftime('%d.%m.%y - %H:%M:%S.%f')[:-7])
        elif index.column() == 1:
            option.icon = QtGui.QIcon("images/ico/" + index.data().replace("BTC", "") + ".svg")
            option.text = str(index.data())

        else:
            super(OpenOrdersDelegate, self).initStyleOption(option, index)


    def paint(self, painter, option, index):
        """Reimplemented custom paint method."""
        painter.save()
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        font = QtGui.QFont()
        painter.setPen(QtGui.QColor(Colors.color_lightgrey))


        # ICON, Coin hover
        if index.column() == 1:
            font = QtGui.QFont()

            icon = QtGui.QIcon("images/ico/" + index.data().replace("BTC", "") + ".svg")
            iconRect = QtCore.QRect(option.rect.left(),
                                    option.rect.top(),
                                    option.rect.height(),
                                    option.rect.height())

            icon.paint(painter, iconRect, QtCore.Qt.AlignLeft)

            if option.state & QtWidgets.QStyle.State_MouseOver:
                painter.setPen(QtGui.QColor(Colors.color_yellow))
                font.setBold(True)
                painter.setFont(font)
            else:
                painter.setPen(QtGui.QColor(Colors.color_lightgrey))

            painter.drawText(option.rect, self.right, options.text)


        # BUY / SELL color
        elif index.column() == 3:
            if index.data() == "SELL":
                painter.setPen(QtGui.QColor(Colors.color_pink))
            else:
                painter.setPen(QtGui.QColor(Colors.color_green))

            painter.drawText(option.rect, self.center, options.text)


        # cancel button
        elif index.column() == 9:
            # painter.setPen(QtGui.QColor(Colors.color_yellow))
            # painter.drawText(option.rect, self.center, options.text)

            if option.state & QtWidgets.QStyle.State_MouseOver:
                painter.setPen(QtGui.QColor(Colors.color_yellow))
                font.setBold(True)
                font.setUnderline(True)
                painter.setFont(font)
            else:
                painter.setPen(QtGui.QColor(Colors.color_pink))

            painter.drawText(option.rect, self.center, options.text)


        # date
        elif index.column() == 0:
            painter.setPen(QtGui.QColor(Colors.color_lightgrey))
            painter.drawText(option.rect, self.left, options.text)

        else:
            # super(OpenOrdersDelegate, self).initStyleOption(option, index)
            # print(index.column(), options.text, index.data())
            painter.setPen(QtGui.QColor(Colors.color_lightgrey))
            painter.drawText(option.rect, self.center, options.text)
        painter.restore()
