# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Base implementations of QTableView, QAbstractTableModel and
QStyledItemDelegate that serve as a starting point for all tableviews."""


import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import app
import pandas as pd
from datetime import datetime
from app.colors import Colors
# import time
from app.data.base_table_setup import BaseTableModel, BasicDelegate, HoverDelegate, RoundFloatDelegate
# from app.data.new_orderbook_table import OrderbookTable
# from app.init import val


class BackgroundTable(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.my_model = BaseTableModel(self)
        self.data_dict = None
        self.df = None
        self.mw = app.mw

        # self.proxy_model = QtCore.QSortFilterProxyModel()
        self.setSortingEnabled(True)
        self.clicked.connect(self.cell_clicked)
        self.max_order = 0
        self.data = None
        self.has_data = False
        self.compare_col = 3
        self.get_color = False

    def paintEvent(self, event):

        if self.has_data is True:
            row_count = self.my_model.rowCount()
            total_width = self.horizontalHeader().width()
            painter = QtGui.QPainter(self.viewport())
            for row in range(row_count):

                # get row color:
                if self.get_color is True:
                    if self.mw.trade_history[row][2] is True:
                        self.bg_color = "#473043"
                    else:
                        self.bg_color = "#3b4c37"

                rowY = self.rowViewportPosition(row)
                rowH = self.rowHeight(row)
                # print(row, rowY, rowH)

                # Create the painter
                value = self.df.iloc[row, self.compare_col]
                percentage = value / self.max_order

                my_rect = QtCore.QRect(0, rowY, (percentage * total_width), rowH)

                painter.save()
                painter.setBrush(QtGui.QColor(self.bg_color))
                painter.setPen(QtGui.QColor("#20262b"))

                painter.drawRect(my_rect)
                painter.restore()

        super(BackgroundTable, self).paintEvent(event)


    def setup(self):
        self.update()

        self.setModel(self.my_model)
        # self.proxy_model.setSourceModel(self.my_model)

        self.set_widths()

        self.sortByColumn(0, QtCore.Qt.DescendingOrder)


    def update(self, payload=None):
        # print("asks update")
        self.my_model.modelAboutToBeReset.emit()


        self.df = self.set_df()

        self.my_model.update(self.df)

        self.my_model.modelReset.emit()

        self.mw.live_data.set_spread()


    def set_df(self):
        return self.create_dataframe(self.data)

    def create_dataframe(self, side):
        if side == "asks":
            df = pd.DataFrame(self.mw.orderbook["asks"])
        elif side == "bids":
            df = pd.DataFrame(self.mw.orderbook["bids"])


        df.columns = ["Price", "Amount", "Total"]
        cols = df.columns
        df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
        total = df.Price * df.Amount
        df["Total"] = total
        df['#'] = df.index + 1
        df = df[["#", "Price", "Amount", "Total"]]

        # reverse asks
        if side == "asks":
            df = df.reindex(index=df.index[::-1])

        maxval = df["Total"].max()
        self.max_order = maxval
        self.has_data = True
        # print("return df", df["Total"])
        return df

    def create_history_df(self):
        df = pd.DataFrame(self.mw.trade_history)
        df.columns = ["Price", "Amount", "isBuyer", "Time"]
        df = df.apply(pd.to_numeric, errors="ignore")
        df = df[["Price", "Amount", "Time"]]

        maxval = df["Amount"].max()
        self.max_order = maxval
        self.has_data = True
        return df


    def set_widths(self):
        self.horizontalHeader().setDefaultSectionSize(100)

        self.setColumnWidth(0, 25)

        self.horizontalHeader().setSortIndicatorShown(False)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(16)
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        for i in range(1, 4):
            self.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

    def cell_clicked(self, index):
        """When Orderbook is clicked, copy price or quantity on click."""
        try:
            row = index.row()
            col = index.column()
            # copy price

            if self.data == "asks":
                row = 20 - row - 1

            if col == 1:
                self.mw.limit_buy_input.setValue(float(self.mw.orderbook[self.data][row][0]))
                self.mw.limit_sell_input.setValue(float(self.mw.orderbook[self.data][row][0]))
            # copy quantity
            elif col == 2:
                self.mw.limit_buy_amount.setValue(float(self.mw.orderbook[self.data][row][1]))
                self.mw.limit_sell_amount.setValue(float(self.mw.orderbook[self.data][row][1]))
        except IndexError as e:
            print("CELL CLICK ERROR: " + str(e))

    def leaveEvent(self, event):
        print("LEAVE EVENT")
        app.main_app.restoreOverrideCursor()


class AsksDelegate(QtWidgets.QStyledItemDelegate):
    """Class to define the style of index values."""

    def __init__(self, parent):
        super(AsksDelegate, self).__init__(parent)
        self.parent = parent
        self.mw = app.mw

        self.center = int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.left = int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.right = int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    def initStyleOption(self, option, index):
        """Set style options based on index column."""
        if index.column() == 0:
            option.text = str(index.data()).zfill(2)

        elif index.column() == 1:
            option.text = '{number:,.{digits}f}'.format(number=float(index.data()), digits=self.mw.tickers[self.mw.cfg_manager.pair]["decimals"])

        elif index.column() == 2:
            option.text = '{number:,.{digits}f}'.format(number=float(index.data()), digits=self.mw.tickers[self.mw.cfg_manager.pair]["assetDecimals"])

        elif index.column() == 3:
            option.text = '{number:,.{digits}f}'.format(number=float(index.data()), digits=3) + " BTC"

        # else:
        #     super(AsksDelegate, self).initStyleOption(option, index)


    def paint(self, painter, option, index):
        """Reimplemented custom paint method."""
        painter.save()
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        font = QtGui.QFont()


        if index.column() == 0:
            painter.setPen(QtGui.QColor("#ffffff"))
            alignment = self.left
            # painter.drawText(option.rect, self.center, options.text)

        elif index.column() == 1:
            alignment = self.center
            if option.state & QtWidgets.QStyle.State_MouseOver:
                    painter.setPen(QtGui.QColor(self.parent.highlight))
                    font.setBold(True)
            else:
                painter.setPen(QtGui.QColor(self.parent.color))

        elif index.column() == 2:
            painter.setPen(QtGui.QColor(Colors.color_lightgrey))
            alignment = self.right

        else:
            painter.setPen(QtGui.QColor(Colors.color_lightgrey))
            alignment = self.center

        painter.setFont(font)
        painter.drawText(option.rect, alignment, options.text)

        painter.restore()


class HistPriceDelegate(BasicDelegate):

    def initStyleOption(self, option, index):
        decimals = self.mw.tickers[self.mw.cfg_manager.pair]["decimals"]
        option.text = '{number:.{digits}f}'.format(number=float(index.data()), digits=decimals)

        if self.mw.trade_history[index.row()][2] is True:
            self.normal_color = Colors.color_pink
            self.hover_color = "#ff58a8"

        else:
            self.normal_color = Colors.color_green
            self.hover_color = "#aaff00"

        if option.state & QtWidgets.QStyle.State_MouseOver:
            self.fg_color = self.hover_color
            self.font.setBold(True)
            if app.main_app.overrideCursor() != QtCore.Qt.PointingHandCursor:
                app.main_app.setOverrideCursor(QtCore.Qt.PointingHandCursor)
        else:
            self.fg_color = self.normal_color
            self.font.setBold(False)


class OrderbookCountDelegate(BasicDelegate):
    def initStyleOption(self, option, index):
        option.text = str(index.data()).zfill(2)


class OrderbookPriceDelegate(HoverDelegate):
    def initStyleOption(self, option, index):
        super(OrderbookPriceDelegate, self).initStyleOption(option, index)
        decimals = self.mw.tickers[self.mw.cfg_manager.pair]["decimals"]
        option.text = '{number:,.{digits}f}'.format(number=float(index.data()), digits=decimals)


class OrderbookQtyDelegate(HoverDelegate):
    def initStyleOption(self, option, index):
        super(OrderbookQtyDelegate, self).initStyleOption(option, index)
        assetDecimals = self.mw.tickers[self.mw.cfg_manager.pair]["assetDecimals"]
        option.text = '{number:,.{digits}f}'.format(number=float(index.data()), digits=assetDecimals)
        self.align = int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)



class TimeDelegate(BasicDelegate):
    """Basic style delegate"""

    def initStyleOption(self, option, index):
        option.text = str(datetime.fromtimestamp(int(str(index.data())[:-3])).strftime('%H:%M:%S.%f')[:-7])


#######################################


class AsksView(BackgroundTable):
    def __init__(self, *args, **kwargs):
        BackgroundTable.__init__(self, *args, **kwargs)
        self.color = Colors.color_pink
        self.bg_color = "#473043"
        self.highlight = "#ff58a8"
        self.data = "asks"
        self.has_data = False
        self.setItemDelegateForColumn(0, OrderbookCountDelegate(self))
        self.setItemDelegateForColumn(1, OrderbookPriceDelegate(self, "#ff58a8", Colors.color_pink))
        self.setItemDelegateForColumn(2, OrderbookQtyDelegate(self, "#fff"))
        self.setItemDelegateForColumn(3, RoundFloatDelegate(self, 3, " BTC"))

    # def get_max_value(self, df):
    #     max_val = df["Total"].max()
    #     return max_val

    def set_df(self):
        return self.create_dataframe(self.data)


class BidsView(BackgroundTable):
    def __init__(self, *args, **kwargs):
        BackgroundTable.__init__(self, *args, **kwargs)
        self.color = Colors.color_green
        self.bg_color = "#3b4c37"
        self.highlight = "#aaff00"
        self.data = "bids"
        self.has_data = False
        self.setItemDelegateForColumn(0, OrderbookCountDelegate(self))
        self.setItemDelegateForColumn(1, OrderbookPriceDelegate(self, "#aaff00", Colors.color_green))
        self.setItemDelegateForColumn(2, OrderbookQtyDelegate(self, "#fff"))
        self.setItemDelegateForColumn(3, RoundFloatDelegate(self, 3, " BTC"))

    def set_df(self):
        return self.create_dataframe(self.data)


class HistView(BackgroundTable):
    def __init__(self, *args, **kwargs):
        BackgroundTable.__init__(self, *args, **kwargs)
        self.color = Colors.color_green
        self.bg_color = "#3b4c37"
        self.highlight = "#aaff00"
        self.has_data = False
        self.compare_col = 1
        # self.setItemDelegate(HistoryDelegate(self))
        self.get_color = True
        self.setItemDelegateForColumn(0, HistPriceDelegate(self))
        self.setItemDelegateForColumn(1, OrderbookQtyDelegate(self, "#fff"))
        self.setItemDelegateForColumn(2, TimeDelegate(self, Colors.color_grey))

    def set_df(self):
        return self.create_history_df()


    def set_widths(self):
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(15)

        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().setDefaultSectionSize(75)
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)

        self.setColumnWidth(0, 80)
        self.setColumnWidth(1, 80)

    def cell_clicked(self, index):
        """When History is clicked, copy price or quantity on click."""
        try:
            row = index.row()
            col = index.column()
            # copy price
            if col == 0:
                self.mw.limit_buy_input.setValue(float(self.mw.trade_history[row][0]))
                self.mw.limit_sell_input.setValue(float(self.mw.trade_history[row][0]))
            # copy quantity
            elif col == 1:
                self.mw.limit_buy_amount.setValue(float(self.mw.trade_history[row][1]))
                self.mw.limit_sell_amount.setValue(float(self.mw.trade_history[row][1]))
        except IndexError as e:
            print("CELL CLICK ERROR: " + str(e))
