# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Collection of functions that concern the gui."""

from functools import partial

import PyQt5.QtCore as QtCore
# from PyQt5.QtCore import QtCore.QSize, Qt, QtCore.QVariant
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtWidgets import QHeaderView, QPushButton, QTableWidgetItem

from app.charts import Webpages as Webpages
from app.colors import Colors
from app.init import val
from app.table_items import CoinDelegate
from app.workers import Worker
from app.callbacks import api_order_history


def initial_values(self):
    """Set various values needed for further tasks. Gets called when the pair
    is changed."""
    self.limit_total_btc.setText(str(val["accHoldings"]["BTC"]["free"]) + " BTC")
    self.limit_total_coin.setText(str(val["accHoldings"][val["coin"]]["free"]) + " " + val["coin"])

    self.limit_buy_label.setText("<span style='font-weight: bold; font-size: 12px;'>Buy " + val["coin"] + "</span>")
    self.limit_sell_label.setText("<span style='font-weight: bold; font-size: 12px;'>Sell " + val["coin"] + "</span>")

    # self.limit_coin_label_buy.setText("<span style='font-weight: bold; color: white;'>" + val["coin"] + "</span>")
    # self.limit_coin_label_sell.setText("<span style='font-weight: bold; color: white;'>" + val["coin"] + "</span>")

    # self.limit_buy_input.setText("kernoschmaus")
    self.limit_buy_input.setDecimals(val["decimals"])
    self.limit_buy_input.setSingleStep(float(val["coins"][val["pair"]]["tickSize"]))

    self.limit_sell_input.setDecimals(val["decimals"])
    self.limit_sell_input.setSingleStep(float(val["coins"][val["pair"]]["tickSize"]))

    self.limit_buy_amount.setDecimals(val["assetDecimals"])
    self.limit_buy_amount.setSingleStep(float(val["coins"][val["pair"]]["minTrade"]))

    self.limit_sell_amount.setDecimals(val["assetDecimals"])
    self.limit_sell_amount.setSingleStep(float(val["coins"][val["pair"]]["minTrade"]))

    self.buy_asset.setText(val["coin"])
    self.sell_asset.setText(val["coin"])

    self.chart.setHtml(Webpages.build_chart2(val["pair"], val["defaultTimeframe"]))
    self.chart.show()

    url = Webpages.build_cmc()
    self.cmc_chart.load(QtCore.QUrl(url))

    bids_header = self.bids_table.horizontalHeader()
    asks_header = self.asks_table.horizontalHeader()
    bids_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
    bids_header.setSectionResizeMode(1, QHeaderView.Stretch)
    bids_header.setSectionResizeMode(2, QHeaderView.Stretch)

    asks_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
    asks_header.setSectionResizeMode(1, QHeaderView.Stretch)
    asks_header.setSectionResizeMode(2, QHeaderView.Stretch)

    trades_header = self.tradeTable.horizontalHeader()
    trades_header.setSectionResizeMode(0, QHeaderView.Stretch)
    trades_header.setSectionResizeMode(1, QHeaderView.Stretch)


def global_filter(self, text):
    if str(text) != "":
        self.open_orders.setSortingEnabled(False)
        self.coin_index.setSortingEnabled(False)
        self.holdings_table.setSortingEnabled(False)

        for row in range(self.open_orders.rowCount()):
            self.open_orders.setRowHidden(row, True)
        items = self.open_orders.model().findItems(text, QtCore.Qt.MatchContains, 2)
        for item in items:
            row = item.row()
            self.open_orders.setRowHidden(row, False)

        for row in range(self.coin_index.rowCount()):
            self.coin_index.setRowHidden(row, True)
        items = self.coin_index.model().findItems(text, QtCore.Qt.MatchContains, 1)
        for item in items:
            row = item.row()
            self.coin_index.setRowHidden(row, False)

        for row in range(self.holdings_table.rowCount()):
            self.holdings_table.setRowHidden(row, True)
        items = self.holdings_table.model().findItems(text, QtCore.Qt.MatchContains, 1)
        for item in items:
            row = item.row()
            self.holdings_table.setRowHidden(row, False)
    elif text == "":
        for row in range(self.open_orders.rowCount()):
            self.open_orders.setRowHidden(row, False)

        for row in range(self.coin_index.rowCount()):
            self.coin_index.setRowHidden(row, False)

        for row in range(self.holdings_table.rowCount()):
            self.holdings_table.setRowHidden(row, False)
        self.open_orders.setSortingEnabled(False)
        self.coin_index.setSortingEnabled(False)
        self.holdings_table.setSortingEnabled(False)


def init_filter(self):
    text = self.coinindex_filter.text()
    state = self.hide_pairs.checkState()

    print("text: " + str(text) + " state: " + str(state))

    filter_table(self, text, state)

    # reset filter
    if state == 0 and text == "":
        for i in range(self.holdings_table.rowCount()):
            self.holdings_table.setRowHidden(i, False)
        for i in range(self.open_orders.rowCount()):
            self.open_orders.setRowHidden(i, False)
        for i in range(self.coin_index.rowCount()):
            self.coin_index.setRowHidden(i, False)



def filter_table(self, text, state):
    # print("filter table state: " + str(state))
    # tabIndex = self.tabsBotLeft.currentIndex()
    # if tabIndex == 0:
    filter_coin_index(self, text, state)
    # elif tabIndex == 1:
    self.open_orders.filter_open_orders(text, state)
    # elif tabIndex == 3:
    filter_holdings(self, text, state)
    if text != "" or state == 2:
        self.holdings_table.setSortingEnabled(False)
        self.open_orders.setSortingEnabled(False)
        self.coin_index.setSortingEnabled(False)
    else:
        self.holdings_table.setSortingEnabled(True)
        self.open_orders.setSortingEnabled(True)
        self.coin_index.setSortingEnabled(True)

    # state = self.hide_pairs.checkState()
    # if state == 2:
    #     self.toggle_other_pairs(state)


def filter_holdings(self, text, state):
    print("holdings row count: " + str(self.holdings_table.rowCount()))
    for i in range(self.holdings_table.rowCount()):
        if state == 2 and not self.holdings_table.item(i, 1).text().startswith(val["coin"]):
            self.holdings_table.setRowHidden(i, True)
        elif not self.holdings_table.item(i, 1).text().startswith(text.upper()):
            self.holdings_table.setRowHidden(i, True)
        else:
            self.holdings_table.setRowHidden(i, False)






def filter_coin_index(self, text, state):
    for i in range(self.coin_index.rowCount()):
        if state == 2 and not self.coin_index.item(i, 1).text().startswith(val["coin"]):
            self.coin_index.setRowHidden(i, True)
        elif not self.coin_index.item(i, 1).text().startswith(text.upper()):
            self.coin_index.setRowHidden(i, True)
        else:
            self.coin_index.setRowHidden(i, False)


def filter_return(self):
    print("filter return")
# def filter_coinindex(self, text):
#     # sort_order = self.coin_index.model().sortColumn()
#     # print(str(sort_order))

#     """Hide every row in coin index that does not contain the user input."""
#     self.coin_index.setSortingEnabled(False)
#     row_count = self.coin_index.rowCount()

#     if text != "":
#         self.coin_index.item(0, 1).setForeground(QColor(Colors.color_yellow))
#         for i in range(row_count):

#             if text.upper() not in str(self.coin_index.item(i, 1).text()):
#                 self.coin_index.hideRow(i)
#             else:
#                 self.coin_index.showRow(i)
#     else:
#         for j in range(row_count):
#             self.coin_index.showRow(j)
#         self.coin_index.setSortingEnabled(True)

    # print("procc")


def filter_confirmed(self):
    """Switch to the topmost coin of the coin index that is not hidden."""
    # check if input is empty
    if self.coinindex_filter.text() != "":
        # self.coin_index.setSortingEnabled(False)
        # test = self.coin_index.
        # print(str(test))

        # iterate through all rows
        for i in (range(self.coin_index.rowCount())):
            # skip the row if hidden
            if self.coin_index.isRowHidden(i):
                continue
            else:
                # return the first nonhidden row (might be inefficient)
                coin = self.coin_index.item(i, 1).text()
                # switch to that coin
                print(str(coin) + "   " + str(val["pair"]))

                if coin != val["pair"].replace("BTC", ""):
                    coinIndex = self.coin_selector.findText(coin)
                    self.coin_selector.setCurrentIndex(coinIndex)
                    self.change_pair()
                    # self.coin_index.setSortingEnabled(True)
                    return

                elif coin == val["pair"].replace("BTC", ""):
                    # self.coin_index.setSortingEnabled(True)
                    return


def build_coinindex(self):
    self.coin_index.setRowCount(0)
    print("setze delegate")
    self.coin_index.setItemDelegate(CoinDelegate(self))

    for pair in val["tickers"]:
        if "USDT" not in pair:
            coin = str(val["tickers"][pair]["symbol"]).replace("BTC", "")
            # print(str(holding))

            icon = QIcon("images/ico/" + coin + ".svg")

            icon_item = QTableWidgetItem()
            icon_item.setIcon(icon)

            # price_change = float(val["tickers"][pair]["priceChangePercent"])
            # if price_change > 0:
            #     operator = "+"
            # else:
            #     operator = ""

            last_price = QTableWidgetItem()
            last_price.setData(QtCore.Qt.EditRole, QtCore.QVariant(val["tickers"][pair]["lastPrice"]))

            price_change = QTableWidgetItem()
            price_change_value = float(val["tickers"][pair]["priceChangePercent"])
            price_change.setData(QtCore.Qt.EditRole, QtCore.QVariant(price_change_value))

            btc_volume = QTableWidgetItem()
            btc_volume.setData(QtCore.Qt.EditRole, QtCore.QVariant(round(float(val["tickers"][pair]["quoteVolume"]), 2)))

            zero_item = QTableWidgetItem()
            zero_item.setData(QtCore.Qt.EditRole, QtCore.QVariant(0))
            # price_change.setData(Qt.DisplayRole, QtCore.QVariant(str(val["tickers"][pair]["priceChangePercent"]) + "%"))

            self.coin_index.insertRow(0)
            self.coin_index.setItem(0, 0, icon_item)
            self.coin_index.setItem(0, 1, QTableWidgetItem(coin))
            self.coin_index.setItem(0, 2, last_price)
            self.coin_index.setItem(0, 3, QTableWidgetItem(price_change))
            self.coin_index.setItem(0, 4, QTableWidgetItem(btc_volume))

            for i in (number + 6 for number in range(7)):
                self.coin_index.setItem(0, i, QTableWidgetItem(zero_item))

            if price_change_value < 0:
                self.coin_index.item(0, 3).setForeground(QColor(Colors.color_pink))
            else:
                self.coin_index.item(0, 3).setForeground(QColor(Colors.color_green))

            self.btn_trade = QPushButton("Trade " + coin)
            self.btn_trade.clicked.connect(self.gotoTradeButtonClicked)
            self.coin_index.setCellWidget(0, 5, self.btn_trade)

    self.coin_index.model().sort(5, QtCore.Qt.AscendingOrder)
    self.coin_index.setIconSize(QtCore.QSize(25, 25))
    self.open_orders.setIconSize(QtCore.QSize(25, 25))

    self.coin_index.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
    self.coin_index.setColumnWidth(2, 120)
    self.coin_index.setColumnWidth(5, 130)
    self.coin_index.model().sort(4, QtCore.Qt.DescendingOrder)





def calc_total_btc():
    total_btc_val = 0
    for holding in val["accHoldings"]:
        free = val["accHoldings"][holding]["free"]
        locked = val["accHoldings"][holding]["locked"]
        total = float(free) + float(locked)

        if holding + "BTC" in val["coins"]:
            if holding != "BTC" and total * float(val["tickers"][holding + "BTC"]["lastPrice"]) > 0.001:

                coin_total = total * float(val["tickers"][holding + "BTC"]["lastPrice"])
                total_btc_val += coin_total

        elif holding == "BTC":
            total_btc_val += total

    total_formatted = '{number:.{digits}f}'.format(number=float(total_btc_val), digits=8) + " BTC"
    # print("total: " + total_formatted)
    return total_formatted


def calc_all_wavgs(self):
    for i in range(self.holdings_table.rowCount()):

        coin = self.holdings_table.item(i, 1).text()
        if coin != "BTC":
            wavg = calc_wavg(coin)
            self.holdings_table.item(i, 8).setText(wavg)





def calc_wavg(symbol):
    coin = symbol
    pair = symbol + "BTC"
    current_free = val["accHoldings"][coin]["free"]
    current_locked = val["accHoldings"][coin]["locked"]
    current_total = float(current_free) + float(current_locked)

    remaining = current_total
    total_cost = 0.0
    wavg = 0.0
    sum_traded = 0.0
    print("calculating wavg for " + str(coin))
    print("currently holding " + str(remaining))
    try:
        for i, order in enumerate(reversed(val["history"][pair])):
            if order["side"] == "BUY":
                sum_traded += float(order["executedQty"])
                remaining -= float(order["executedQty"])
                total_cost += float(order["price"]) * float(order["executedQty"])

                wavg = total_cost / sum_traded

                print(str(i))
                print("sum traded: " + str(sum_traded))
                print("remainign: " + str(remaining))
                print("exec qty: " + str(order["executedQty"]))
                # print(str(i) + ". buy: " + str(total_cost) + " remaining: " + str(remaining) + " wavg; " + str(wavg))
            elif order["side"] == "SELL":
                print(str(i))
                if wavg != 0:
                    sum_traded -= float(order["executedQty"])
                    print(str(i) + ". Sell: " + str(total_cost) + " remaining: " + str(remaining) + " wavg; " + str(wavg))
                    remaining += float(order["executedQty"])
                    total_cost -= float(order["executedQty"]) * wavg

            if coin != "BTC":
                if remaining <= float(val["coins"][coin + "BTC"]["minTrade"]):

                    if current_total > 0:
                        # if remaining < 0:
                        final = ('{number:.{digits}f}'.format(number=total_cost / (current_total - remaining), digits=8))


                        print("ENOUGH! " + final)
                        print("total amount: " + str((current_total - remaining)) + " total cost: " + str(total_cost))

                        return str(final)

                    return "0"
    except Exception as e:
        print("Error: " + str(e))


def update_holding_prices(self):

    """Update the total value of every coin in the holdings table."""

    bold_font = QFont()
    bold_font.setBold(True)

    for i in range(self.holdings_table.rowCount()):

        current_total = self.holdings_table.item(i, 6).text()

        coin = self.holdings_table.item(i, 1).text()
        total = float(self.holdings_table.item(i, 3).text())

        if coin != "BTC":
            current_price = float(val["tickers"][coin + "BTC"]["lastPrice"])
        elif coin == "BTC":
            current_price = 1

        total_value = total * current_price
        total_formatted = '{number:.{digits}f}'.format(number=float(total_value), digits=8)

        if current_total != total_formatted:
            self.holdings_table.item(i, 6).setText(total_formatted)
            self.holdings_table.item(i, 6).setFont(bold_font)
            self.holdings_table.item(i, 6).setForeground(QColor(Colors.color_lightgrey))


def update_coin_index_prices(self):
    for i in range(self.coin_index.rowCount()):
        coin = self.coin_index.item(i, 1).text()
        price = self.coin_index.item(i, 2).text()
        price_change = self.coin_index.item(i, 3).text()
        btc_volume = self.coin_index.item(i, 4).text()


        new_price = QTableWidgetItem()
        new_price_change = QTableWidgetItem()
        new_btc_volume = QTableWidgetItem()

        new_price_value = "{0:.8f}".format(float(val["tickers"][coin + "BTC"]["lastPrice"]))
        new_price_change_value = float(val["tickers"][coin + "BTC"]["priceChangePercent"])
        new_btc_volume_value = float(val["tickers"][coin + "BTC"]["quoteVolume"])

        new_price.setData(QtCore.Qt.EditRole, QtCore.QVariant(new_price_value))
        new_price_change.setData(QtCore.Qt.EditRole, QtCore.QVariant(new_price_change_value))
        new_btc_volume.setData(QtCore.Qt.EditRole, QtCore.QVariant(new_btc_volume_value))


        if price != new_price_value:
            self.coin_index.setItem(i, 2, new_price)

        if float(price_change) != new_price_change_value:

            self.coin_index.setItem(i, 3, new_price_change)

        if float(btc_volume) != new_btc_volume_value:

            self.coin_index.setItem(i, 4, new_btc_volume)


def get_trade_history(self, pair):
        worker = Worker(partial(api_order_history, pair))
        worker.signals.progress.connect(self.orders_received)
        self.threadpool.start(worker)
