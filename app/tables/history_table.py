# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from datetime import datetime
import app
from app.init import val
# from app.table_items import CoinDelegate
from app.colors import Colors



class HistoryTable(QtWidgets.QTableWidget):

    """CoinIndex main class."""

    def __init__(self, parent=None):
        super(HistoryTable, self).__init__(parent)
        self.mw = app.mw
        self.setIconSize(QtCore.QSize(25, 25))




    def initialize(self):
        history_header = self.horizontalHeader()
        history_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.setColumnWidth(0, 130)
        self.setColumnWidth(2, 70)
        self.setColumnWidth(3, 70)
        self.setColumnWidth(6, 120)
        self.setColumnWidth(7, 80)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(30)


    def add_to_history(self, order):
        # print("add to history")
        # if order["symbol"] == self.mw.cfg_manager.pair:
        # print(str(val["histoy"][order["symbol"]]))
        print(str(order))
        if not isinstance(val["history"][order["symbol"]], list):
            val["history"][order["symbol"]] = list()

        self.insertRow(0)

        coin = order["symbol"].replace("BTC", "")

        val["history"][order["symbol"]].append(order)


        icon = QtGui.QIcon("images/ico/" + coin + ".svg")
        icon_item = QtWidgets.QTableWidgetItem()
        icon_item.setIcon(icon)
        self.setItem(0, 1, icon_item)

        self.setItem(0, 0, QtWidgets.QTableWidgetItem(str(datetime.fromtimestamp(int(str(order["time"])[:-3])).strftime('%d.%m.%y - %H:%M:%S.%f')[:-7])))
        self.setItem(0, 2, QtWidgets.QTableWidgetItem(order["symbol"]))

        self.setItem(0, 3, QtWidgets.QTableWidgetItem(order["side"]))


        price = '{number:.{digits}f}'.format(number=float(order["price"]), digits=val["decimals"])
        self.setItem(0, 4, QtWidgets.QTableWidgetItem(price))

        qty = '{number:.{digits}f}'.format(number=float(order["executedQty"]), digits=val["assetDecimals"]) + " " + order["symbol"].replace("BTC", "")
        self.setItem(0, 5, QtWidgets.QTableWidgetItem(qty))


        # total = '{number:.{digits}f}'.format(number=float(order["price"]) * float(order["executedQty"]), digits=8)

        self.setItem(0, 6, QtWidgets.QTableWidgetItem('{number:.{digits}f}'.format(number=float(order["price"]) * float(order["executedQty"]), digits=8) + " BTC"))

        if order["side"] == "BUY":
            self.item(0, 3).setForeground(QtGui.QColor(Colors.color_green))
        else:
            self.item(0, 3).setForeground(QtGui.QColor(Colors.color_pink))


    def orders_received(self, orders):
        """Callback function to draw order history."""
        for order in orders:

            # if add order to history if it was completely filled or canceled but partially filled.
            if order["status"] == "FILLED" or order["status"] == "CANCELED" or order["status"] == "PARTIALLY_FILLED":
                if float(order["executedQty"]) > 0:
                    self.add_to_history(order)
            else:
                print(str(order))
