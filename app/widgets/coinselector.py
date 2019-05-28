# pylint: disable=unsubscriptable-object

# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from app.widgets.table_implementations import RoundFloatDelegate, ChangePercentDelegate


from app.widgets.base_table import SortModel
from app.colors import Colors

import os

import app
import pandas as pd

from app.helpers import resource_path

class CoinSelector(QtWidgets.QComboBox):
    def __init__(self, *args, **kwargs):
        QtWidgets.QComboBox.__init__(self, *args, **kwargs)

        self.mw = app.mw
        self.model = SortModel()
        self.setModel(self.model)
        self.completed_setup = False
        self.basic_setup()

    def basic_setup(self):
        self.activated.connect(self.select_coin)
        self.setEditable(False)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setIconSize(QtCore.QSize(25, 25))
        self.setModelColumn(0)
        self.setMouseTracking(False)


    def paintEvent(self, event):
        """Reimplemented."""
        painter = QtWidgets.QStylePainter(self)
        option = QtWidgets.QStyleOptionComboBox()
        self.initStyleOption(option)

        ctext = option.currentText[:-3]

        option.currentText = ctext
        icon_path = resource_path("images/ico/" + ctext + ".svg")
        if not os.path.isfile(icon_path):
            icon_path = resource_path("images/ico/BTC.svg")

        option.currentIcon = QtGui.QIcon(icon_path)
        painter.drawComplexControl(QtWidgets.QStyle.CC_ComboBox, option)

        painter.drawControl(QtWidgets.QStyle.CE_ComboBoxLabel, option)

    # def showPopup(self):
    #     """Reimplemented."""
    #     self.setCurrentIndex(-1)

    #     print("SHOWING POPUP")
    #     # self.setCurrentIndex(-1)
    #     # self.setFocus(-1)
    #     # self.setCurrentText("Lel")
    #     # emit the new signal
    #     # self.popupAboutToBeShown.emit()
    #     # call the base method now to display the popup
        # self.view.setFocus(-1)
        # super().showPopup()

    # def hidePopup(self):
    #     print("PAIR", self.mw.data.current.symbol)
    #     find = self.findText(self.mw.data.current.symbol, flags=QtCore.Qt.MatchStartsWith)
    #     self.setCurrentIndex(find)
    #     return super().hidePopup()

    def select_coin(self, cindex):
        self.mw.gui_mgr.change_pair()

        # self.clearFocus()  # TODO: Verify


    def update(self):
        self.model.update(self.mw.data.current.ticker_df)
        # TODO: clean up this mess
        # This is a work around. Since the model of the coin
        # selector qcombobox is sortable, the current selection
        # is set again after each update to circumvent it changing.

        # Maybe:
        # change ticker dataframe to an int index.
        # on sort, reset index; get row index w/o "idx" column

        df: pd.DataFrame = self.model.datatable
        if isinstance(df, pd.DataFrame):
            pass
        else:
            print("CANCEL")
            return


        pair = self.mw.data.current.pair

        # if not pair:
        #     pair = "BNBBTC"

        row = df.index[df["Coin"] == pair][0]
        self.setCurrentIndex(row)

        # This has to be done once but after the model received it's data.
        if not self.completed_setup:
            self.view.set_widths()
            self.completed_setup = True

    def setup(self):
        print("selector setup")
        self.view = SelectorView()
        self.view.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setView(self.view)

        self.model.update(self.mw.data.current.ticker_df)
        self.setModelColumn(0)
        self.update()

class SelectorView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.setObjectName("coin_selector_view")
        self.set_delegates()
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSortingEnabled(True)
        self.setMouseTracking(False)
        self.setTabletTracking(False)
        self.viewport().setMouseTracking(False)
        # self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        self.setMinimumWidth(500)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        # Disable displaying header text in bold
        self.horizontalHeader().setHighlightSections(False)


    def set_delegates(self):
        self.setItemDelegateForColumn(0, NCoinDelegate(self))
        self.setItemDelegateForColumn(1, NPriceDelegate(self))
        self.setItemDelegateForColumn(2, ChangePercentDelegate(self))
        self.setItemDelegateForColumn(3, RoundFloatDelegate(self, 2, " BTC", int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignRight)))

    def set_widths(self):
        print("COIN SELECTOR SET WIDTHS")

        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)
        # self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        # self.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        self.setColumnWidth(0, 100)
        self.setColumnWidth(1, 165)
        self.setColumnWidth(2, 100)
        self.setColumnWidth(3, 120)


class NPriceDelegate(QtWidgets.QStyledItemDelegate):
    """Delegate that colors satoshi in a BTC value."""  # TODO: Find better name
    # def initStyleOption(self, option, index):
    #     option.text = '{number:,.{digits}f}'.format(number=float(index.data()), digits=8)
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def paint(self, painter, option, index):

        option.text = '{number:,.{digits}f}'.format(number=float(index.data()), digits=8)
        options = QtWidgets.QStyleOptionViewItem(option)

        font = app.mw.coin_selector.view.property("font")
        metrics = QtGui.QFontMetrics(font)

        # TODO: Find way to correctly center text horizontally
        # Move delegates to separate file
        x = option.rect.left() + 25
        y = option.rect.center().y() + 6
        painter.save()

        color_text = False

        char = None

        for char in options.text:
            if color_text is False and char == "0" or char == "." :
                painter.setPen(QtGui.QColor(Colors.color_lightgrey))

            else:
                painter.setPen(QtGui.QColor(Colors.white))
                color_text = True

            painter.drawText(x, y, char)
            # x += metrics.width(c)
            x += metrics.horizontalAdvance(char)

        if char:
            x += metrics.horizontalAdvance(char)

        # Display dollar value with two decimal places
        dollar_value = round(float(options.text) * float(app.mw.data.btc_price["lastPrice"]), 2)
        
        # TODO: Verify hardcoded value
        # If dollar value is below 0.02, display 4 decimal places
        if dollar_value < 0.02:
            dollar_value = round(float(options.text) * float(app.mw.data.btc_price["lastPrice"]), 4)

        painter.setPen(QtGui.QColor(Colors.color_lightgrey))
        painter.drawText(x, y, str(dollar_value) + "$")
        painter.restore()


# refactor (used by coin_selector view)
class NCoinDelegate(QtWidgets.QStyledItemDelegate):

    @staticmethod
    def initStyleOption(option, index):
        """Set style options based on index column."""

        iconPath = "images/ico/" + index.data().replace("BTC", "") + ".svg"
        rp = resource_path(iconPath)
        if os.path.isfile(rp):
            option.icon = QtGui.QIcon(rp)
        else:
            option.icon = QtGui.QIcon(resource_path("images/ico/BTC.svg"))


        option.text = index.data().replace("BTC", "")

    def paint(self, painter, option, index):
        """Reimplemented custom paint method."""
 
        # alignment = int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        align_left = int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        painter.save()
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        font = QtGui.QFont()


        iconRect = QtCore.QRect(option.rect.left() + 6,
                                option.rect.top(),
                                # icon is quadratic; set width to it's height.
                                option.rect.height(),
                                option.rect.height())

        textRect = QtCore.QRect(option.rect.left() + iconRect.width() + 12,
                                option.rect.top(),
                                # subtract previously added icon width.
                                option.rect.width() - iconRect.width(),
                                option.rect.height())



        if option.state & QtWidgets.QStyle.State_Selected:
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