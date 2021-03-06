# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""OpenOrdersTable main class."""

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import app
from app.colors import Colors
from app.init import val


class HoldingsTable(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super(HoldingsTable, self).__init__(parent)
        self.mw = app.mw
        self.setIconSize(QtCore.QSize(25, 25))



    def holding_updated(self):
        """Callback function to draw updated holdings."""
        print("holding updated")
        self.mw.limit_total_btc.setText(str(val["accHoldings"]["BTC"]["free"]) + " BTC")
        self.mw.limit_total_coin.setText(str(val["accHoldings"][self.mw.cfg_manager.coin]["free"]) + " " + self.mw.cfg_manager.coin)

        bold_font = QtGui.QFont()
        bold_font.setBold(True)

        # debug:
        self.header = self.horizontalHeader()

        sort_order = self.header.sortIndicatorOrder()
        sort_section = self.header.sortIndicatorSection()

        # self.header.setSortIndicator(0, 10)
        self.setSortingEnabled(False)


        rows_to_remove = list()

        print("Sort order: " + str(sort_order) + " Sort section: " + str(sort_section))

        for i in range(self.rowCount()):
            try:
                coin = self.item(i, 1).text()
                free = val["accHoldings"][coin]["free"]
                locked = val["accHoldings"][coin]["locked"]
                total = '{number:.{digits}f}'.format(number=float(free) + float(locked), digits=8)

                if coin != "BTC":
                    price = val["coins"][coin + "BTC"]["close"]
                    # print("wavg: " + str(wAvg))
                    self.setItem(i, 4, QtWidgets.QTableWidgetItem("{0:n}".format(float(free))))
                    self.setItem(i, 5, QtWidgets.QTableWidgetItem("{0:n}".format(float(locked))))
                elif coin == "BTC":
                    price = 1
                    self.setItem(i, 4, QtWidgets.QTableWidgetItem("{0:.8f}".format(float(free))))
                    self.setItem(i, 5, QtWidgets.QTableWidgetItem("{0:.8f}".format(float(locked))))

                total_btc = float(total) * float(price)
                total_btc_formatted = '{number:.{digits}f}'.format(number=total_btc, digits=8)

                self.setItem(i, 3, QtWidgets.QTableWidgetItem("{0:.8f}".format(float(total))))
                self.setItem(i, 6, QtWidgets.QTableWidgetItem(total_btc_formatted))
                self.item(i, 6).setFont(bold_font)
                self.item(i, 6).setForeground(QtGui.QColor(Colors.color_lightgrey))


                if float(total) * float(price) < 0.001 and coin != "BTC":
                    rows_to_remove.append(i)
                    
            except AttributeError as e:
                print("attr error: " + str(i))
                print(str(e))
                # self.build_holdings()

        # remove marked rows after loop since we would break iteration,
        # if we remove a row while iterating.
        for row in rows_to_remove:
            print("remove row " + str(row))
            print(str(self.item(row, 1).text()))
            self.removeRow(row)

        self.mw.limit_pane.check_buy_amount()
        self.mw.limit_pane.check_sell_amount()


        state = self.mw.hide_pairs.checkState()
        text = self.mw.coinindex_filter.text()
        self.filter_holdings(text, state)
        
        self.setSortingEnabled(True)
        # self.header.setSortIndicator(0, sort_section)


    def build_holdings(self):
        print("build holdings table")
        self.setSortingEnabled(False)

        self.setRowCount(0)
        for holding in val["accHoldings"]:

            try:
                # if holding != "BTC" and holding != "BNC":
                if holding + "BTC" in val["coins"]:
                    name = val["coins"][holding + "BTC"]["baseAssetName"]
                elif holding == "BTC":
                    name = "Bitcoin"
            except KeyError:
                # catch BTCBTC
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
                    self.insertRow(0)
                    self.setItem(0, 0, icon_item)

                    self.setItem(0, 1, QtWidgets.QTableWidgetItem(holding))
                    self.setItem(0, 2, QtWidgets.QTableWidgetItem(name))
                    self.setItem(0, 3, QtWidgets.QTableWidgetItem("{0:.8f}".format(float(total))))
                    self.setItem(0, 4, QtWidgets.QTableWidgetItem("{0:.8f}".format(float(free))))
                    self.setItem(0, 5, QtWidgets.QTableWidgetItem("{0:.8f}".format(float(locked))))
                    self.setItem(0, 6, QtWidgets.QTableWidgetItem(total_formatted))

                    self.item(0, 6).setFont(bold_font)
                    self.item(0, 6).setForeground(QtGui.QColor(Colors.color_lightgrey))

                    self.btn_sell = QtWidgets.QPushButton('Trade' + " BTC")
                    self.btn_sell.setEnabled(False)
                    self.btn_sell.setStyleSheet("color: #666;")
                    self.btn_sell.clicked.connect(self.gotoTradeButtonClicked)

                    self.setCellWidget(0, 7, self.btn_sell)

                    self.setItem(0, 8, QtWidgets.QTableWidgetItem("-"))

                elif holding + "BTC" in val["coins"]:
                    if float(total) * float(val["coins"][holding + "BTC"]["close"]) >= 0.001:
                        icon = QtGui.QIcon("images/ico/" + str(holding) + ".svg")

                        icon_item = QtWidgets.QTableWidgetItem()
                        icon_item.setIcon(icon)

                        total_btc = total * float(val["coins"][holding + "BTC"]["close"])
                        total_btc_formatted = '{number:.{digits}f}'.format(number=total_btc, digits=8)

                        self.insertRow(1)
                        self.setItem(1, 0, icon_item)

                        self.setItem(1, 1, QtWidgets.QTableWidgetItem(holding))
                        self.setItem(1, 2, QtWidgets.QTableWidgetItem(name))
                        self.setItem(1, 3, QtWidgets.QTableWidgetItem("{0:.8f}".format(float(total))))
                        self.setItem(1, 4, QtWidgets.QTableWidgetItem("{0:g}".format(float(free))))
                        self.setItem(1, 5, QtWidgets.QTableWidgetItem("{0:g}".format(float(locked))))
                        self.setItem(1, 6, QtWidgets.QTableWidgetItem(total_btc_formatted))

                        self.item(1, 6).setFont(bold_font)
                        self.item(1, 6).setForeground(QtGui.QColor(Colors.color_lightgrey))

                        btn_sell = QtWidgets.QPushButton('Trade ' + str(holding))
                        btn_sell.clicked.connect(self.gotoTradeButtonClicked)
                        self.setCellWidget(1, 7, btn_sell)

                        self.setItem(1, 8, QtWidgets.QTableWidgetItem("0"))

            except KeyError as e:
                print("Build holdings error: " + str(e))

            header = self.horizontalHeader()
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            # header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            self.setSortingEnabled(True)



    def check_add_to_holdings(self, order):
        """Check if the coin has to be added to the holdings table"""
        pair = order["symbol"]
        symbol = pair.replace("BTC", "")
        holdings = list()

        # collect holdings from table
        for i in range(self.rowCount()):
            holdings.append(self.item(i, 1).text())

        # check if the symbol of the order is in the holdings table
        if not any(symbol in s for s in holdings):
            # if not, rebuild holdings table
            print("adding " + str(symbol) + " to holdings table.")
            # self.build_holdings()
            # self.insertRow(1)
            # self.setItem(1, 1, QtWidgets.QTableWidgetItem(symbol))
            self.add_holding(order)
            self.update_holding_prices()

    def add_holding(self, order):
        self.setSortingEnabled(False)
        pair = order["symbol"]
        symbol = pair.replace("BTC", "")

        name = val["coins"][symbol + "BTC"]["baseAssetName"]
        free = val["accHoldings"][symbol]["free"]
        locked = val["accHoldings"][symbol]["locked"]
        total = float(free) + float(locked)
        # total_formatted = '{number:.{digits}f}'.format(number=total, digits=8)

        bold_font = QtGui.QFont()
        bold_font.setBold(True)

        if float(total) * float(val["coins"][symbol + "BTC"]["close"]) >= 0.001:
            icon = QtGui.QIcon("images/ico/" + str(symbol) + ".svg")

            icon_item = QtWidgets.QTableWidgetItem()
            icon_item.setIcon(icon)

            total_btc = total * float(val["coins"][symbol + "BTC"]["close"])
            total_btc_formatted = '{number:.{digits}f}'.format(number=total_btc, digits=8)

            self.insertRow(0)
            self.setItem(0, 0, icon_item)

            self.setItem(0, 1, QtWidgets.QTableWidgetItem(symbol))
            self.setItem(0, 2, QtWidgets.QTableWidgetItem(name))
            self.setItem(0, 3, QtWidgets.QTableWidgetItem("{0:.8f}".format(float(total))))
            self.setItem(0, 4, QtWidgets.QTableWidgetItem("{0:g}".format(float(free))))
            self.setItem(0, 5, QtWidgets.QTableWidgetItem("{0:g}".format(float(locked))))
            self.setItem(0, 6, QtWidgets.QTableWidgetItem(total_btc_formatted))

            self.item(0, 6).setFont(bold_font)
            self.item(0, 6).setForeground(QtGui.QColor(Colors.color_lightgrey))

            btn_sell = QtWidgets.QPushButton('Trade ' + str(symbol))
            btn_sell.clicked.connect(self.gotoTradeButtonClicked)
            self.setCellWidget(0, 7, btn_sell)

            self.setItem(0, 8, QtWidgets.QTableWidgetItem("0"))
        self.setSortingEnabled(True)


    def initialize(self):
        self.build_holdings()
        self.setColumnWidth(0, 150)
        self.setColumnWidth(1, 75)
        self.setColumnWidth(7, 120)
        self.setIconSize(QtCore.QSize(25, 25))
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(30)


    def gotoTradeButtonClicked(self):
        button_text = self.sender().text()
        coin = button_text.replace("Trade ", "")

        coinIndex = self.mw.coin_selector.findText(coin)
        self.mw.coin_selector.setCurrentIndex(coinIndex)

        self.mw.gui_manager.change_pair()


    def filter_holdings(self, text, state):
        for i in range(self.rowCount()):
            if state == 2 and not self.item(i, 1).text().startswith(self.mw.cfg_manager.coin):
                self.setRowHidden(i, True)
            elif not self.item(i, 1).text().startswith(text.upper()):
                self.setRowHidden(i, True)
            else:
                self.setRowHidden(i, False)


    def update_holding_prices(self):

        """Update the total value of every coin in the holdings table."""

        self.setSortingEnabled(False)

        bold_font = QtGui.QFont()
        bold_font.setBold(True)

        row_count = self.rowCount()

        for i in range(row_count):

            try:
                current_total = self.item(i, 6).text()

                coin = self.item(i, 1).text()
                total = float(self.item(i, 3).text())

                if coin != "BTC":
                    current_price = float(val["tickers"][coin + "BTC"]["lastPrice"])
                elif coin == "BTC":
                    current_price = 1

                total_value = total * current_price
                total_formatted = '{number:.{digits}f}'.format(number=float(total_value), digits=8)

                if current_total != total_formatted:
                    self.item(i, 6).setText(total_formatted)
                    self.item(i, 6).setFont(bold_font)
                    self.item(i, 6).setForeground(QtGui.QColor(Colors.color_lightgrey))
            except AttributeError as e:
                # coin has been removed
                # self.build_holdings()
                print("update holdings error: " + str(e))


            self.setSortingEnabled(True)
