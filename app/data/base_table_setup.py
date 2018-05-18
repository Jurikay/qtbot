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


#################################################################
# BaseTableView
#################################################################


class BaseTableView(QtWidgets.QTableView):

    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.setItemDelegate(BasicDelegate(self))
        self.my_model = SortFilterModel(self)

        # print("BASE TABLE MODEL", self.my_model)
        self.df = None
        self.mw = app.mw
        self.setSortingEnabled(True)
        self.clicked.connect(self.cell_clicked)


    def websocket_update(self):
        if self.my_model.rowCount() == 0:
            self.setup()

        else:
            self.update()

    def setup(self):
        self.update()
        df_rows = len(self.df)
        # if self.my_model.rowCount():
        if df_rows > 0:
            # print("BASE TABLE SETUP")
            self.setModel(self.my_model)
            self.set_default_widths()
            self.sortByColumn(0, QtCore.Qt.DescendingOrder)

    def update(self):
        # print("BASE TABLE UPDATE")
        # self.my_model.modelAboutToBeReset.emit()
        # set_df has to be extended
        self.df = self.set_df()
        self.my_model.update(self.df)
        # self.my_model.modelReset.emit()

    def set_default_widths(self):
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(30)

        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().setDefaultSectionSize(100)
        self.set_widths()


    def leaveEvent(self, event):
        print("LEAVE EVENT")
        app.main_app.restoreOverrideCursor()

    def set_widths(self):
        pass


    # def set_df(self):
    #     # print("set empty df")
    #     """This should be overwritten."""
    #     return pd.DataFrame

    # def cell_clicked(self, index):
    #     """This should be overwritten."""
    #     pass


#################################################################
# BaseTableModel
#################################################################


class BaseTableModel(QtCore.QAbstractTableModel):
    """TableModel that receives it's data from a pandas DataFrame."""
    def __init__(self, parent=None, *args):
        super(BaseTableModel, self).__init__()
        self.mw = app.mw
        self.datatable = None


    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Set header data."""
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.datatable.columns[section]


    def update(self, dataIn):
        self.modelAboutToBeReset.emit()
        self.datatable = dataIn
        self.modelReset.emit()


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


    # def setFilter(self):
    #     # print("BASIC FILTER")
    #     pass


class SortFilterModel(BaseTableModel):
    """SortFilterModel extends BaseTableModel and adds sort
    and filter functionality."""
    def __init__(self, parent=None, filter_col=0, *args, **kwargs):
        BaseTableModel.__init__(self, *args, **kwargs)
        self.parent = parent
        self.searchText = None
        self.order_col = 0
        self.order_dir = True
        self.filter_col = filter_col

        self.current_coin = None
        self.old_search_text = None


    def set_current_coin(self, state):
        print("SET CURRENT COIN")
        print("state", state)
        if state == 2:
            self.old_search_text = self.mw.coinindex_filter.text()
            self.searchText = self.mw.cfg_manager.coin
            self.setFilter(self.searchText)
            self.mw.coinindex_filter.setText(self.searchText)
            self.mw.coinindex_filter.setEnabled(False)
            self.mw.coinindex_filter.setStyleSheet("color: grey")
        else:
            self.searchText = self.old_search_text
            self.setFilter(self.searchText)
            self.mw.coinindex_filter.setText(self.old_search_text)
            self.mw.coinindex_filter.setEnabled(True)
            self.mw.coinindex_filter.setStyleSheet("color: white")


    def setFilter(self, searchText=None):
        # print("setfilter", searchText)

        self.searchText = searchText
        if searchText:
            for row in range(self.rowCount()):
                self.parent.setRowHidden(row, False)


                current_coin = str(self.datatable.iloc[row, self.filter_col]).replace("BTC", "")

                if str(searchText.upper()) in current_coin:
                    self.parent.setRowHidden(row, False)
                else:
                    self.parent.setRowHidden(row, True)

        else:
            for row in range(self.rowCount()):
                self.parent.setRowHidden(row, False)


    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        if isinstance(self.datatable, pd.DataFrame):
            self.modelAboutToBeReset.emit()

            if len(self.datatable) > 0:
                self.datatable = self.datatable.sort_values(self.datatable.columns[Ncol], ascending=not order)

            # save order dir and order col
            self.order_col = Ncol
            self.order_dir = order

            self.modelReset.emit()

            if self.searchText:
                self.setFilter(searchText=self.searchText)

    def update(self, dataIn):
        self.datatable = dataIn
        self.sort(self.order_col, self.order_dir)

#################################################################
# Custom Delegates
#################################################################


class BasicDelegate(QtWidgets.QStyledItemDelegate):
    """Basic StyledItemDelegate implementation"""
    center = int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

    def __init__(self, parent, text_color=Colors.color_lightgrey, align=center):
        super(BasicDelegate, self).__init__(parent)
        self.parent = parent
        self.fg_color = text_color
        self.font = QtGui.QFont()
        self.mw = app.mw
        self.align = align


    def initStyleOption(self, option, index):
        option.text = index.data()
        self.font = QtGui.QFont()


    def paint(self, painter, option, index):
        painter.save()
        if option.state & QtWidgets.QStyle.State_MouseOver:
            app.main_app.restoreOverrideCursor()

        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        painter.setFont(self.font)
        painter.setPen(QtGui.QColor(self.fg_color))

        painter.drawText(option.rect, self.align, options.text)
        painter.restore()


class HoverDelegate(BasicDelegate):
    def __init__(self, parent, hover_color=Colors.color_yellow, text_color=Colors.color_lightgrey):
        super(HoverDelegate, self).__init__(parent)
        self.normal_color = text_color
        self.hover_color = hover_color

    def initStyleOption(self, option, index):
        if option.state & QtWidgets.QStyle.State_MouseOver:
            self.fg_color = self.hover_color
            self.font.setBold(True)
            if app.main_app.overrideCursor() != QtCore.Qt.PointingHandCursor:
                app.main_app.setOverrideCursor(QtCore.Qt.PointingHandCursor)
        else:
            self.fg_color = self.normal_color
            self.font.setBold(False)

        option.text = index.data()






class ChangePercentDelegate(BasicDelegate):
    def initStyleOption(self, option, index):
        if float(index.data()) < 0:
            prefix = ""
            self.fg_color = Colors.color_pink
        elif float(index.data()) == 0:
            prefix = " "
            self.fg_color = Colors.color_lightgrey

        else:
            prefix = "+"
            self.fg_color = Colors.color_green

        option.text = prefix + '{number:.{digits}f}'.format(number=float(index.data()), digits=2) + "%"


class FilledPercentDelegate(BasicDelegate):

    def initStyleOption(self, option, index):
        if float(index.data()) == 0.00:
            self.fg_color = Colors.color_pink
        elif float(index.data()) < 25:
            self.fg_color = Colors.color_pink
        elif float(index.data()) < 75:
            self.fg_color = Colors.color_yellow
        else:
            self.fg_color = Colors.color_green

        option.text = '{number:.{digits}f}'.format(number=float(index.data()), digits=2) + "%"



class DateDelegate(BasicDelegate):
    """Basic style delegate"""

    def initStyleOption(self, option, index):
        option.text = str(datetime.fromtimestamp(int(str(index.data())[:-3])).strftime('%d.%m.%y - %H:%M:%S.%f')[:-7])


class RoundFloatDelegate(BasicDelegate):
    """Delegate that rounds a float to the given decimal place.
        Defaults to 8."""

    def __init__(self, parent, round_to=8, suffix="", text_color=Colors.color_lightgrey):
        super(RoundFloatDelegate, self).__init__(parent)
        self.round_to = round_to
        self.mw = app.mw
        self.suffix = suffix

    def initStyleOption(self, option, index):
        option.text = '{number:,.{digits}f}'.format(number=float(index.data()), digits=self.round_to) + str(self.suffix)



class RoundAssetDelegate(RoundFloatDelegate):
    """ Takes the parameters asset_column and paring as well as suffix."""
    def __init__(self, parent, asset_column=1, pairing="", suffix="", text_color=Colors.color_lightgrey):
        super(RoundAssetDelegate, self).__init__(parent)
        self.asset_column = asset_column
        self.suffix = suffix
        self.pairing = pairing


    def initStyleOption(self, option, index):

        model = self.parent.model()

        pair_index = model.index(index.row(), self.asset_column)
        pair = model.data(pair_index, QtCore.Qt.DisplayRole)
        # try:
        if pair != "BTC":
            assetDecimals = self.mw.tickers[pair + self.pairing]["assetDecimals"]
        else:
            assetDecimals = 8
        # except KeyError as e:
            # print("init key error", e)
        #     assetDecimals = 8
        self.round_to = int(assetDecimals)
        # print(index.row(), pair, assetDecimals)
        option.text = '{number:,.{digits}f}'.format(number=float(index.data()), digits=self.round_to) + str(self.suffix)


class BuySellDelegete(BasicDelegate):
    """Delegate that colors a cell green or pink depending on
    if it's content is "BUY" order "SELL"."""

    def initStyleOption(self, option, index):
        super(BuySellDelegete, self).initStyleOption(option, index)
        if index.data() == "BUY":
            self.fg_color = Colors.color_green
        else:
            self.fg_color = Colors.color_pink





class PairDelegate(QtWidgets.QStyledItemDelegate):
    """Delegate that adds an icon + hover effect to a pair."""

    @staticmethod
    def initStyleOption(option, index):
        """Set style options based on index column."""
        option.text = index.data().replace("BTC", "") + " / BTC"
        option.icon = QtGui.QIcon("images/ico/" + index.data().replace(
                                  "BTC", "") + ".svg")

    def paint(self, painter, option, index):
        """Reimplemented custom paint method."""

        # alignment = int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        align_left = int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        painter.save()
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        font = QtGui.QFont()


        iconRect = QtCore.QRect(option.rect.left(),
                                option.rect.top(),
                                # icon is quadratic; set width to it's height.
                                option.rect.height(),
                                option.rect.height())

        textRect = QtCore.QRect(option.rect.left() + iconRect.width() + 5,
                                option.rect.top(),
                                # subtract previously added icon width.
                                option.rect.width() - iconRect.width(),
                                option.rect.height())



        if option.state & QtWidgets.QStyle.State_MouseOver:
            painter.setPen(QtGui.QColor(Colors.color_yellow))
            font.setBold(True)
            painter.setFont(font)

            # set cursor
            if app.main_app.overrideCursor() != QtCore.Qt.PointingHandCursor:
                app.main_app.setOverrideCursor(QtCore.Qt.PointingHandCursor)

        else:
            painter.setPen(QtGui.QColor(Colors.color_lightgrey))

        icon = options.icon
        icon.paint(painter, iconRect, QtCore.Qt.AlignLeft)
        painter.drawText(textRect, align_left, options.text)
        painter.restore()



class CoinDelegate(PairDelegate):
    def initStyleOption(self, option, index):
        option.text = index.data()
        # print("INDEX DATA", index.data())
        option.icon = QtGui.QIcon("images/ico/" + index.data() + ".svg")


#################################################################
# Implementations
#################################################################


class OpenOrders(BaseTableView):
    """Extended TableView that draws a colored background."""

    def __init__(self, parent=None, *args):
        super(OpenOrders, self).__init__()
        self.my_model = SortFilterModel(self, 1)
        self.setItemDelegateForColumn(0, DateDelegate(self))
        self.setItemDelegateForColumn(1, PairDelegate(self))
        self.setItemDelegateForColumn(3, BuySellDelegete(self))
        self.setItemDelegateForColumn(4, RoundFloatDelegate(self))
        self.setItemDelegateForColumn(5, RoundAssetDelegate(self, 1))
        self.setItemDelegateForColumn(6, FilledPercentDelegate(self))
        self.setItemDelegateForColumn(7, RoundFloatDelegate(self, 8))
        self.setItemDelegateForColumn(9, HoverDelegate(self, Colors.color_lightgrey, Colors.color_pink))

        self.parent = parent


    def set_df(self):
        return self.mw.user_data.create_open_orders_df()


    def cell_clicked(self, index):
        """Change pair or cancel order"""
        if index.column() == 9:
            row = index.row()

            # check proxy model data to account for
            # sort order and or filter
            model = self.model()

            id_index = model.index(row, 8)
            pair_index = model.index(row, 1)
            order_id = model.data(id_index, QtCore.Qt.DisplayRole)
            pair = model.data(pair_index, QtCore.Qt.DisplayRole)

            self.mw.api_manager.cancel_order_byId(order_id, pair)

        elif index.column() == 1:
            pair = index.data()
            coin = pair.replace("BTC", "")
            self.mw.gui_manager.change_to(coin)

    def set_widths(self):
        for i in range(4):
            self.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Fixed)

        self.setColumnWidth(0, 130)
        self.setColumnWidth(1, 120)
        self.setColumnWidth(2, 60)
        self.setColumnWidth(3, 60)


class History(BaseTableView):
    def __init__(self, parent=None, *args):
        super(History, self).__init__()
        self.my_model = SortFilterModel(self, 1)
        self.setItemDelegateForColumn(0, DateDelegate(self))
        self.setItemDelegateForColumn(1, PairDelegate(self))
        self.setItemDelegateForColumn(2, BuySellDelegete(self))
        self.setItemDelegateForColumn(3, RoundFloatDelegate(self))
        self.setItemDelegateForColumn(4, RoundAssetDelegate(self, 1))
        self.setItemDelegateForColumn(5, RoundFloatDelegate(self, 8))


    def set_df(self):
        return self.mw.user_data.create_history_df()

    def set_widths(self):
        for i in range(self.my_model.columnCount()):
            self.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

    def cell_clicked(self, index):
        if index.column() == 1:
            pair = index.data()
            coin = pair.replace("BTC", "")
            self.mw.gui_manager.change_to(coin)


class Holdings(BaseTableView):
    def __init__(self, parent=None, *args):
        super(Holdings, self).__init__()
        self.my_model = SortFilterModel(self, 0)
        self.setItemDelegateForColumn(0, CoinDelegate(self))
        self.setItemDelegateForColumn(2, RoundAssetDelegate(self, 0, "BTC"))
        self.setItemDelegateForColumn(3, RoundAssetDelegate(self, 0, "BTC"))
        self.setItemDelegateForColumn(4, RoundAssetDelegate(self, 0, "BTC"))
        self.setItemDelegateForColumn(5, RoundFloatDelegate(self))


    def set_df(self):
        return self.mw.user_data.create_holdings_df()

    def cell_clicked(self, index):
        if index.column() == 0:
            pair = index.data()
            if pair != "BTC":
                self.mw.gui_manager.change_to(pair)

    def set_widths(self):
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.setColumnWidth(0, 130)


class Index(BaseTableView):
    def __init__(self, parent=None, *args):
        super(Index, self).__init__()
        self.my_model = SortFilterModel(self, 0)

        self.setItemDelegateForColumn(0, PairDelegate(self))
        self.setItemDelegateForColumn(1, RoundFloatDelegate(self, 8, " BTC"))
        self.setItemDelegateForColumn(2, ChangePercentDelegate(self))
        self.setItemDelegateForColumn(3, RoundFloatDelegate(self, 2))

        for i in range(4, 7):
            self.setItemDelegateForColumn(i, RoundFloatDelegate(self, 3))

        for i in range(7, 10):
            self.setItemDelegateForColumn(i, ChangePercentDelegate(self))



    def set_df(self):
        return self.mw.index_data.coin_index

    def set_widths(self):
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.setColumnWidth(0, 130)
        self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        self.setColumnWidth(1, 130)

    def cell_clicked(self, index):
        if index.column() == 0:
            pair = index.data()
            coin = pair.replace("BTC", "")
            self.mw.gui_manager.change_to(coin)
