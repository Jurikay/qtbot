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
        self.running = False




    def add_order(self, arg2):
        """Ad a new order to the fishing bot table."""
        # print("adde order")
        print(str(self) + " " + str(arg2))


        side_combo_box = QtWidgets.QComboBox()
        side_combo_box.addItem("Buy")
        side_combo_box.addItem("Sell")

        price_selector = QtWidgets.QDoubleSpinBox()
        price_selector.setDecimals(val["decimals"])
        price_selector.setSingleStep(float(val["coins"][self.mw.cfg_manager.pair]["tickSize"]))

        amount_selector = QtWidgets.QDoubleSpinBox()
        amount_selector.setDecimals(val["assetDecimals"])
        amount_selector.setSingleStep(float(val["coins"][self.mw.cfg_manager.pair]["minTrade"]))


        row_count = self.rowCount()

        self.insertRow(row_count)
        self.setCellWidget(row_count, 0, self.build_coin_selector())
        self.setCellWidget(row_count, 1, side_combo_box)
        self.setCellWidget(row_count, 2, price_selector)
        self.setCellWidget(row_count, 3, amount_selector)

        cancel_button = QtWidgets.QPushButton("cancel")
        # cancel_button.setProperty("row", row_count)
        cancel_button.clicked.connect(self.remove_order)
        self.setCellWidget(row_count, 4, cancel_button)

        self.setItem(row_count, 5, QtWidgets.QTableWidgetItem(str(row_count)))

        self.set_properties()


    def build_coin_selector(self):
        coin_combo_box = QtWidgets.QComboBox()
        for coin in val["coins"]:
            icon = QtGui.QIcon("images/ico/" + coin[:-3] + ".svg")
            coin_combo_box.addItem(icon, coin[:-3])

        coinIndex = coin_combo_box.findText(self.mw.cfg_manager.coin)
        coin_combo_box.setCurrentIndex(coinIndex)
        coin_combo_box.setEditable(True)
        coin_combo_box.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        return coin_combo_box


    def set_properties(self):
        for i in range(self.rowCount()):
            widget = self.cellWidget(i, 4)
            widget.setProperty("row", i)
            # self.setItem(i, 2, QtWidgets.QTableWidgetItem(str(i)))


    def remove_order(self):
        # print("selfmw: " + str(self.mw))
        row = self.mw.sender().property("row")
        for i in range(self.rowCount()):
            widget = self.cellWidget(i, 4)
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


    def go_fishing(self):
        if self.running is False:
            self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
            self.mw.go_fishing.setText("Stop Fishing")
            self.running = True
            self.widgets_editable(False)
        else:
            self.setEditTriggers(QtWidgets.QAbstractItemView.SelectedClicked)
            self.mw.go_fishing.setText("Go Fishing")
            self.running = False
            self.widgets_editable(True)



    def widgets_editable(self, true_false):
        if isinstance(true_false, bool):
            for i in range(self.rowCount()):
                for j in range(5):
                    self.cellWidget(i, j).setEnabled(true_false)

                if true_false is False:
                    self.cellWidget(i, j).setStyleSheet("color: #999")
                else:
                    self.cellWidget(i, j).setStyleSheet("color: #cdcdcd")

            if true_false is False:
                self.mw.fish_add_trade.setStyleSheet("color: #999;")
                self.mw.fish_clear_all.setStyleSheet("color: #999;")
                self.mw.fish_status.setText("<span style='color: #94c940'>running</span>")

            else:
                self.mw.fish_add_trade.setStyleSheet("color: #cdcdcd;")
                self.mw.fish_clear_all.setStyleSheet("color: #cdcdcd;")
                self.mw.fish_status.setText("<span style='color: #f3ba2e'>paused</span>")


            self.mw.fish_add_trade.setEnabled(true_false)
            self.mw.fish_clear_all.setEnabled(true_false)


    def initialize(self):
        self.setColumnWidth(0, 100)
        self.setColumnWidth(1, 50)
        self.setColumnWidth(2, 75)
        self.setColumnWidth(4, 100)
        self.setColumnWidth(5, 120)
        self.mw.fish_add_trade.clicked.connect(self.add_order)
        self.mw.fish_clear_all.clicked.connect(self.clear_all_orders)

        self.mw.go_fishing.clicked.connect(self.go_fishing)