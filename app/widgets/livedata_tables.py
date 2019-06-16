# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Base implementations of QTableView, QAbstractTableModel and
QStyledItemDelegate that serve as a starting point for all tableviews."""


import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import pandas as pd
from datetime import datetime
import app
from app.colors import Colors
from app.widgets.base_table import BaseTableModel
from app.widgets.table_implementations import BasicDelegate, HoverDelegate, RoundFloatDelegate
# debug
# from pprint import pprint


class BackgroundTable(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.my_model = BaseTableModel(self)
        self.side_dict = None
        self.df = None
        self.mw = app.mw

        # self.proxy_model = QtCore.QSortFilterProxyModel()
        self.setSortingEnabled(True)
        self.clicked.connect(self.cell_clicked)
        self.max_order = 0
        self.side = None
        self.has_data = False
        self.compare_col = 3
        self.get_color = False
        self.bg_color = None
        self.rowH = 18


    def paintEvent(self, event):
        if self.df is not None and isinstance(self.df, pd.DataFrame) and not self.df.empty:
            if self.model():
                
                vh = self.verticalHeader()
        
                # Get the first and last rows that are visible in the view and if the 
                # last visiable row returns -1 set it to the row count
                firstVisualRow = max([vh.visualIndexAt(0), 0])
                lastVisualRow = vh.visualIndexAt(vh.viewport().height())
                if lastVisualRow == -1:
                    lastVisualRow = self.model().rowCount(self.rootIndex()) - 1  # 19

                total_width = self.horizontalHeader().width()
                painter = QtGui.QPainter(self.viewport())
                for row in range(firstVisualRow, lastVisualRow + 1):

                    # get row color:
                    if self.get_color is True:
                        
                        if self.mw.data.current["history"][row]["maker"] is True:
                            self.bg_color = "#473043"
                        else:
                            self.bg_color = "#3b4c37"

                    rowY = self.rowViewportPosition(row)

                    self.rowH = self.rowHeight(row)
                    # if not self.rowH:
                    #     self.rowH = self.rowHeight(row)

                    # Create the painter
                    value = self.df.iat[row, self.compare_col]

                    # Set the dataframe dependant on if self.side is present.
                    # If so, it is a bids or asks table and the max value is the total
                    # amount. For the trade history table, the order quantity is used as max value.
                    if self.side:
                        maxval = self.df["Total"].max()
                    else:
                        maxval = self.df["quantity"].max()

                    percentage = value / maxval

                    my_rect = QtCore.QRect(0, rowY, (percentage * total_width), self.rowH)

                    painter.save()
                    painter.setBrush(QtGui.QColor(self.bg_color))
                    painter.setPen(QtGui.QColor("transparent"))

                    painter.drawRect(my_rect)
                    painter.restore()

        super(BackgroundTable, self).paintEvent(event)


    def setup(self):
        self.update()
        self.setModel(self.my_model)
        
        self.set_widths()
        self.set_delegates()
        self.sortByColumn(0, QtCore.Qt.DescendingOrder)
        

    def update(self, payload=None):
        # self.my_model.layoutAboutToBeChanged.emit()
        self.df = self.set_df()
        self.my_model.update(self.df)
        # self.my_model.layoutChanged.emit()

    # def set_df(self):
    #     return self.create_dataframe(self.side)

    # def create_dataframe(self, side):
    #     if side == "asks":
    #         df = pd.DataFrame(self.mw.data.current.orderbook["asks"])
    #     elif side == "bids":
    #         df = pd.DataFrame(self.mw.data.current.orderbook["bids"])


        # df.columns = ["Price", "Amount", "Total"]
        # cols = df.columns
        # df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
        # total = df.Price * df.Amount
        # df["Total"] = total
        # df['#'] = df.index + 1
        # df = df[["#", "Price", "Amount", "Total"]]

        # # reverse asks
        # if side == "asks":
        #     df = df.reindex(index=df.index[::-1])

        # maxval = df["Total"].max()
        # self.max_order = maxval
        # self.has_data = True
        # # print("return df", df["Total"])
        # return df

    # def create_history_df(self):
    #     df = pd.DataFrame(self.mw.data.current.history_df)

    #     df.columns = ["maker", "price", "quantity", "time"]
    #     df = df.apply(pd.to_numeric, errors="ignore")
    #     df = df[["price", "quantity", "time"]]

    #     maxval = df["quantity"].max()
    #     self.max_order = maxval
    #     self.has_data = True
    #     return df


    def set_widths(self):
        self.horizontalHeader().setDefaultSectionSize(100)

        self.setColumnWidth(0, 24)
        self.setColumnWidth(2, 60)

        self.horizontalHeader().setSortIndicatorShown(False)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(16)
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        # self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        # for i in range(1, 4):
        #     self.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)

    def cell_clicked(self, index):
        """When Orderbook is clicked, copy price or quantity on click."""
        try:
            row = index.row()
            col = index.column()
            # copy price

            if self.side == "asks":
                row = 20 - row - 1

            if col == 1:
                self.mw.limit_buy_input.setValue(float(self.mw.data.current.orderbook[self.side][row][0]))
                self.mw.limit_sell_input.setValue(float(self.mw.data.current.orderbook[self.side][row][0]))
            # copy quantity
            elif col == 2:
                self.mw.limit_buy_amount.setValue(float(self.mw.data.current.orderbook[self.side][row][1]))
                self.mw.limit_sell_amount.setValue(float(self.mw.data.current.orderbook[self.side][row][1]))
        except IndexError as e:
            print("CELL CLICK ERROR: " + str(e))

    def leaveEvent(self, event):
        app.main_app.restoreOverrideCursor()


# class AsksDelegate(QtWidgets.QStyledItemDelegate):
#     """Class to define the style of index values."""

#     def __init__(self, parent):
#         super(AsksDelegate, self).__init__(parent)
#         self.parent = parent
#         self.mw = app.mw

#         self.center = int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
#         self.left = int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
#         self.right = int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

#     def initStyleOption(self, option, index):
#         """Set style options based on index column."""
#         if index.column() == 0:
#             option.text = str(index.data()).zfill(2)

#         elif index.column() == 1:
#             option.text = '{number:,.{digits}f}'.format(number=float(index.data()), digits=self.mw.data.pairs[self.mw.data.current.pair]["decimals"])

#         elif index.column() == 2:
#             option.text = '{number:,.{digits}f}'.format(number=float(index.data()), digits=self.mw.data.pairs[self.mw.data.current.pair]["assetDecimals"])

#         elif index.column() == 3:
#             option.text = '{number:,.{digits}f}'.format(number=float(index.data()), digits=3) + " BTC"

#         # else:
#         #     super(AsksDelegate, self).initStyleOption(option, index)


#     def paint(self, painter, option, index):
#         """Reimplemented custom paint method."""
#         painter.save()
#         options = QtWidgets.QStyleOptionViewItem(option)
#         self.initStyleOption(options, index)
#         font = QtGui.QFont()


#         if index.column() == 0:
#             painter.setPen(QtGui.QColor("#ffffff"))
#             alignment = self.left
#             # painter.drawText(option.rect, self.center, options.text)

#         elif index.column() == 1:
#             alignment = self.center
#             if option.state & QtWidgets.QStyle.State_MouseOver:
#                     painter.setPen(QtGui.QColor(self.parent.highlight))
#                     font.setBold(True)
#             else:
#                 painter.setPen(QtGui.QColor(self.parent.color))

#         elif index.column() == 2:
#             painter.setPen(QtGui.QColor(Colors.color_lightgrey))
#             alignment = self.right

#         else:
#             painter.setPen(QtGui.QColor(Colors.color_lightgrey))
#             alignment = self.center

#         painter.setFont(font)
#         painter.drawText(option.rect, alignment, options.text)

#         painter.restore()


class HistPriceDelegate(BasicDelegate):

    
    def initStyleOption(self, option, index):

        decimals = self.mw.data.pairs[self.mw.data.current.pair]["decimals"]
        option.text = '{number:.{digits}f}'.format(number=float(index.data()), digits=decimals)

        if self.mw.data.current["history"][index.row()]["maker"] is True:
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

        decimals = self.mw.data.pairs[self.mw.data.current.pair]["decimals"]
        option.text = '{number:,.{digits}f}'.format(number=float(index.data()), digits=decimals)


class OrderbookQtyDelegate(HoverDelegate):
    def initStyleOption(self, option, index):
        super(OrderbookQtyDelegate, self).initStyleOption(option, index)
        assetDecimals = self.mw.data.pairs[self.mw.data.current.pair]["assetDecimals"]
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
        self.side = "asks"
        self.has_data = False
        self.set_delegates()

    # def get_max_value(self, df):
    #     max_val = df["Total"].max()
    #     return max_val

    def setup(self):
        super().setup()
        self.scrollToBottom()


    def set_delegates(self):
        self.setItemDelegateForColumn(0, OrderbookCountDelegate(self))
        self.setItemDelegateForColumn(1, OrderbookPriceDelegate(self, "#ff58a8", Colors.color_pink))
        self.setItemDelegateForColumn(2, OrderbookQtyDelegate(self, "#fff"))
        self.setItemDelegateForColumn(3, RoundFloatDelegate(self, 3, " BTC"))


    def set_df(self):
        return self.mw.data.current.depth_df[self.side].copy()


class BidsView(BackgroundTable):
    def __init__(self, *args, **kwargs):
        BackgroundTable.__init__(self, *args, **kwargs)
        self.color = Colors.color_green
        self.bg_color = "#3b4c37"
        self.highlight = "#aaff00"
        self.side = "bids"
        self.has_data = False


    def set_delegates(self):
        self.setItemDelegateForColumn(0, OrderbookCountDelegate(self))
        self.setItemDelegateForColumn(1, OrderbookPriceDelegate(self, "#aaff00", Colors.color_green))
        self.setItemDelegateForColumn(2, OrderbookQtyDelegate(self, "#fff"))
        self.setItemDelegateForColumn(3, RoundFloatDelegate(self, 3, " BTC"))

    def set_df(self):
        # return pd.DataFrame()
        df = self.mw.data.current.depth_df[self.side].copy()
        row_count = df.shape[0]

        # Fill df with empty data if it contains less than 20 values, to
        # avoid ui issues.
        for i in range(20 - row_count):
            df = df.append(pd.DataFrame([[str(row_count + i + 1), 0, 0, 0]], columns=df.columns))
        return df



class HistView(BackgroundTable):
    def __init__(self, *args, **kwargs):
        BackgroundTable.__init__(self, *args, **kwargs)
        self.color = Colors.color_green
        self.bg_color = "#3b4c37"
        self.highlight = "#aaff00"
        self.has_data = False
        self.compare_col = 1
        self.side = None
        # self.setItemDelegate(HistoryDelegate(self))
        self.get_color = True
        print("hist view get color:", self.get_color)
        self.set_delegates()

    def set_delegates(self):
        self.setItemDelegateForColumn(0, HistPriceDelegate(self))
        self.setItemDelegateForColumn(1, OrderbookQtyDelegate(self, "#fff"))
        self.setItemDelegateForColumn(2, TimeDelegate(self, Colors.color_grey))

    def set_df(self):
        df = self.mw.data.history_df()
        return df


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
                self.mw.limit_buy_input.setValue(float(self.mw.data.current.history[row]["price"]))
                self.mw.limit_sell_input.setValue(float(self.mw.data.current.history[row]["price"]))
            # copy quantity
            elif col == 1:
                self.mw.limit_buy_amount.setValue(float(self.mw.data.current.history[row]["quantity"]))
                self.mw.limit_sell_amount.setValue(float(self.mw.data.current.history[row]["quantity"]))
        except IndexError as e:
            print("CELL CLICK ERROR: " + str(e))
