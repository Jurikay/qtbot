# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""OpenOrdersTable main class."""

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

# from functools import partial
from datetime import datetime
from app.init import val
from app.colors import Colors
import app
import logging
from app.workers import Worker
# from app.apiFunctions import ApiCalls
# from functools import partial


class OpenOrdersTable(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super(OpenOrdersTable, self).__init__(parent)
        self.mw = app.mw
        self.threadpool = QtCore.QThreadPool()
        self.setIconSize(QtCore.QSize(25, 25))


    def mouseDoubleClickEvent(self, event):
        print("CLICK")
        print(str(self))
        print(str(self.parent()))


    # def mouseMoveEvent(self, event):
    #     print("move: " + str(event))



    def add_to_open_orders(self, order):
        print("add to open orders: " + order["symbol"] + str(order["price"]))

        # if the table was empty at initialization, set widths when the first row is added.
        if self.mw.open_orders.rowCount() == 0:
            self.set_width()

        self.mw.open_orders.insertRow(0)
        self.mw.open_orders.setItem(0, 0, QtWidgets.QTableWidgetItem(str(datetime.fromtimestamp(int(str(order["time"])[:-3])).strftime('%d.%m.%y - %H:%M:%S.%f')[:-7])))

        coin = order["symbol"].replace("BTC", "")
        icon = QtGui.QIcon("images/ico/" + coin + ".svg")
        icon_item = QtWidgets.QTableWidgetItem()
        icon_item.setIcon(icon)
        self.mw.open_orders.setItem(0, 1, icon_item)

        self.mw.open_orders.setItem(0, 2, QtWidgets.QTableWidgetItem(order["symbol"]))


        self.mw.btn_trade = QtWidgets.QPushButton("Trade " + coin)
        self.mw.btn_trade.clicked.connect(self.gotoTradeButtonClicked)


        self.mw.open_orders.setCellWidget(0, 3, self.mw.btn_trade)

        self.mw.open_orders.setItem(0, 4, QtWidgets.QTableWidgetItem(order["type"]))
        self.mw.open_orders.setItem(0, 5, QtWidgets.QTableWidgetItem(order["side"]))
        price = '{number:.{digits}f}'.format(number=float(order["price"]), digits=val["decimals"])
        self.mw.open_orders.setItem(0, 6, QtWidgets.QTableWidgetItem(price))
        qty = '{number:.{digits}f}'.format(number=float(order["origQty"]), digits=val["assetDecimals"]) + " " + coin
        self.mw.open_orders.setItem(0, 7, QtWidgets.QTableWidgetItem(qty))

        filled_percent = '{number:.{digits}f}'.format(number=(float(order["executedQty"]) / float(order["origQty"]) * 100), digits=2) + "%"

        self.mw.open_orders.setItem(0, 8, QtWidgets.QTableWidgetItem(filled_percent))

        total_btc = '{number:.{digits}f}'.format(number=float(order["origQty"]) * float(order["price"]), digits=8) + " BTC"


        self.mw.open_orders.setItem(0, 9, QtWidgets.QTableWidgetItem(total_btc))

        self.mw.open_orders.setItem(0, 10, QtWidgets.QTableWidgetItem(str(order["orderId"])))

        self.mw.open_orders.setItem(0, 11, QtWidgets.QTableWidgetItem("cancel"))

        self.mw.open_orders.item(0, 11).setForeground(QtGui.QColor(Colors.color_yellow))

        if order["side"] == "BUY":
            self.mw.open_orders.item(0, 5).setForeground(QtGui.QColor(Colors.color_green))
        else:
            self.mw.open_orders.item(0, 5).setForeground(QtGui.QColor(Colors.color_pink))


    def remove_from_open_orders(self, order):
        # if order["symbol"] == self.mw.cfg_manager.pair:
        items = self.mw.open_orders.findItems(str(order["orderId"]), QtCore.Qt.MatchExactly)

        # findItems returns a list hence we iterate through it. We only expect one result though.
        for item in items:

            # get current row of coin to check
            row = item.row()
            self.mw.open_orders.removeRow(row)

        # Log order
        if order["status"] == "FILLED":
            logging.info('[ ✓ ] ORDER FILLED! %s' % str(order["symbol"]) + " " + str(order["side"]) + " " + str(float(order["executedQty"])) + "/" + str(float(order["origQty"])) + " filled at " + str(order["price"]))

        elif order["status"] == "CANCELED":
            logging.info('[ ✘ ] ORDER CANCELED! %s' % str(order["symbol"]) + " " + str(order["side"]) + " " + str(float(order["executedQty"])) + "/" + str(float(order["origQty"])) + " filled at " + str(order["price"]))


    def update_open_order(self, order):
        logging.info('ORDER UPDATED! %s' % str(order))

        for i in range(self.mw.open_orders.rowCount()):
            order_id = self.mw.open_orders.item(i, 10).text()
            if str(order_id) == str(order["orderId"]):
                filled_percent = '{number:.{digits}f}'.format(number=(float(order["executedQty"]) / float(order["origQty"]) * 100), digits=2) + "%"

                self.mw.open_orders.setItem(0, 8, QtWidgets.QTableWidgetItem(filled_percent))
                return


    def build_open_orders(self, orders):
        """Callback function to draw list of open orders."""
        for _, order in enumerate(orders):
            if order["status"] == "NEW" or order["status"] == "PARTIALLY_FILLED":

                self.add_to_open_orders(order)


    def filter_open_orders(self, text, state):
        for i in range(self.mw.open_orders.rowCount()):
            if state == 2 and not self.mw.open_orders.item(i, 2).text().startswith(self.mw.cfg_manager.coin):
                self.mw.open_orders.setRowHidden(i, True)
            elif not self.mw.open_orders.item(i, 2).text().startswith(text.upper()):
                self.mw.open_orders.setRowHidden(i, True)
            else:
                self.mw.open_orders.setRowHidden(i, False)

            if text != "" and str(self.mw.open_orders.item(i, 10).text()).startswith(str(text)):
                self.mw.open_orders.setRowHidden(i, False)


    def open_orders_cell_clicked(self, row, column):
        """Method to cancel open orders from open orders table."""
        print("open orders click")


        if column == 11:
            order_id = str(self.item(row, 10).text())
            pair = str(self.item(row, 2).text())

            self.mw.api_manager.cancel_order_byId(order_id, pair)


    def initialize(self):
        print("open orders init")
        self.cellClicked.connect(self.open_orders_cell_clicked)

        worker = Worker(self.mw.api_manager.api_all_orders)
        worker.signals.progress.connect(self.build_open_orders)
        self.mw.threadpool.start(worker)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(30)
        self.set_width()

    def gotoTradeButtonClicked(self):
        button_text = self.sender().text()
        coin = button_text.replace("Trade ", "")

        coinIndex = self.mw.coin_selector.findText(coin)
        self.mw.coin_selector.setCurrentIndex(coinIndex)

        self.mw.gui_manager.change_pair()

    def set_width(self):
        self.setColumnWidth(0, 125)
        self.setColumnWidth(1, 30)
        self.setColumnWidth(2, 70)
        self.setColumnWidth(3, 120)
        self.setColumnWidth(4, 50)
        self.setColumnWidth(5, 50)
        self.setColumnWidth(7, 120)
        self.setColumnWidth(8, 75)
        self.setColumnWidth(9, 120)
        self.setColumnWidth(10, 75)


        # orders_header = self.horizontalHeader()
        # orders_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        # orders_header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        # orders_header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)

    def cancel_all_orders(self):
        if self.rowCount() > 0:
            logging.info("Cancel all open Orders!")
            for row in reversed(range(self.rowCount())):
                pair = self.item(row, 2).text()
                order_id = self.item(row, 10).text()
                self.mw.api_manager.cancel_order_byId(order_id, pair)
