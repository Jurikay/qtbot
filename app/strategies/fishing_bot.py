# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from app.init import val
# from functools import partial
import app
# import time


class FishingBot(QtWidgets.QTableWidget):

    """Class containing fishing bot methods."""

    def __init__(self, parent=None):
        super(FishingBot, self).__init__(parent)

        self.mw = app.mw




    def add_order(self, arg2):
        """Ad a new order to the fishing bot table."""
        # print("adde order")
        print(str(self) + " " + str(arg2))

        coin_combo_box = QtWidgets.QComboBox()

        for coin in val["coins"]:
            icon = QtGui.QIcon("images/ico/" + coin[:-3] + ".svg")
            coin_combo_box.addItem(icon, coin[:-3])

        coinIndex = coin_combo_box.findText(val["coin"])
        coin_combo_box.setCurrentIndex(coinIndex)
        coin_combo_box.setEditable(True)
        coin_combo_box.setInsertPolicy(QtWidgets.QComboBox.NoInsert)

        side_combo_box = QtWidgets.QComboBox()
        side_combo_box.addItem("Buy")
        side_combo_box.addItem("Sell")

        row_count = self.rowCount()

        self.insertRow(row_count)
        self.setCellWidget(row_count, 0, coin_combo_box)
        self.setCellWidget(row_count, 1, side_combo_box)

        cancel_button = QtWidgets.QPushButton("cancel")
        # cancel_button.setProperty("row", row_count)
        cancel_button.clicked.connect(self.remove_order)
        self.setCellWidget(row_count, 3, cancel_button)

        self.setItem(row_count, 2, QtWidgets.QTableWidgetItem(str(row_count)))
        
        self.set_properties()


    def set_properties(self):
        for i in range(self.rowCount()):
            widget = self.cellWidget(i, 3)
            widget.setProperty("row", i)
            self.setItem(i, 2, QtWidgets.QTableWidgetItem(str(i)))


    def remove_order(self):
        # print("selfmw: " + str(self.mw))
        row = self.mw.sender().property("row")
        for i in range(self.rowCount()):
            widget = self.cellWidget(i, 3)
            try:
                if widget.property("row") == row:
                    self.removeRow(i)
            except Exception as e:
                print(str(e))
        self.set_properties()


    def clear_all_orders(self):
        print(str(app.mw))
        row_count = self.rowCount()
        print("clearing %i rows." % int(self.rowCount()))
        for i in reversed(range(row_count)):
            print(str(i))
            self.removeRow(i)


    def update_table(self):
        for _ in range(self.rowCount()):
            # set current price from val tickers
            pass


    def parse_table_contents(self):
        for _ in range(self.rowCount()):
            # get values of every row and store in array
            pass


    def start_fishing(self):
        pass

    def initialize(self):
        self.setColumnWidth(0, 100)
        self.setColumnWidth(1, 50)
        self.setColumnWidth(2, 75)
        self.setColumnWidth(4, 100)
        self.setColumnWidth(5, 120)
        self.mw.fish_add_trade.clicked.connect(self.add_order)
        self.mw.fish_clear_all.clicked.connect(self.clear_all_orders)
