# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Collection of functions that concern the gui."""

# from functools import partial

import PyQt5.QtCore as QtCore
# from PyQt5.QtCore import QtCore.QSize, Qt, QtCore.QVariant
# from PyQt5.QtGui import QColor, QFont, QIcon
# import PyQt5.QtWidgets as QtWidgets

# from app.charts import Webpages as Webpages
# from app.colors import Colors
from app.init import val
# from app.table_items import CoinDelegate
# from app.workers import Worker
# from app.callbacks import api_order_history



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

    # print("text: " + str(text) + " state: " + str(state))

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
    self.coin_index.filter_coin_index(text, state)
    # elif tabIndex == 1:
    self.open_orders.filter_open_orders(text, state)
    # elif tabIndex == 3:
    self.holdings_table.filter_holdings(text, state)
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
                # print(str(coin) + "   " + str(val["pair"]))

                if coin != val["pair"].replace("BTC", ""):
                    coinIndex = self.coin_selector.findText(coin)
                    self.coin_selector.setCurrentIndex(coinIndex)
                    self.change_pair()
                    # self.coin_index.setSortingEnabled(True)
                    return

                elif coin == val["pair"].replace("BTC", ""):
                    # self.coin_index.setSortingEnabled(True)
                    return


# global ui
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
