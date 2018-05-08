# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


import pandas as pd
# import app
import PyQt5.QtCore as QtCore
# import numpy as np
# from datetime import datetime
from binance.exceptions import BinanceAPIException


class UserData(QtCore.QObject):
    """Object that holds various user data like
    open orders, trade history and current holdings."""

    def __init__(self, mw, mutex, parent=None):
        super(UserData, self).__init__(parent)
        print("INIT UserData")
        self.mw = mw
        self.mutex = mutex

        self.open_orders = dict()
        self.trade_history = dict()
        self.current_holdings = dict()
        # self.initial_open_orders()


    def set_save(self, storage, index, value):
        """Uses mutex to savely set dictionary values."""
        self.mutex.lock()
        storage[index] = value
        self.mutex.unlock()


    def del_save(self, storage, index):
        self.mutex.lock()
        del storage[index]
        self.mutex.unlock()




    #################################################################
    # OPEN ORDERS
    #################################################################

    def add_to_open_orders(self, order):
        order_id = order["orderId"]
        run_setup = False

        # if no order is open, run setup to initialize table widths
        if not len(self.open_orders):
            run_setup = True
        self.set_save(self.open_orders, order_id, order)

        # if clientOrderId is not present, order information comes
        # from websocket therefore open_orders_table should be updated.
        if not order.get("clientOrderId"):
            print(order)
            order["price"] = order["orderPrice"]

            # if this is the first open order, run setup.
            # else, update open orders table
            if run_setup:
                print("RUNNING SETUP")
                self.mw.data_open_orders_table.setup()
            else:
                self.mw.data_open_orders_table.update()


    def initial_open_orders(self):
        try:
            orders = self.mw.api_manager.api_all_orders()
            for order in orders:
                self.add_to_open_orders(order)
        except BinanceAPIException:
            print("OPEN ORDERS COULD NOT BE FETCHED!!")


    def create_dataframe(self):
        """Create a pandas dataframe suitable for displaying open orders."""
        for _, order in self.open_orders.items():
            order["filled_percent"] = '{number:.{digits}f}'.format(number=(float(order["executedQty"]) / float((order["origQty"])) * 100), digits=2) + "%"
            order["total_btc"] = '{number:.{digits}f}'.format(number=float(order["origQty"]) * float(order["price"]), digits=8) + " BTC"
            order["cancel"] = "cancel"
            
            order_id = order["orderId"]
            self.set_save(self.open_orders, order_id, order)

        if self.open_orders:
            df = pd.DataFrame.from_dict(self.open_orders, orient='index')
            sorted_df = df[["time", "symbol", "type", "side", "price", "origQty", "filled_percent", "total_btc", "orderId", "cancel"]]
            return sorted_df
        else:
            # return an empty dataframe if no orders are open.
            return pd.DataFrame()


    def remove_from_open_orders(self, order):
        order_id = order["orderId"]
        self.del_save(self.open_orders, order_id)

        if not order.get("clientOrderId"):
            self.mw.data_open_orders_table.update()

    def update_order(self, order):
        order_id = order["orderId"]
        



    #################################################################
    # TRADE HISTORY
    #################################################################

    def add_to_history(self, order):
        order_id = order["orderId"]
        pair = order["symbol"]
        if not self.trade_history.get(pair):
            self.trade_history[pair] = dict()

        self.set_save(self.trade_history[pair], order_id, order)


    def initial_history(self):
        print("Initial history")
        pair = self.mw.cfg_manager.pair
        history = self.mw.api_manager.api_my_trades(pair)

        for entry in history:
            self.add_to_history(entry)



    #################################################################
    # ACCOUNT HOLDINGS
    #################################################################

    def update_accholdings(self, holdings):
        """Receives a list of updated holdings.
        Stores values in dictionary current_holdings."""

        if isinstance(holdings, list):
            for holding in holdings:
                coin = holding["a"]
                free = holding["f"]
                locked = holding["l"]
                total = float(free) + float(locked)

                values = {"free": free,
                          "locked": locked,
                          "total": total}

                self.set_save(self.current_holdings, coin, values)