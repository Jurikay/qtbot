# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import os
from datetime import datetime
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import app
from app.widgets.base_table import FilterModel, BaseTableView, BasicDelegate
from app.helpers import resource_path
from app.colors import Colors


class OpenOrders(BaseTableView):
    """Extended TableView."""

    def __init__(self, parent=None, *args):
        super(OpenOrders, self).__init__()
        self.my_model = FilterModel(self)
        self.parent = parent

    def redraw(self):
        """Redraw table model without data having changed. Useful for
        models that are displayed via custom item delegates, that display
        data dynamically."""
        
        self.my_model.layoutAboutToBeChanged.emit()
        self.my_model.layoutChanged.emit()

    def set_df(self):
        return app.mw.user_data.create_open_orders_df()


    # TODO: This should be done somewhere else. Think of this when refactoring user_data
    def query_update(self):
        """Update the model by querying the api. This is done in situations where the websocket
        is not working properly."""
        print("OPEN ORDERS QUERY UPDATE")
        app.mw.user_data.initial_open_orders()

        self.my_model.update(self.set_df())
        # self.update()

    def cell_clicked(self, index):
        """Change pair or cancel order"""

        # cancel was clicked
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

        # pair was clicked
        elif index.column() == 1:
            pair = index.data()
            coin = pair.replace("BTC", "")
            self.mw.gui_mgr.change_to(coin)

    def set_widths(self):
        for i in range(4):
            self.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Fixed)

        self.setColumnWidth(0, 130)
        self.setColumnWidth(1, 130)
        self.setColumnWidth(2, 55)
        self.setColumnWidth(3, 55)

    def set_delegates(self):
        super().set_delegates()
        self.setItemDelegateForColumn(0, DateDelegate(self))
        self.setItemDelegateForColumn(1, PairDelegate(self))
        self.setItemDelegateForColumn(3, BuySellDelegete(self))
        self.setItemDelegateForColumn(4, RoundFloatDelegate(self))
        self.setItemDelegateForColumn(5, RoundAssetDelegate(self, 1))
        self.setItemDelegateForColumn(6, FilledPercentDelegate(self))
        self.setItemDelegateForColumn(7, RoundFloatDelegate(self, 8))
        self.setItemDelegateForColumn(9, HoverDelegate(self, Colors.color_pink, Colors.white))
        self.setItemDelegateForColumn(10, FillCalcDelegate(self))


class HistoryModel(FilterModel):
    """HistoryModel extends FilterModel and adds additional filter
    capabilities to filter trades by date."""

    def time_in_ms(self):
        hour = 60 * 60000
        return {1: 24 * hour, 2: 168 * hour, 3: 720 * hour, 4: 2160 * hour, 5: 8640 * hour}

    def set_filter(self, *args):
        searchText = app.mw.coinindex_filter.text()
        cb_index = app.mw.cb_history_time.currentIndex()

        
        if cb_index == 0:
            consider_timeframes = False
            ms_time_period = 0
        else:
            consider_timeframes = True
            ms_time_period = self.time_in_ms()[cb_index]
       
        now = datetime.utcnow()
        final_time = int((now - datetime(1970, 1, 1)).total_seconds() * 1000) - ms_time_period

        if searchText:
            for row in range(self.rowCount()):
                correct_coin = False
                correct_date = False
                self.parent.setRowHidden(row, False)

                current_coin = str(self.datatable.iat[row, self.filter_col]).replace("BTC", "")
                current_date = int(self.datatable.iat[row, 0])

                if str(searchText.upper()) in current_coin:
                    correct_coin = True

                if final_time < current_date or not consider_timeframes:
                    correct_date = True

                if correct_coin and correct_date:
                    self.parent.setRowHidden(row, False)
                else:
                    self.parent.setRowHidden(row, True)

        elif consider_timeframes:
            for row in range(self.rowCount()):
                current_date = int(self.datatable.iat[row, 0])

                if final_time > current_date:
                    self.parent.setRowHidden(row, True)
                else:
                    self.parent.setRowHidden(row, False)

        else:
            for row in range(self.rowCount()):
                self.parent.setRowHidden(row, False)


class History(BaseTableView):
    def __init__(self, parent=None):
        super(History, self).__init__()
        self.my_model = HistoryModel(self)
        

    def set_df(self):
        return self.mw.user_data.create_history_df()

    def set_widths(self):
        for i in range(self.my_model.columnCount()):
            self.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

    def cell_clicked(self, index):
        if index.column() == 1:
            pair = index.data()
            coin = pair.replace("BTC", "")
            self.mw.gui_mgr.change_to(coin)

    def set_delegates(self):
        # super().set_delegates()
        self.setItemDelegateForColumn(0, DateDelegate(self))
        self.setItemDelegateForColumn(1, PairDelegate(self))
        self.setItemDelegateForColumn(2, BuySellDelegete(self))
        self.setItemDelegateForColumn(3, RoundFloatDelegate(self))
        self.setItemDelegateForColumn(4, RoundAssetDelegate(self, 1))
        self.setItemDelegateForColumn(5, RoundFloatDelegate(self, 8))


class Holdings(BaseTableView):
    def __init__(self, parent=None, *args):
        super(Holdings, self).__init__()
        self.my_model = FilterModel(self, 0)

    def set_df(self):
        df = self.mw.user_data.create_holdings_df()
        return df

    def cell_clicked(self, index):
        if index.column() == 0:
            pair = index.data()
            if pair != "BTC":
                self.mw.gui_mgr.change_to(pair)

    def set_widths(self):
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.setColumnWidth(0, 130)

    def set_delegates(self):
        super().set_delegates()
        self.setItemDelegateForColumn(0, CoinDelegate(self))
        self.setItemDelegateForColumn(2, RoundAssetDelegate(self, 0, "BTC"))
        self.setItemDelegateForColumn(3, RoundAssetDelegate(self, 0, "BTC"))
        self.setItemDelegateForColumn(4, RoundAssetDelegate(self, 0, "BTC"))
        self.setItemDelegateForColumn(5, RoundFloatDelegate(self))



class Index(BaseTableView):
    def __init__(self, parent=None, *args):
        super(Index, self).__init__()
        self.my_model = FilterModel(self, 0)

        # self.setItemDelegateForColumn(0, PairDelegate(self))
        self.setItemDelegateForColumn(1, RoundFloatDelegate(self, 8, " BTC"))
        # self.setItemDelegateForColumn(2, ChangePercentDelegate(self))
        self.setItemDelegateForColumn(3, RoundFloatDelegate(self, 8, " BTC"))

        # for i in range(4, 7):
        #     self.setItemDelegateForColumn(i, RoundFloatDelegate(self, 3))

        # for i in range(7, 10):
        #     self.setItemDelegateForColumn(i, ChangePercentDelegate(self))



    def set_df(self):
        if self.mw.data.current.index_df is not None:
            return self.mw.data.current.index_df
        # return self.mw.index_data.coin_index

    def set_widths(self):
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.setColumnWidth(0, 130)
        self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        self.setColumnWidth(1, 130)

    def cell_clicked(self, index):
        if index.column() == 0:
            pair = index.data()
            coin = pair.replace("BTC", "")
            self.mw.gui_mgr.change_to(coin)

###########################



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
        if float(index.data()) == 0:
            self.fg_color = Colors.color_lightgrey
        elif float(index.data()) < 25:
            self.fg_color = Colors.color_pink
        elif float(index.data()) < 75:
            self.fg_color = Colors.color_yellow
        else:
            self.fg_color = Colors.color_green

        option.text = '{number:.{digits}f}'.format(number=float(index.data()), digits=2) + "%"


class FillCalcDelegate(BasicDelegate):
    """Delegate that calculates how much the current price has to change to reach the price of the respective order."""

    def initStyleOption(self, option, index):
        model = self.parent.model()
        pair_index = model.index(index.row(), 1)
        pair = model.data(pair_index, QtCore.Qt.DisplayRole)

        difference = float(index.data()) / (float(self.mw.data.tickers[pair]["lastPrice"]) / 100) - 100


        if abs(difference) == 0:
            self.fg_color = Colors.white
        elif abs(difference) <= 1:
            self.fg_color = Colors.color_green
        elif abs(difference) < 10:
            self.fg_color = Colors.color_yellow
        else:
            self.fg_color = Colors.color_pink

        option.text = '{number:.{digits}f}'.format(number=float(difference), digits=2) + "%"


class DateDelegate(BasicDelegate):
    """Basic style delegate"""

    def initStyleOption(self, option, index):
        option.text = str(datetime.fromtimestamp(int(str(index.data())[:-3])).strftime('%d.%m.%y - %H:%M:%S.%f')[:-7])


class RoundFloatDelegate(BasicDelegate):
    """Delegate that rounds a float to the given decimal place.
        Defaults to 8."""
    center = int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

    def __init__(self, parent, round_to=8, suffix="", text_color=Colors.color_lightgrey, align=center):
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
        if pair != "BTC" and pair != "SBTC":
            try:
                assetDecimals = self.mw.data.pairs[pair + self.pairing]["assetDecimals"]
            except TypeError as e:
                print(e)
                print("Pair has no asset decimals", pair)
                assetDecimals = 8
        else:
            assetDecimals = 8

        if not isinstance(assetDecimals, int):
            assetDecimals = 8
        
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

        iconPath = "images/ico/" + index.data().replace("BTC", "") + ".svg"
        rp = resource_path(iconPath)
        if (os.path.isfile(rp)):
            option.icon = QtGui.QIcon(rp)
        else:
            option.icon = QtGui.QIcon(resource_path("images/ico/BTC.svg"))


        option.text = index.data().replace("BTC", "") + " / BTC"

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
        # TODO: Replace with coin missing icon
        icon_path = resource_path("images/ico/" + index.data() + ".svg")
        if not os.path.isfile(icon_path):
            icon_path = resource_path("images/ico/BTC.svg")
        
        option.icon = QtGui.QIcon(icon_path)