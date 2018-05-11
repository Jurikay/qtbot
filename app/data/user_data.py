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
        self.holdings = dict()
        # self.initial_open_orders()


    def initialize(self):
        self.initial_open_orders()
        self.initial_history()
        self.initial_holdings()

        self.mw.print_btn.clicked.connect(self.print_dicts)

        


    def set_save(self, storage, index, value):
        """Use mutex to savely set dictionary values."""
        self.mutex.lock()
        storage[index] = value
        self.mutex.unlock()


    def del_save(self, storage, index):
        """Savely delete a dictionary key."""
        self.mutex.lock()
        storage.pop(index, None)
        self.mutex.unlock()


    def print_dicts(self):
        print("USER DATA:")
        print("###############")
        print(self.open_orders)
        print("###############")
        print(self.trade_history)
        print("###############")
        print(self.holdings)


    #################################################################
    # OPEN ORDERS
    #################################################################

    def add_to_open_orders(self, order):
        order_id = order["orderId"]
        run_setup = False

        # if no order is open, remember to run setup to initialize table widths
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
                self.mw.data_open_orders_table.set_data()
            else:
                self.mw.data_open_orders_table.set_data()


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
            df = df[["time", "symbol", "type", "side", "price", "origQty", "filled_percent", "total_btc", "orderId", "cancel"]]
            df.columns = ["Date & Time", "Pair", "Type", "Side", "Price", "Quantity", "Filled %", "Total", "id", "cancel"]
            return df
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
        self.set_save(self.open_orders, order_id, order)
        



    #################################################################
    # TRADE HISTORY
    #################################################################

    def add_to_history(self, order):
        # print("ADD TO HIST", order)
        order_id = order["orderId"]
        pair = order["symbol"]
        if not self.trade_history.get(pair):
            self.trade_history[pair] = dict()

        self.set_save(self.trade_history[pair], order_id, order)


    def initial_history(self):
        
        pair = self.mw.cfg_manager.pair
        # print("Initial history", pair)
        history = self.mw.api_manager.api_my_trades(pair)

        for entry in history:
            entry["symbol"] = pair
            # print("init hist", entry)
            self.add_to_history(entry)



    #################################################################
    # ACCOUNT HOLDINGS
    #################################################################

    def update_accholdings(self, holdings):
        """Receives a list of updated holdings.
        Stores values in dictionary holdings."""

        print("update holdings", holdings)

        for holding in holdings:
            print(holding)
            # coin = holding[0]
            # free = holding[1]["free"]
            # locked = holding[1]["locked"]
            # total = float(free) + float(locked)

                # coin = holding["a"]
                # free = holding["f"]
                # locked = holding["l"]
                # total = float(free) + float(locked)

            # values = {"free": free,
                    #   "locked": locked,
                    #   "total": total}

            # self.set_save(self.holdings, coin, values)

    def initial_holdings(self):
        holdings = self.mw.api_manager.getHoldings()
        print("init holdings", holdings)

        self.update_accholdings(holdings)


