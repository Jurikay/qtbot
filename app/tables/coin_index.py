# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import app
from app.init import val
from app.table_items import CoinDelegate
from app.colors import Colors

"""CoinIndex main class."""


class CoinIndex(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super(QtWidgets.QTableWidget, self).__init__(parent)
        self.mw = app.mw

    def filter_coin_index(self, text, state):
        for i in range(self.rowCount()):
            if state == 2 and not self.item(i, 1).text().startswith(val["coin"]):
                self.setRowHidden(i, True)
            elif not self.item(i, 1).text().startswith(text.upper()):
                self.setRowHidden(i, True)
            else:
                self.setRowHidden(i, False)


    def build_coinindex(self):
        self.setRowCount(0)
        print("setze delegate")
        self.setItemDelegate(CoinDelegate(self))

        for pair in val["tickers"]:
            if "USDT" not in pair:
                coin = str(val["tickers"][pair]["symbol"]).replace("BTC", "")
                # print(str(holding))

                icon = QtGui.QIcon("images/ico/" + coin + ".svg")

                icon_item = QtWidgets.QTableWidgetItem()
                icon_item.setIcon(icon)

                # price_change = float(val["tickers"][pair]["priceChangePercent"])
                # if price_change > 0:
                #     operator = "+"
                # else:
                #     operator = ""

                last_price = QtWidgets.QTableWidgetItem()
                last_price.setData(QtCore.Qt.EditRole, QtCore.QVariant(val["tickers"][pair]["lastPrice"]))

                price_change = QtWidgets.QTableWidgetItem()
                price_change_value = float(val["tickers"][pair]["priceChangePercent"])
                price_change.setData(QtCore.Qt.EditRole, QtCore.QVariant(price_change_value))

                btc_volume = QtWidgets.QTableWidgetItem()
                btc_volume.setData(QtCore.Qt.EditRole, QtCore.QVariant(round(float(val["tickers"][pair]["quoteVolume"]), 2)))

                zero_item = QtWidgets.QTableWidgetItem()
                zero_item.setData(QtCore.Qt.EditRole, QtCore.QVariant(0))
                # price_change.setData(Qt.DisplayRole, QtCore.QVariant(str(val["tickers"][pair]["priceChangePercent"]) + "%"))

                self.insertRow(0)
                self.setItem(0, 0, icon_item)
                self.setItem(0, 1, QtWidgets.QTableWidgetItem(coin))
                self.setItem(0, 2, last_price)
                self.setItem(0, 3, QtWidgets.QTableWidgetItem(price_change))
                self.setItem(0, 4, QtWidgets.QTableWidgetItem(btc_volume))

                for i in (number + 6 for number in range(7)):
                    self.setItem(0, i, QtWidgets.QTableWidgetItem(zero_item))

                if price_change_value < 0:
                    self.item(0, 3).setForeground(QtGui.QColor(Colors.color_pink))
                else:
                    self.item(0, 3).setForeground(QtGui.QColor(Colors.color_green))

                self.btn_trade = QtWidgets.QPushButton("Trade " + coin)
                self.btn_trade.clicked.connect(self.gotoTradeButtonClicked)
                self.setCellWidget(0, 5, self.btn_trade)

        self.model().sort(5, QtCore.Qt.AscendingOrder)
        self.setIconSize(QtCore.QSize(25, 25))
        self.setIconSize(QtCore.QSize(25, 25))

        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.setColumnWidth(2, 120)
        self.setColumnWidth(5, 130)
        self.model().sort(4, QtCore.Qt.DescendingOrder)



    def gotoTradeButtonClicked(self):
        button_text = self.sender().text()
        coin = button_text.replace("Trade ", "")

        coinIndex = self.mw.coin_selector.findText(coin)
        self.mw.coin_selector.setCurrentIndex(coinIndex)

        self.mw.change_pair()

    
    def update_coin_index_prices(self):
        for i in range(self.rowCount()):
            coin = self.item(i, 1).text()
            price = self.item(i, 2).text()
            price_change = self.item(i, 3).text()
            btc_volume = self.item(i, 4).text()

            new_price = QtWidgets.QTableWidgetItem()
            new_price_change = QtWidgets.QTableWidgetItem()
            new_btc_volume = QtWidgets.QTableWidgetItem()

            new_price_value = "{0:.8f}".format(float(val["tickers"][coin + "BTC"]["lastPrice"]))
            new_price_change_value = float(val["tickers"][coin + "BTC"]["priceChangePercent"])
            new_btc_volume_value = float(val["tickers"][coin + "BTC"]["quoteVolume"])

            new_price.setData(QtCore.Qt.EditRole, QtCore.QVariant(new_price_value))
            new_price_change.setData(QtCore.Qt.EditRole, QtCore.QVariant(new_price_change_value))
            new_btc_volume.setData(QtCore.Qt.EditRole, QtCore.QVariant(new_btc_volume_value))

            if price != new_price_value:
                self.setItem(i, 2, new_price)

            if float(price_change) != new_price_change_value:

                self.setItem(i, 3, new_price_change)

            if float(btc_volume) != new_btc_volume_value:

                self.setItem(i, 4, new_btc_volume)