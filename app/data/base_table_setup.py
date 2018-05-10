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
            self.my_model = BaseTableModel(self)
            self.data_dict = None
            self.df = None
            self.mw = app.mw
            # self.setItemDelegate(AsksDelegate(self))
            # self.proxy_model = QtCore.QSortFilterProxyModel()
            self.setSortingEnabled(True)
            self.clicked.connect(self.cell_clicked)
            self.max_order = 0
            self.data = None
            self.has_data = False
            self.color_background = False
            # 
            self.has_proxy = False


    # move out of main tableview


    def setup(self):
        self.update()

        if self.my_model.rowCount():
            print("BASE TABLE SETUP")
            if self.has_proxy:
                self.proxy_model.setSourceModel(self.my_model)
                self.setModel(self.proxy_model)
            else:
                self.setModel(self.my_model)

            self.set_widths()
            self.sortByColumn(0, QtCore.Qt.DescendingOrder)

    def update(self):
        print("BASE TABLE UPDATE")
        self.my_model.modelAboutToBeReset.emit()
        # set_df has to be extended
        self.df = self.set_df()
        self.my_model.update(self.df)
        self.my_model.modelReset.emit()

    def set_widths(self):
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(15)

        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setDefaultSectionSize(75)

    def set_df(self):
        print("set empty df")
        """This should be overwritten."""
        return pd.DataFrame

    def cell_clicked(self, click):
        """This should be overwritten."""
        pass


class BackgroundTable(BaseTableView):
    """Extended TableView that draws a colored background."""

    def __init__(self, parent=None, *args):
        super(BackgroundTable, self).__init__()

    def paintEvent(self, event):
        """Custom paint event to draw colored background to
        indicate order size."""

        if self.color_background:
            if self.has_data is True:
                row_count = self.my_model.rowCount()
                for row in range(row_count):
                    rowY = self.rowViewportPosition(row)
                    rowH = self.rowHeight(row)

                    # Create the painter
                    painter = QtGui.QPainter(self.viewport())

                    value = self.df.iloc[row, 3]
                    percentage = value / self.max_order
                    total_width = self.horizontalHeader().width()

                    painter.save()
                    bg_rect = QtCore.QRect(0, rowY, (percentage * total_width), rowH)
                    painter.setBrush(QtGui.QColor(self.bg_color))
                    painter.setPen(QtGui.QColor("#20262b"))
                    painter.drawRect(bg_rect)
                    painter.restore()

            super(BaseTableView, self).paintEvent(event)
        else:
            super(BaseTableView, self).paintEvent(event)


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


class SortFilterModel(QtCore.QAbstractTableModel):
    """TableModel that receives it's data from a pandas DataFrame."""
    def __init__(self, parent=None, *args):
        super(SortFilterModel, self).__init__()

    def setFilter(self, searchText=None):
        self.searchText = searchText
        if searchText:
            for row in range(self.rowCount()):
                self.mw.test_table_view.setRowHidden(row, False)

                if str(searchText.upper()) in str(self.datatable.iloc[row, 0]).replace("BTC", ""):
                    self.mw.test_table_view.setRowHidden(row, False)
                else:
                    self.mw.test_table_view.setRowHidden(row, True)

        else:
            for row in range(self.rowCount()):
                self.mw.test_table_view.setRowHidden(row, False)


    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        if Ncol >= 0:
            self.modelAboutToBeReset.emit()
            self.datatable = self.datatable.sort_values(self.datatable.columns[Ncol], ascending=not order)

            # save order dir and order col
            self.order_col = Ncol
            self.order_dir = order

            if self.searchText:
                self.setFilter(searchText=self.searchText)

            self.modelReset.emit()


#################################################################
# Cell Delegates
#################################################################


class BasicDelegate(QtWidgets.QStyledItemDelegate):
    """Basic style delegate"""

    def __init__(self, parent, text_color):
        super(BasicDelegate, self).__init__(parent)
        self.parent = parent
        self.mw = app.mw
        self.fg_color = text_color


    def initStyleOption(self, option, index):
        option.text = index.data()


    def paint(self, painter, option, index):
        painter.save()
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        font = QtGui.QFont()
        painter.setFont(font)
        painter.setPen(QtGui.QColor(self.fg_color))
        align_center = int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        painter.drawText(option.rect, align_center, options.text)
        painter.restore()


class PairDelegate(QtWidgets.QStyledItemDelegate):
    """Class to define the style of index values."""

    def __init__(self, parent):
        super(PairDelegate, self).__init__(parent)
        self.parent = parent
        self.mw = app.mw

    def initStyleOption(self, option, index):
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

        icon = QtGui.QIcon("images/ico/" + index.data().replace("BTC", "") + ".svg")
        iconRect = QtCore.QRect(option.rect.left() + 15 - option.rect.height(),
                                option.rect.top(),
                                option.rect.height(),
                                option.rect.height())

        textRect = QtCore.QRect(option.rect.left() + 25 + iconRect.width() - option.rect.height(),
                                option.rect.top(),
                                option.rect.width(),
                                option.rect.height())


        icon.paint(painter, iconRect, QtCore.Qt.AlignLeft)

        if option.state & QtWidgets.QStyle.State_MouseOver:
            painter.setPen(QtGui.QColor(Colors.color_yellow))
            font.setBold(True)
            painter.setFont(font)
        else:
            painter.setPen(QtGui.QColor(Colors.color_lightgrey))

        painter.drawText(textRect, align_left, options.text)
        painter.restore()


#################################################################
# Implementations
#################################################################


class TestHist(BaseTableView):
    """Extended TableView that draws a colored background."""

    def __init__(self, parent=None, *args):
        super(TestHist, self).__init__()
        # PairDelegate = 
        self.setItemDelegateForColumn(1, PairDelegate(self))
        # self.setItemDelegateForColumn(2, BasicDelegate)


    def set_df(self):
        print("set true df")
        return self.mw.user_data.create_dataframe()
