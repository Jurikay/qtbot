# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Collection of functions that concern the gui.
filter and wavg"""
# from functools import partial

# import PyQt5.QtCore as QtCore
# from PyQt5.QtCore import QtCore.QSize, Qt, QtCore.QVariant
# from PyQt5.QtGui import QColor, QFont, QIcon
# import PyQt5.QtWidgets as QtWidgets

# from app.charts import Webpages as Webpages
# from app.colors import Colors
from app.init import val
# from app.table_items import CoinDelegate
# from app.workers import Worker
# from app.callbacks import api_order_history




def calc_all_wavgs(self):
    for i in range(self.holdings_table.rowCount()):

        coin = self.holdings_table.item(i, 1).text()
        if coin != "BTC":
            wavg = calc_wavg(self)
            self.holdings_table.item(i, 8).setText(wavg)


# test
def calc_wavg(self):

    """Takes a pair and returns the weighted average buy price."""
    symbol = self.mw.cfg_manager.pair
    coin = symbol.replace("BTC", "")

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
        for i, order in enumerate(reversed(val["history"][symbol])):
            if order["side"] == "BUY":
                sum_traded += float(order["executedQty"])
                remaining -= float(order["executedQty"])
                total_cost += float(order["price"]) * float(order["executedQty"])

                wavg = total_cost / sum_traded

                print(str(i) + ". Buy: " + str(total_cost) + " remaining: " + str(remaining) + " wavg; " + str(wavg))

                # print(str(i) + ". buy: " + str(total_cost) + " remaining: " + str(remaining) + " wavg; " + str(wavg))
            elif order["side"] == "SELL":
                print(str(i))

                sum_traded -= float(order["executedQty"])
                remaining += float(order["executedQty"])
                total_cost -= float(order["executedQty"]) * float(order["price"])
                print(str(i) + ". Sell: " + str(total_cost) + " remaining: " + str(remaining) + " wavg; " + str(wavg))


            if coin != "BTC":
                if remaining <= float(val["coins"][coin + "BTC"]["minTrade"]):

                    if current_total > 0:
                        # if remaining < 0:
                        final = ('{number:.{digits}f}'.format(number=total_cost / (current_total + remaining), digits=8))


                        print("ENOUGH! " + final)
                        print("total amount: " + str((current_total - remaining)) + " total cost: " + str(total_cost))

                        return str(final)

                    return "0"
    except Exception as e:
        print("Error: " + str(e))
