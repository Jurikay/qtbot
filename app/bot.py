# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
import logging
from datetime import datetime, timedelta
from app.init import val
from app.colors import Colors
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore


class BotClass():

    """Callback functions that the main gui class is going to inherit."""

    def __init__(self):
        pass

    # this should stay in gui
    def holding_updated(self):
        """Callback function to draw updated holdings."""
        print("holding updated")
        self.limit_total_btc.setText(str(val["accHoldings"]["BTC"]["free"]) + " BTC")
        self.limit_total_coin.setText(str(val["accHoldings"][val["coin"]]["free"]) + " " + val["coin"])

        bold_font = QtGui.QFont()
        bold_font.setBold(True)

        for i in range(self.holdings_table.rowCount()):
            try:
                coin = self.holdings_table.item(i, 1).text()
                free = val["accHoldings"][coin]["free"]
                locked = val["accHoldings"][coin]["locked"]
                total = '{number:.{digits}f}'.format(number=float(free) + float(locked), digits=8)

                if coin != "BTC":
                    price = val["coins"][coin + "BTC"]["close"]
                    # print("wavg: " + str(wAvg))
                elif coin == "BTC":
                    price = 1

                total_btc = float(total) * float(price)
                total_btc_formatted = '{number:.{digits}f}'.format(number=total_btc, digits=8)

                self.holdings_table.setItem(i, 3, QtWidgets.QTableWidgetItem("{0:.8f}".format(float(total))))
                self.holdings_table.setItem(i, 4, QtWidgets.QTableWidgetItem("{0:g}".format(float(free))))
                self.holdings_table.setItem(i, 5, QtWidgets.QTableWidgetItem("{0:g}".format(float(locked))))
                self.holdings_table.setItem(i, 6, QtWidgets.QTableWidgetItem(total_btc_formatted))
                self.holdings_table.item(i, 6).setFont(bold_font)
                self.holdings_table.item(i, 6).setForeground(QtGui.QColor(Colors.color_lightgrey))


                if float(total) * float(price) < 0.001 and coin != "BTC":
                    self.holdings_table.removeRow(i)

            except AttributeError:
                print("attr error: " + str(i))

        self.check_buy_amount()
        self.check_sell_ammount()


    def add_to_open_orders(self, order):

        # play a sound file to indicate a new order
        # print("play sound")

        # val["sound_1"].play()
        # QSoundEffect.play("sounds/Tink.mp3")

        # only add to open orders table if the coin is currently selected.
        # if order["symbol"] == val["pair"]:
        self.open_orders.insertRow(0)
        self.open_orders.setItem(0, 0, QtWidgets.QTableWidgetItem(str(datetime.fromtimestamp(int(str(order["time"])[:-3])).strftime('%d.%m.%y - %H:%M:%S.%f')[:-7])))

        coin = order["symbol"].replace("BTC", "")
        icon = QtGui.QIcon("images/ico/" + coin + ".svg")
        icon_item = QtWidgets.QTableWidgetItem()
        icon_item.setIcon(icon)
        self.open_orders.setItem(0, 1, icon_item)

        self.open_orders.setItem(0, 2, QtWidgets.QTableWidgetItem(order["symbol"]))


        self.btn_trade = QtWidgets.QPushButton("Trade " + coin)
        self.btn_trade.clicked.connect(self.gotoTradeButtonClicked)


        self.open_orders.setCellWidget(0, 3, self.btn_trade)

        self.open_orders.setItem(0, 4, QtWidgets.QTableWidgetItem(order["type"]))
        self.open_orders.setItem(0, 5, QtWidgets.QTableWidgetItem(order["side"]))
        price = '{number:.{digits}f}'.format(number=float(order["price"]), digits=val["decimals"])
        self.open_orders.setItem(0, 6, QtWidgets.QTableWidgetItem(price))
        qty = '{number:.{digits}f}'.format(number=float(order["origQty"]), digits=val["assetDecimals"]) + " " + coin
        self.open_orders.setItem(0, 7, QtWidgets.QTableWidgetItem(qty))

        filled_percent = '{number:.{digits}f}'.format(number=float(order["executedQty"]) / float(order["origQty"]), digits=2) + "%"

        self.open_orders.setItem(0, 8, QtWidgets.QTableWidgetItem(filled_percent))

        total_btc = '{number:.{digits}f}'.format(number=float(order["origQty"]) * float(order["price"]), digits=8) + " BTC"


        self.open_orders.setItem(0, 9, QtWidgets.QTableWidgetItem(total_btc))

        self.open_orders.setItem(0, 10, QtWidgets.QTableWidgetItem(str(order["orderId"])))

        self.open_orders.setItem(0, 11, QtWidgets.QTableWidgetItem("cancel"))

        self.open_orders.item(0, 11).setForeground(QtGui.QColor(Colors.color_yellow))

        if order["side"] == "BUY":
            self.open_orders.item(0, 5).setForeground(QtGui.QColor(Colors.color_green))
        else:
            self.open_orders.item(0, 5).setForeground(QtGui.QColor(Colors.color_pink))



    def remove_from_open_orders(self, order):
        # if order["symbol"] == val["pair"]:
        items = self.open_orders.findItems(str(order["orderId"]), QtCore.Qt.MatchExactly)

        # findItems returns a list hence we iterate through it. We only expect one result though.
        for item in items:

            # get current row of coin to check
            row = item.row()
            self.open_orders.removeRow(row)

        # Log order
        if order["status"] == "FILLED":
            logging.info('[ ✓ ] ORDER FILLED! %s' % str(order["symbol"]) + " " + str(order["side"]) + " " + str(float(order["executedQty"])) + "/" + str(float(order["origQty"])) + " filled at " + str(order["price"]))

        elif order["status"] == "CANCELED":
            logging.info('[ ✘ ] ORDER CANCELED! %s' % str(order["symbol"]) + " " + str(order["side"]) + " " + str(float(order["executedQty"])) + "/" + str(float(order["origQty"])) + " filled at " + str(order["price"]))


    def add_to_history(self, order):

        # if order["symbol"] == val["pair"]:
        # print(str(val["histoy"][order["symbol"]]))

        if not type(val["history"][order["symbol"]]) is list:
            val["history"][order["symbol"]] = list()

        self.history_table.insertRow(0)

        coin = order["symbol"].replace("BTC", "")

        val["history"][order["symbol"]].append(order)

        print(type(val["history"][order["symbol"]]))

        icon = QtGui.QIcon("images/ico/" + coin + ".svg")
        icon_item = QtWidgets.QTableWidgetItem()
        icon_item.setIcon(icon)
        self.history_table.setItem(0, 1, icon_item)

        self.history_table.setItem(0, 0, QtWidgets.QTableWidgetItem(str(datetime.fromtimestamp(int(str(order["time"])[:-3])).strftime('%d.%m.%y - %H:%M:%S.%f')[:-7])))
        self.history_table.setItem(0, 2, QtWidgets.QTableWidgetItem(order["symbol"]))

        self.history_table.setItem(0, 3, QtWidgets.QTableWidgetItem(order["side"]))


        price = '{number:.{digits}f}'.format(number=float(order["price"]), digits=val["decimals"])
        self.history_table.setItem(0, 4, QtWidgets.QTableWidgetItem(price))

        qty = '{number:.{digits}f}'.format(number=float(order["executedQty"]), digits=val["assetDecimals"]) + " " + val["coin"]
        self.history_table.setItem(0, 5, QtWidgets.QTableWidgetItem(qty))


        # total = '{number:.{digits}f}'.format(number=float(order["price"]) * float(order["executedQty"]), digits=8)

        self.history_table.setItem(0, 6, QtWidgets.QTableWidgetItem('{number:.{digits}f}'.format(number=float(order["price"]) * float(order["executedQty"]), digits=8) + " BTC"))

        if order["side"] == "BUY":
            self.history_table.item(0, 3).setForeground(QtGui.QColor(Colors.color_green))
        else:
            self.history_table.item(0, 3).setForeground(QtGui.QColor(Colors.color_pink))


    def check_add_to_holdings(self, order):
        """Check if the coin has to be added to the holdings table"""
        pair = order["symbol"]
        symbol = pair.replace("BTC", "")
        holdings = list()

        # collect holdings from table
        for i in range(self.holdings_table.rowCount()):
            holdings.append(self.holdings_table.item(i, 1).text())

        # check if the symbol of the order is in the holdings table
        if not any(symbol in s for s in holdings):
            # if not, rebuild holdings table
            self.build_holdings()

    # remove canceled order from open orders table

    def update_open_order(self, order):
        logging.info('ORDER UPDATED! %s' % str(order))

        for i in range(self.open_orders.rowCount()):
            order_id = self.open_orders.item(i, 10).text()
            if str(order_id) == str(order["orderId"]):
                filled_percent = '{number:.{digits}f}'.format(number=(float(order["executedQty"]) / float(order["origQty"]) * 100), digits=2) + "%"

                self.open_orders.setItem(0, 8, QtWidgets.QTableWidgetItem(filled_percent))
                return


        # WIP check (fix)
        print("adde to open orders")
        self.add_to_open_orders(order)

    def orders_received(self, orders):
        """Callback function to draw order history."""
        for _, order in enumerate(orders):

            # if add order to history if it was completely filled or canceled but partially filled.
            if order["status"] == "FILLED" or order["status"] == "CANCELED":
                if float(order["executedQty"]) > 0:
                    self.add_to_history(order)

    def build_open_orders(self, orders):
        """Callback function to draw list of open orders."""
        for _, order in enumerate(orders):
            if order["status"] == "NEW" or order["status"] == "PARTIALLY_FILLED":

                self.add_to_open_orders(order)

    def build_holdings(self, *args):
        self.holdings_table.setRowCount(0)
        for holding in val["accHoldings"]:

            try:
                # if holding != "BTC" and holding != "BNC":
                if holding + "BTC" in val["coins"]:
                    name = val["coins"][holding + "BTC"]["baseAssetName"]
                elif holding == "BTC":
                    name = "Bitcoin"
            except KeyError:
                name = "Bitcoin"
            free = val["accHoldings"][holding]["free"]
            locked = val["accHoldings"][holding]["locked"]
            total = float(free) + float(locked)
            total_formatted = '{number:.{digits}f}'.format(number=total, digits=8)

            bold_font = QtGui.QFont()
            bold_font.setBold(True)

            try:
                if holding == "BTC":
                    icon = QtGui.QIcon("images/ico/" + str(holding) + ".svg")

                    icon_item = QtWidgets.QTableWidgetItem()
                    icon_item.setIcon(icon)
                    self.holdings_table.insertRow(0)
                    self.holdings_table.setItem(0, 0, icon_item)

                    self.holdings_table.setItem(0, 1, QtWidgets.QTableWidgetItem(holding))
                    self.holdings_table.setItem(0, 2, QtWidgets.QTableWidgetItem(name))
                    self.holdings_table.setItem(0, 3, QtWidgets.QTableWidgetItem("{0:.8f}".format(float(total))))
                    self.holdings_table.setItem(0, 4, QtWidgets.QTableWidgetItem("{0:g}".format(float(free))))
                    self.holdings_table.setItem(0, 5, QtWidgets.QTableWidgetItem("{0:g}".format(float(locked))))
                    self.holdings_table.setItem(0, 6, QtWidgets.QTableWidgetItem(total_formatted))

                    self.holdings_table.item(0, 6).setFont(bold_font)
                    self.holdings_table.item(0, 6).setForeground(QtGui.QColor(Colors.color_lightgrey))

                    self.btn_sell = QtWidgets.QPushButton('Trade' + " BTC")
                    self.btn_sell.setEnabled(False)
                    self.btn_sell.setStyleSheet("color: #666;")
                    self.btn_sell.clicked.connect(self.gotoTradeButtonClicked)
                    self.holdings_table.setCellWidget(0, 7, self.btn_sell)

                    self.holdings_table.setItem(0, 8, QtWidgets.QTableWidgetItem("-"))

                elif holding + "BTC" in val["coins"]:
                    if float(total) * float(val["coins"][holding + "BTC"]["close"]) >= 0.001:
                        icon = QtGui.QIcon("images/ico/" + str(holding) + ".svg")

                        icon_item = QtWidgets.QTableWidgetItem()
                        icon_item.setIcon(icon)

                        total_btc = total * float(val["coins"][holding + "BTC"]["close"])
                        total_btc_formatted = '{number:.{digits}f}'.format(number=total_btc, digits=8)

                        self.holdings_table.insertRow(1)
                        self.holdings_table.setItem(1, 0, icon_item)

                        self.holdings_table.setItem(1, 1, QtWidgets.QTableWidgetItem(holding))
                        self.holdings_table.setItem(1, 2, QtWidgets.QTableWidgetItem(name))
                        self.holdings_table.setItem(1, 3, QtWidgets.QTableWidgetItem("{0:.8f}".format(float(total))))
                        self.holdings_table.setItem(1, 4, QtWidgets.QTableWidgetItem("{0:g}".format(float(free))))
                        self.holdings_table.setItem(1, 5, QtWidgets.QTableWidgetItem("{0:g}".format(float(locked))))
                        self.holdings_table.setItem(1, 6, QtWidgets.QTableWidgetItem(total_btc_formatted))

                        self.holdings_table.item(1, 6).setFont(bold_font)
                        self.holdings_table.item(1, 6).setForeground(QtGui.QColor(Colors.color_lightgrey))

                        self.btn_sell = QtWidgets.QPushButton('Trade ' + str(holding))
                        self.btn_sell.clicked.connect(self.gotoTradeButtonClicked)
                        self.holdings_table.setCellWidget(1, 7, self.btn_sell)

                        self.holdings_table.setItem(1, 8, QtWidgets.QTableWidgetItem("0"))

            except KeyError:
                pass

            header = self.holdings_table.horizontalHeader()
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            # header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

            self.holdings_table.setIconSize(QtCore.QSize(25, 25))

    def shutdown_bot(self):
        self.write_stats()
