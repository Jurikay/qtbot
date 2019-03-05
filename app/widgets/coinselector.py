# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from app.widgets.base_table_setup import BaseTableView, BasicDelegate, SortFilterModel, RoundFloatDelegate, PairDelegate, ChangePercentDelegate

import app
import pandas as pd


class CoinSelector(QtWidgets.QComboBox):
    def __init__(self, *args, **kwargs):
        QtWidgets.QComboBox.__init__(self, *args, **kwargs)

        self.mw = app.mw
        self.model = None
        # self.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
    
    # def mousePressEvent(self, event):
    #     print("MOUSE!", event)
        # self.mousePressed.emit(event)
    def update(self):
        self.model.update(self.mw.data.current.ticker_df)

    def setup(self):
        self.model = SelectorModel()
        self.setModel(self.model)
        self.setView(SelectorView())
        self.model.update(self.mw.data.current.ticker_df)
        # self.view().window.setFixedWidth(1000)

class SelectorModel(SortFilterModel):
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
    #             return str(self.df.iloc[index.row(), index.column()])


class SelectorView(BaseTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTreeView.__init__(self, *args, **kwargs)

        # self.setUniformRowHeights(True)
        self.mw = app.mw
        # self.setItemDelegate(BasicDelegate(self))
        self.setItemDelegateForColumn(0, PairDelegate(self))
        self.setItemDelegateForColumn(1, RoundFloatDelegate(self, 8, " BTC"))
        self.setItemDelegateForColumn(2, ChangePercentDelegate(self))
        self.setItemDelegateForColumn(3, RoundFloatDelegate(self, 2, " BTC"))
        
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        # self.setSelectionBehavior(QtWidgets.QAbstractItemView.NoSelection)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setMouseTracking(True)

        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        # setSizePolicy(QSizePolicy::MinimumExpanding, QSizePolicy::Preferred)
        ld_width = self.width() * 2
        
        print("LD W", ld_width)
        # print(self.parent)
        self.setMinimumWidth(500)
        self.set_widths()

    def set_widths(self):
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().setDefaultSectionSize(100)