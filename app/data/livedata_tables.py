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

from app.data.base_table_setup import BaseTableModel, BaseTableView, BasicDelegate


class BackgroundTable(BaseTableView):
    """Extended TableView that draws a colored background."""

    def __init__(self, *args, **kwargs):
        BaseTableView.__init__(self, *args, **kwargs)
        self.max_order = 1
        self.has_data = False
        self.my_model = BaseTableModel(self)

    def paintEvent(self, event):
        """Custom paint event to draw colored background to
        indicate order size."""

        print("bg table paint")
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
            print("rev new tables")
            df = df.reindex(index=df.index[::-1])
        
        maxval = self.get_max_value(df)
        self.max_order = maxval
        self.has_data = True
        print("return df", df)
        return df


    def get_max_value(self, df):
        return 1

    def set_widths(self):
        self.horizontalHeader().setSortIndicatorShown(False)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(16)
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)

    def update(self):
        self.df = self.create_dataframe(self.data)
        self.my_model.update(self.df)


class AsksView(BackgroundTable):
    def __init__(self, *args, **kwargs):
        BackgroundTable.__init__(self, *args, **kwargs)
        self.color = Colors.color_pink
        self.bg_color = "#473043"
        self.highlight = "#ff58a8"
        self.data = "asks"


    def get_max_value(self, df):
        max_val = df["Total"].max()
        return max_val

    def set_df(self):
        return self.create_dataframe(self.data)


class BidsView(BackgroundTable):
    def __init__(self, *args, **kwargs):
        BackgroundTable.__init__(self, *args, **kwargs)
        self.color = Colors.color_green
        self.bg_color = "#3b4c37"
        self.highlight = "#aaff00"
        self.data = "bids"


    # def get_max_value(self, df):
    #     max_val = df["Total"].max()
    #     return max_val

    def set_df(self):
        return self.create_dataframe("bids")
