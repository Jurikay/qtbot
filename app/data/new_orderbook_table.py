# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import app
import pandas as pd
# from datetime import datetime
from app.colors import Colors
# from app.init import val


class OrderbookTable(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.my_model = AsksModel(self)
        self.data_dict = None
        self.df = None
        self.mw = app.mw
        self.setItemDelegate(AsksDelegate(self))
        # self.proxy_model = QtCore.QSortFilterProxyModel()
        self.setSortingEnabled(True)
        self.clicked.connect(self.cell_clicked)
        self.max_order = 0
        self.data = None
        self.has_data = False

    def paintEvent(self, event):

        if self.has_data is True:
            row_count = self.my_model.rowCount()
            for row in range(row_count):
                rowY = self.rowViewportPosition(row)
                rowH = self.rowHeight(row)
                # print(row, rowY, rowH)
                
                # Create the painter
                painter = QtGui.QPainter(self.viewport())


                value = self.df.iloc[row, 3]
                percentage = value / self.max_order
                total_width = self.horizontalHeader().width()

                painter.save()
                my_rect = QtCore.QRect(0, rowY, (percentage * total_width), rowH)

                # bg_brush = QtGui.QBrush(QtGui.QColor(self.bg_color))
                painter.setBrush(QtGui.QColor(self.bg_color))
                painter.setPen(QtGui.QColor("#20262b"))

                painter.drawRect(my_rect)
                painter.restore()
    
        super(OrderbookTable, self).paintEvent(event)


    def setup(self):
        self.update()

        self.setModel(self.my_model)
        # self.proxy_model.setSourceModel(self.my_model)

        self.set_widths()

        self.sortByColumn(0, QtCore.Qt.DescendingOrder)


    def update(self, payload=None):
        # print("asks update")
        self.my_model.modelAboutToBeReset.emit()
        # self.df = pd.DataFrame(val["asks"].copy())

        self.df = self.create_dataframe(self.data)

        self.my_model.update(self.df)

        self.my_model.modelReset.emit()


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


    def set_widths(self):
        self.horizontalHeader().setDefaultSectionSize(20)
        # self.setColumnWidth(0, 1)
        self.setColumnWidth(0, 25)
        # self.setColumnWidth(2, 60)
        # self.setColumnWidth(3, 60)
        self.horizontalHeader().setSortIndicatorShown(False)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(16)
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        for i in range(1, 4):
            self.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

    def cell_clicked(self, index):
        """Change pair or cancel order"""
        # self.update()
        pass


class AsksModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None, *args):
        super(AsksModel, self).__init__()
        self.mw = app.mw
        self.datatable = None
        # self.header_data = ["#", "Price", "Amount", "Total"]

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Set header data."""
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                # return self.header_data[section]
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
            option.text = '{number:.{digits}f}'.format(number=float(index.data()), digits=self.mw.decimals)

        elif index.column() == 2:
            option.text = '{number:.{digits}f}'.format(number=float(index.data()), digits=self.mw.assetDecimals)

        elif index.column() == 3:
            option.text = '{number:.{digits}f}'.format(number=float(index.data()), digits=3) + " BTC"

        else:
            super(AsksDelegate, self).initStyleOption(option, index)


    def paint(self, painter, option, index):
        """Reimplemented custom paint method."""
        painter.save()
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        font = QtGui.QFont()


        if index.column() == 0:
            painter.setPen(QtGui.QColor("#ffffff"))

            painter.drawText(option.rect, self.center, options.text)

        elif index.column() == 1:
            if option.state & QtWidgets.QStyle.State_MouseOver:
                    painter.setPen(QtGui.QColor(self.parent.highlight))
                    font.setBold(True)
            else:
                painter.setPen(QtGui.QColor(self.parent.color))

        else:
            painter.setPen(QtGui.QColor(Colors.color_lightgrey))


        painter.setFont(font)
        painter.drawText(option.rect, self.center, options.text)

        painter.restore()



class DataAsks(OrderbookTable):
    def __init__(self, *args, **kwargs):
        OrderbookTable.__init__(self, *args, **kwargs)
        self.color = Colors.color_pink
        self.bg_color = "#473043"
        self.highlight = "#ff58a8"
        self.data = "asks"


class DataBids(OrderbookTable):
    def __init__(self, *args, **kwargs):
        OrderbookTable.__init__(self, *args, **kwargs)
        self.color = Colors.color_green
        self.bg_color = "#3b4c37"
        self.highlight = "#aaff00"
        self.data = "bids"
