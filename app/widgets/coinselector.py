# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from app.widgets.base_table_setup import BaseTableView, BasicDelegate, SortFilterModel, RoundFloatDelegate, PairDelegate, ChangePercentDelegate, BaseTableModel, NCoinDelegate, NPriceDelegate

import app
import pandas as pd

from app.helpers import resource_path

class CoinSelector(QtWidgets.QComboBox):
    def __init__(self, *args, **kwargs):
        QtWidgets.QComboBox.__init__(self, *args, **kwargs)

        self.mw = app.mw
        self.model = None
        self.completer = None
        self.activated.connect(self.select_coin)
        # self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setEditable(False)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setIconSize(QtCore.QSize(25, 25))

        self.model = SelectorModel()
        self.setModel(self.model)

        self.setModelColumn(0)
        self.setMouseTracking(False)
        # self.lineEdit().setReadOnly(False)

    # def debugModel(self):
    #     self.setView(self.mw.debugTb)

    def paintEvent(self, event):
        """Reimplemented."""
        painter = QtWidgets.QStylePainter(self)
        option = QtWidgets.QStyleOptionComboBox()
        self.initStyleOption(option)

        ctext = option.currentText[:-3]
        
        option.currentText = ctext
        option.currentIcon = QtGui.QIcon(resource_path("images/ico/" + ctext + ".svg"))
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

    #     super().showPopup()

    # def hidePopup(self):
    #     print("PAIR", self.mw.data.current.symbol)
    #     find = self.findText(self.mw.data.current.symbol, flags=QtCore.Qt.MatchStartsWith)
    #     self.setCurrentIndex(find)
    #     return super().hidePopup()

    def select_coin(self, cindex):
        self.mw.gui_manager.change_pair()
        self.clearFocus()  # TODO: Verify
        

    def update(self):
        self.model.update(self.mw.data.current.ticker_df)
        # TODO: clean up this mess
        # This is a work around. Since the model of the coin
        # selector qcombobox is sortable, the current selection
        # is set again after each update to circumvent it changing.

        # Maybe:
        # change ticker dataframe to an int index.
        # on sort, reset index; get row index w/o "idx" column

        df = self.model.datatable
        # if isinstance(df, pd.DataFrame):
        #     pass
        # else:
        #     print("CANCEL")
        #     return
        pair = self.mw.data.current.pair

        if not pair:
            pair = "BNBBTC"

        try: 
            # row = df.loc[df['Coin'] == pair].index()
            row = df.index[df["Coin"] == pair][0]
            
            # print("matching row:", self.model.datatable.iloc[row])
            self.setCurrentIndex(row)
            self.view.set_widths()

        except Exception as e:
            print("ERROR", e)

    def setup(self):
        self.view = SelectorView()
        self.view.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setView(self.view)

        self.model.update(self.mw.data.current.ticker_df)
        self.setModelColumn(0)

        # self.view().window.setFixedWidth(1000)


class SelectorModel(SortFilterModel):
    def __init__(self, *args, **kwargs):
        QtCore.QAbstractTableModel.__init__(self, *args, **kwargs)
        self.datatable = None
        self.order_col = 0
        self.order_dir = 0
        self.searchText = ""
    # def rowCount(self, parent=QtCore.QModelIndex()):
    #     if isinstance(self.df, pd.DataFrame):
    #         return len(self.df.index)
    #     return 0

    # def columnCount(self, parent=QtCore.QModelIndex()):
    #     if isinstance(self.df, pd.DataFrame):
    #         return len(self.df.columns.values)
    #     return 0

    # def data(self, index, role):
    #     if role == QtCore.Qt.DisplayRole:
    #         if index.isValid():
    #             return str(self.datatable.iloc[index.row(), index.column()])
    #     elif role == QtCore.Qt.UserRole:
    #         return "asdasd"

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return str(self.datatable.iloc[index.row(), index.column()])

class SelectorView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.setObjectName("coin_selector_view")
        self.setItemDelegateForColumn(0, NCoinDelegate(self))
        
        self.setItemDelegateForColumn(1, NPriceDelegate(self))
        # self.setItemDelegateForColumn(1, RoundFloatDelegate(self, 8, " BTC"))
        self.setItemDelegateForColumn(2, ChangePercentDelegate(self))
        self.setItemDelegateForColumn(3, RoundFloatDelegate(self, 2, " BTC"))
        
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSortingEnabled(True)
        self.setMouseTracking(False)
        self.setTabletTracking(False)
        self.viewport().setMouseTracking(False)
        # self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        self.setMinimumWidth(500)
        self.setShowGrid(False)

        # Disable displaying header text in bold
        self.horizontalHeader().setHighlightSections(False)


    def set_widths(self):
        # for i in range(4):
        #     self.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Fixed)
        # self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # self.horizontalHeader().setDefaultSectionSize(100)
        # self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)

        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        # self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        # self.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        self.setColumnWidth(0, 350)
        self.setColumnWidth(1, 200)
        self.setColumnWidth(2, 0)
        self.setColumnWidth(3, 400)