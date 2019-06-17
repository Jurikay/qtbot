# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import pandas as pd
import app
from app.colors import Colors
import numpy as np
from collections import OrderedDict

class BaseTableView(QtWidgets.QTableView):

    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.my_model = SortModel(self)
        self.mw = app.mw
        self.df = None
        # self.setSortingEnabled(True)
        self.clicked.connect(self.cell_clicked)
        # self.set_delegates()

    def websocket_update(self):
        if self.my_model.rowCount() == 0:

            # Setup may only be called from main thread
            self.setup()
        else:
            self.update()

    def setup(self):
        print("TABLE SETUP", self.objectName)
        self.update()

        # TODO: Improve
        if self.df is not None:
            self.setModel(self.my_model)
            self.set_default_widths()
            self.set_delegates()
            self.sortByColumn(0, QtCore.Qt.DescendingOrder)
        else:
            print("TABLE SETUP DF == NONE")

    def update(self):
        # self.my_model.layoutAboutToBeChanged.emit()
        self.df = self.set_df()
        # if isinstance(self.df,    pd.DataFrame):
        self.my_model.update(self.df)
        # self.my_model.layoutChanged.emit()

    def set_default_widths(self):
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(30)

        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().setDefaultSectionSize(100)
        self.set_widths()


    def leaveEvent(self, event):
        app.main_app.restoreOverrideCursor()

    def set_widths(self):
        """This must be overwritten."""
        return NotImplementedError


    def set_df(self):
        """This must be overwritten."""
        return NotImplementedError

    def set_delegates(self):
        return
        self.setItemDelegate(BasicDelegate(self))

    # def cell_clicked(self, index):
    #     """This should be overwritten."""
    #     pass


#################################################################
# BaseTableModel
#################################################################

class DictTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mw = app.mw
        self.headers = ["price", "volume"]

        self.data_dict = {"BTC": {"price": 0.001, "volume": 3, "symbol": "BTC"}}

        self.sorted_dict = OrderedDict(sorted(self.data_dict.items(), key=lambda x: x[1]['volume'], reverse=False))
        self.items = list(self.sorted_dict.items())


        # store sort order and col
        self.order_col = 0
        self.order_dir = QtCore.Qt.AscendingOrder
    
    def headerData(self, p_int, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                print("ITEMS", self.items)
                return self.headerAssignment(p_int)

    def headerAssignment(self, idx):
        headerData = {0: "price", 1: "volume"}
        return headerData[idx]

    def rowCount(self, parent=None):
        return len(self.sorted_dict.keys())

    def columnCount(self, parent=None):
        return len(self.items[0])

    def sort(self, sort_col, order=QtCore.Qt.AscendingOrder):
        self.order_col = sort_col
        self.order_dir = order
        self.layoutAboutToBeChanged.emit()

        col = self.headerAssignment(sort_col)
        order_dir = True
        if order == QtCore.Qt.AscendingOrder:
            order_dir = False
        # else:
        #     oorder_dir = True


        self.sorted_dict = OrderedDict(sorted(self.data_dict.items(), key=lambda x: x[1][col], reverse=order_dir))


        self.layoutChanged.emit()
        
        

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                # return self._data[index.row(), index.column()]

                col = self.headerAssignment(index.column())
                data = self.sorted_dict[index.row()][1][self.headerAssignment(index.column())]
                return data

        return None

    def update(self, dataIn):
        """Pass a dict of dicts to update
        Update modeldata and redraw view."""
        # self.layoutAboutToBeChanged.emit()
        col = self.headerAssignment(self.order_col)

        self.data_dict = dataIn
        self.items = list(self.sorted_dict.items())
        self.sort(self.order_col, self.order_dir)



class NumpyTableModel(QtCore.QAbstractTableModel):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mw = app.mw
        self.datatable = pd.DataFrame()
        self._data = np.array(self.datatable)
        self._cols = 0
        self.r, self.c = np.shape(self._data)


        self.order_col = 0
        self.order_dir = QtCore.Qt.AscendingOrder

    def rowCount(self, parent=None):
        return self.r

    def columnCount(self, parent=None):
        return self.c
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return self._data[index.row(), index.column()]
        return None


    def headerData(self, p_int, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._cols[p_int]
            elif orientation == QtCore.Qt.Vertical:
                return p_int
        return None

    def update(self, dataIn):
        """Update modeldata and redraw view."""
        # self.layoutAboutToBeChanged.emit()
        self.datatable = dataIn

        self.sort(self.order_col, self.order_dir)

        self._data = np.array(self.datatable)
        try:
            self._cols = dataIn.columns
        except AttributeError:
            self._cols = 0
        
        self.r, self.c = np.shape(self._data)

        
        # self.layoutChanged.emit()

    def sort(self, sort_col, order=QtCore.Qt.AscendingOrder):
        self.layoutAboutToBeChanged.emit()

        # self.layoutAboutToBeChanged.emit()
        self.datatable = self.datatable.sort_values(self.datatable.columns[sort_col], ascending=not order)

        self.layoutChanged.emit()
        self.order_col = sort_col
        self.order_dir = order

        # self._data.sort(axis=sort_col)
        # self.layoutChanged.emit()


class BaseTableModel(QtCore.QAbstractTableModel):
    """TableModel that holds data from a pandas dataframe."""
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mw = app.mw
        self.datatable = None


    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Return header data based on Qt.DisplayRole"""
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                # TODO: Verify try except here
                try:
                    return self.datatable.columns[section]
                except (IndexError, AttributeError) as e:
                    print("HEADERDATA ERROR:", e)
                    return

    def update(self, dataIn):
        """Update modeldata and redraw view."""
        self.layoutAboutToBeChanged.emit()
        self.datatable = dataIn
        self.layoutChanged.emit()


    def rowCount(self, parent=QtCore.QModelIndex()):
        """Return pandas row count."""
        if isinstance(self.datatable, pd.DataFrame):
            return len(self.datatable.index)
        return 0


    def columnCount(self, parent=QtCore.QModelIndex()):
        """Return pandas column count."""
        if isinstance(self.datatable, pd.DataFrame):
            return len(self.datatable.columns.values)
        return 0


    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Return cell data."""
        if role == QtCore.Qt.DisplayRole:
            if index.isValid():
                return str(self.datatable.iat[index.row(), index.column()])


class SortModel(BaseTableModel):
    """Sortable BaseTableModel."""
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.order_col = 0
        self.order_dir = True

    def reindex(self):
        self.datatable = self.datatable.reset_index(drop=True)

    def sort(self, sort_col, sort_order):
        """Sort table by given column number sort_col in the given direction sort_order"""

        if isinstance(self.datatable, pd.DataFrame) and self.rowCount() > 1:

            self.layoutAboutToBeChanged.emit()
            # Sort the table
            self.datatable = self.datatable.sort_values(self.datatable.columns[sort_col], ascending=not sort_order)

            # Reindex the table; This is only needed for the coin selector model.
            # TODO: Move to subclass/ Verify performance is ok
            # self.datatable = self.datatable.reset_index(drop=True)
            self.reindex()

            # save sort_order dir and order col
            self.order_col = sort_col
            self.order_dir = sort_order

            self.layoutChanged.emit()


    def update(self, dataIn):
        self.datatable = dataIn
        self.sort(self.order_col, self.order_dir)


class FilterModel(SortModel):
    def __init__(self, parent=None, filter_col=1):
        super().__init__(parent=parent)
        self.searchText = None
        self.parent = parent
        self.filter_col = filter_col

        self.old_search_text = None

    # def redraw(self):
    #     """Redraw table model without data having changed. Useful for
    #     models that are displayed via custom item delegates, that display
    #     data dynamically."""

    #     self.layoutAboutToBeChanged.emit()
    #     self.layoutChanged.emit()


    def set_current_coin(self, state):
        # TODO: Think of moving somewhere else.
        if state == 2:
            self.old_search_text = app.mw.coinindex_filter.text()
            app.mw.coinindex_filter.setText(app.mw.data.current.coin)
            app.mw.coinindex_filter.setEnabled(False)
            self.mw.coinindex_filter.setStyleSheet("color: grey")

        elif state == 0:
            app.mw.coinindex_filter.setText(self.old_search_text)
            app.mw.coinindex_filter.setEnabled(True)
            self.mw.coinindex_filter.setStyleSheet("color: white")

    def set_filter(self):
        searchText = app.mw.coinindex_filter.text()
        self.searchText = searchText

        if searchText and not searchText == "":
            for row in range(self.rowCount()):
                self.parent.setRowHidden(row, False)

                current_coin = str(self.datatable.iat[row, self.filter_col]).replace("BTC", "")

                if str(searchText.upper()) in current_coin:
                    self.parent.setRowHidden(row, False)
                else:
                    self.parent.setRowHidden(row, True)
        else:
            for row in range(self.rowCount()):
                self.parent.setRowHidden(row, False)

    def reindex(self):
        """Reindexing of base class not needed."""


    def sort(self, sort_col, sort_order):
        """Base sort + apply filter."""
        super().sort(sort_col, sort_order)
        self.set_filter()


class BasicDelegate(QtWidgets.QStyledItemDelegate):
    """Basic StyledItemDelegate implementation"""
    center = int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
    left = int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignLeft)
    right = int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignRight)

    def __init__(self, parent, text_color=Colors.color_lightgrey, align=center):
        self.parent = parent
        self.fg_color = text_color
        self.font = QtGui.QFont()
        self.mw = app.mw
        self.align = align
        super(BasicDelegate, self).__init__(parent)


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