# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import app
import pandas as pd
from datetime import datetime
from app.colors import Colors
from app.init import val


class DataAsks(QtWidgets.QTableView):
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
        self.max_ask = 0

    def paintEvent(self, event):
        print("PAINT EVENT")
        super(DataAsks, self).paintEvent(event)
        for row in range(self.my_model.rowCount()):
            rowY = self.rowViewportPosition(row)
            rowH = self.rowHeight(row)
            print(rowY, rowH)

    def setup(self):
        try:
            self.update()
        except (AttributeError, KeyError) as e:
            print("UPDATE ERROR!", e)
            return


        self.setModel(self.my_model)
        # self.proxy_model.setSourceModel(self.my_model)

        self.set_widths()

        self.sortByColumn(0, QtCore.Qt.DescendingOrder)


    def update(self, payload=None):
        print("asks update")
        self.my_model.modelAboutToBeReset.emit()
        # self.df = pd.DataFrame(val["asks"].copy())

        self.df = self.create_dataframe(val["asks"])

        self.my_model.update(self.df)

        self.my_model.modelReset.emit()


    def create_dataframe(self, data):
        df = pd.DataFrame(val["asks"])
        
        df.columns = ["Price", "Amount", "Total"]
        cols = df.columns
        df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
        total = df.Price * df.Amount
        df["Total"] = total
        df[""] = ""
        df['#'] = df.index + 1
        df = df[["", "#", "Price", "Amount", "Total"]]

        # reverse asks
        df = df.reindex(index=df.index[::-1])
        maxval = df["Total"].max()
        self.max_ask = maxval
        return df


    def set_widths(self):
        self.horizontalHeader().setDefaultSectionSize(20)
        self.setColumnWidth(0, 1)
        self.setColumnWidth(1, 25)
        # self.setColumnWidth(2, 60)
        # self.setColumnWidth(3, 60)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(16)
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        for i in range(2, 5):
            self.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

    def cell_clicked(self, index):
        """Change pair or cancel order"""
        self.update()


class AsksModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None, *args):
        super(AsksModel, self).__init__()
        self.mw = app.mw
        self.datatable = None
        self.header_data = ["#", "Price", "Amount", "Total"]

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Set header data."""
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                # return self.header_data[section]
                return self.datatable.columns[section]


    def update(self, dataIn):
        self.datatable = dataIn


    def rowCount(self, parent=QtCore.QModelIndex()):
        if not self.datatable.empty:
            return len(self.datatable.index)
        else:
            return 0

    def columnCount(self, parent=QtCore.QModelIndex()):
        if not self.datatable.empty:
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
        if index.column() == 1:
            option.text = str(index.data()).zfill(2)

        elif index.column() == 2:
            option.text = '{number:.{digits}f}'.format(number=float(index.data()), digits=self.mw.decimals)

        elif index.column() == 3:
            option.text = '{number:.{digits}f}'.format(number=float(index.data()), digits=self.mw.assetDecimals)

        elif index.column() == 4:
            option.text = '{number:.{digits}f}'.format(number=float(index.data()), digits=3) + " BTC"

        else:
            super(AsksDelegate, self).initStyleOption(option, index)



    def paintN(self, painter, option, index):
        """Reimplemented custom paint method."""
        painter.save()
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        if index.column() == 0:
            pass



    def paint(self, painter, option, index):
        """Reimplemented custom paint method."""
        painter.save()
        option.backgroundBrush = QtGui.QBrush(QtCore.Qt.NoBrush)
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        # font = QtGui.QFont()
        options.backgroundBrush = QtGui.QBrush(QtCore.Qt.NoBrush)
        
        if index.column() == 0:
            
            # figure out percentage
            row = index.row()
            value = self.mw.new_asks.df.iloc[row, 4]

            percentage = value / self.mw.new_asks.max_ask
            # print("percentage", percentage)
            # print(value, "/", self.mw.new_asks.max_ask)
            painter.setPen(QtGui.QColor("#20262B"))
            painter.setBrush(QtGui.QColor("#473043"))
            bg_brush = QtGui.QBrush(QtGui.QColor("#473043"))
            total_width = self.mw.new_asks.horizontalHeader().width()

            # percent1 = float(total_width) / 100

            # percent50 = float(self.mw.new_asks.horizontalHeader().width()) / 1.5

            # left = self.mw.new_asks.horizontalHeader().left()
            my_rect = QtCore.QRect(0, option.rect.top(), (percentage * total_width), options.rect.height())
            # my_clip = QtCore.QRect(0, option.rect.top(), percent1 * percentage, options.rect.height())

            # painter.setClipRect(my_clip)
            painter.fillRect(my_rect, bg_brush)



        elif index.column() == 1:
            painter.setPen(QtGui.QColor("#ffffff"))

            painter.drawText(option.rect, self.center, options.text)


        elif index.column() == 2:
            painter.setPen(QtGui.QColor(Colors.color_pink))
            painter.drawText(option.rect, self.center, options.text)

        elif index.column() == 3:
            painter.drawText(option.rect, self.center, options.text)


        elif index.column() == 4:
            painter.drawText(option.rect, self.center, options.text)
            

        else:
            painter.setPen(QtGui.QColor(Colors.color_lightgrey))

        # painter.begin(painter)
        # painter.drawText(option.rect, self.center, options.text)

        # painter.end()

        painter.restore()
