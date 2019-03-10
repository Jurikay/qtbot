# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from app.widgets.base_table_setup import BaseTableView, BasicDelegate, SortFilterModel, RoundFloatDelegate, PairDelegate, ChangePercentDelegate, BaseTableModel

import app
import pandas as pd


class CoinSelector(QtWidgets.QComboBox):
    def __init__(self, *args, **kwargs):
        QtWidgets.QComboBox.__init__(self, *args, **kwargs)

        self.mw = app.mw
        self.model = None
        self.completer = None
        self.activated.connect(self.select_coin)
        # self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setEditable(True)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setIconSize(QtCore.QSize(25, 25))

        self.model = SelectorModel()
        self.setModel(self.model)
        self.setModelColumn(0)

        self.lineEdit().setReadOnly(False)


    def paintEvent(self, event):
        """Reimplemented."""
        painter = QtWidgets.QStylePainter(self)
        option = QtWidgets.QStyleOptionComboBox()
        self.initStyleOption(option)

        ctext = option.currentText[:-3]
        
        option.currentText = ctext
        option.currentIcon = QtGui.QIcon("images/ico/" + ctext + ".svg")
        painter.drawComplexControl(QtWidgets.QStyle.CC_ComboBox, option)

        painter.drawControl(QtWidgets.QStyle.CE_ComboBoxLabel, option)



    def select_coin(self, cindex):
        # print("SC KW", kw)
        print("select coin")
        pair = self.model.index(cindex, 0).data()
        print(pair)
        # self.setCurrentText(pair)
        # self.setCurrentIndex(4)
        # self.update()
        # self.setEditText(pair)
        print("INDEX:", self.currentIndex())
        # self.lineEdit().setText(pair)

    def update(self):
        # print("TDF", self.mw.data.current.ticker_df)
        self.model.update(self.mw.data.current.ticker_df)
        # self.completer.setModel(self.model)
        # self.setCompleter(self.completer)

    def setup(self):
        


        self.view = SelectorView()
        self.view.setFocusPolicy(QtCore.Qt.NoFocus)
        
        # self.view.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setView(self.view)

        self.completer = MyCompleter()
        self.completer.setModel(self.model)
        self.completer.setCompletionColumn(0)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer.setCompletionMode(0)
        
        self.completer.setModelSorting(0)
        self.completer.setMaxVisibleItems(10)
        self.completer.setFilterMode(QtCore.Qt.MatchStartsWith)
        # self.completer.popup().setItemDelegate(PairDelegate(self))
        self.setCompleter(self.completer)
        


        self.model.update(self.mw.data.current.ticker_df)
        # self.view().window.setFixedWidth(1000)

class MyCompleter(QtWidgets.QCompleter):
    def __init__(self, parent=None):
        super(MyCompleter, self).__init__(parent)
        # self.delegate = PairDelegate(self)
        # self.popup().setItemDelegate(self.delegate)


class SelectorModel(BaseTableModel):
    def __init__(self, *args, **kwargs):
        QtCore.QAbstractTableModel.__init__(self, *args, **kwargs)
        self.datatable = None
        self.order_col = 0
        self.order_dir = 0
        self.searchText = ""

    # def update(self, dataIn):
    #     self.modelAboutToBeReset.emit()
    #     self.datatable = dataIn
    #     self.modelReset.emit()

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


class SelectorView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)

        # self.setUniformRowHeights(True)
        self.mw = app.mw
        # self.setItemDelegate(BasicDelegate(self))
        self.setItemDelegateForColumn(0, PairDelegate(self))
        self.setItemDelegateForColumn(1, RoundFloatDelegate(self, 8, " BTC"))
        self.setItemDelegateForColumn(2, ChangePercentDelegate(self))
        self.setItemDelegateForColumn(3, RoundFloatDelegate(self, 2, " BTC"))
        
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setMouseTracking(False)
        self.setTabletTracking(False)
        self.viewport().setMouseTracking(False)


        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        # setSizePolicy(QSizePolicy::MinimumExpanding, QSizePolicy::Preferred)
        ld_width = self.width() * 2
        
        print("LD W", ld_width)
        # print(self.parent)
        self.setMinimumWidth(500)
        self.set_widths()
        self.setShowGrid(False)
        # self.setFocusPolicy(QtCore.Qt.NoFocus)
        # self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)


    def set_widths(self):
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().setDefaultSectionSize(100)