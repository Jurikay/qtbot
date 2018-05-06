# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


import pandas as pd
# import app
import PyQt5.QtCore as QtCore
import numpy as np
from datetime import datetime


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
        self.initial_open_orders()


    def add(self, order, value_type):
        self.mutex.lock()

        if value_type == open_orders:
            pass


    def update(self, order, type):
        pass

    def remove(self, order, type):
        pass


    def set_save(self, storage, index, value):
        """Uses mutex to savely set dictionary values."""
        self.mutex.lock()
        storage[index] = value
        self.mutex.unlock()


    def del_save(self, storage, index):
        self.mutex.lock()
        del storage[index]
        self.mutex.unlock()


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


    def add_to_open_orders(self, order):
        order_id = order["orderId"]
        self.set_save(self.open_orders, order_id, order)

        # if clientOrderId is not present, order information comes
        # from websocket therefore open_orders_table should be updated.
        if not order.get("clientOrderId"):
            self.mw.data_open_orders_table.update()

    def remove_from_open_orders(self, order):
        order_id = order["orderId"]
        self.del_save(self.open_orders, order_id)
        
        if not order.get("clientOrderId"):
            self.mw.data_open_orders_table.update()

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


    def initial_open_orders(self):
        orders = self.mw.api_manager.api_all_orders()
        for order in orders:
            self.add_to_open_orders(order)
