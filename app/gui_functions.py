# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Collection of functions that concern the gui.
filter and wavg"""
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
