# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


import pandas as pd
# import app
import PyQt5.QtCore as QtCore
# import numpy as np
# from datetime import datetime
from binance.exceptions import BinanceAPIException
import logging
from app.workers import Worker
# Todo: Think of location; Move into dataclass; Verify necessity of QObject
# inheritence and 

class UserData(QtCore.QObject):
    """QObject that holds various dicts of user data like
    open orders, trade history and current holdings."""

    def __init__(self, mw, mutex, tp, parent=None):
        super(UserData, self).__init__(parent)
        print("INIT UserData")
        self.mw = mw
        self.mutex = mutex
        self.threadpool = tp
        self.open_orders = dict()
        self.trade_history = dict()
        self.holdings = dict()
        # self.initial_open_orders()


    def initialize(self):
        """Spawn workers in a separate thread to fetch
        user data initially."""
        
        
        worker = Worker(self.get_initial_data)
        worker.signals.progress.connect(self.process_initial_data)
        self.threadpool.start(worker)


    def get_initial_data(self, progress_callback):
        """Fetch user data."""
        self.initial_open_orders()
        # self.initial_history()
        self.initial_holdings()

        progress_callback.emit("1")

    # currently not needed
    def process_initial_data(self, callback):
        """process user data."""
        print("init data callback", callback)


    def change_pair(self):
        """This is called when the pair is changed.
        All pair dependant user_data functions are called from here."""
        self.initial_history()

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
        """Store order in open orders dictionary.
        Update concerned ui elements."""
        order_id = order["orderId"]
        run_setup = False

        # if no order is open, remember to run setup to initialize table widths
        if not len(self.open_orders):
            run_setup = True
        self.set_save(self.open_orders, order_id, order)

        # if clientOrderId is not present, order information comes
        # from websocket therefore open_orders_table should be updated.
        if not order.get("clientOrderId"):
            order["price"] = order["orderPrice"]

            # if this is the first open order, run setup.
            # else, update open orders table
            # TODO: This logic should probably go to the model/view
            if run_setup:
                self.mw.open_orders_view.setup()

            self.mw.open_orders_view.websocket_update()



    def initial_open_orders(self):
        try:
            orders = self.mw.api_manager.api_all_orders()
            for order in orders:
                self.add_to_open_orders(order)
        except BinanceAPIException:
            print("OPEN ORDERS COULD NOT BE FETCHED!!")


    def create_open_orders_df(self):
        """Create a pandas dataframe suitable for displaying open orders."""
        print("create open orders df")
        for _, order in self.open_orders.items():
            order["filled_percent"] = float(order["executedQty"]) / float((order["origQty"])) * 100
            order["total_btc"] = float(order["origQty"]) * float(order["price"])
            order["cancel"] = "cancel"

            order_id = int(order["orderId"])

            # Filled in percent value is calculated by a custom item delegate.
            # The price is used as a sort off dummy.
            order["filled_in_percent"] = float(order["price"])

            self.set_save(self.open_orders, order_id, order)

        if self.open_orders:
            df = pd.DataFrame.from_dict(self.open_orders, orient='index')
            df = df[["time", "symbol", "type", "side", "price", "origQty", "filled_percent", "total_btc", "orderId", "cancel", "filled_in_percent"]]
            df.columns = ["Date & Time", "Pair", "Type", "Side", "Price", "Quantity", "Filled %", "Total", "id", "cancel", "Filled in %"]
            df = df.apply(pd.to_numeric, errors='ignore')
            return df
        
        # return an empty dataframe if no orders are open.
        return pd.DataFrame()


    def remove_from_open_orders(self, order):
        order_id = order["orderId"]
        self.del_save(self.open_orders, order_id)

        if not order.get("clientOrderId"):
            self.mw.open_orders_view.websocket_update()

    # Maybe not needed TODO
    def update_orders(self):
        """Iterate over open orders and update"""
        pass

    # Currently unused
    def update_order(self, order):
        order_id = order["orderId"]
        self.set_save(self.open_orders, order_id, order)
        self.mw.open_orders_view.websocket_update()


    def cancel_all(self):
        print("CANCEL ALL")
        logging.info("CANCEL OPEN ORDERS:")
        for i in range(self.mw.open_orders_view.model().rowCount()):
            if not self.mw.open_orders_view.isRowHidden(i):
                order_id = self.mw.open_orders_view.model().index(i, 8).data(QtCore.Qt.DisplayRole)
                pair = self.mw.open_orders_view.model().index(i, 1).data(QtCore.Qt.DisplayRole)
                
                self.mw.api_manager.cancel_order_byId(order_id, pair)
                logging.info("Cancel " + str(pair) + " Order: " + str(order_id))


    #################################################################
    # TRADE HISTORY
    #################################################################

    def add_to_history(self, order):
        """Called for every trade in user trade history."""
        # print("ADD TO HISTORY ORDER", order, "\n")

        # Bugfix: Store historical orders in a dictionary where the key is
        # "id", which is unique, unlike orderId which is used to combine partial orders.
        # TODO fix in other places; make sure to differentiate between orderId and id.
        # implement method that combines multiple partial fills
        
        # Refactor: Rather than try/except handle like dataclass methods; isinstance() to
        # differentiate between api call and websocket.
        try:
            order_id = order["id"]
        except KeyError:
            print("Order filled: check id/orderId!")
            order_id = order["orderId"]

        pair = order["symbol"]
        order["total"] = float(order["executedQty"]) * float(order["price"])
        qty = 0
        if not self.trade_history.get(pair):
            self.trade_history[pair] = dict()

        elif (self.trade_history[pair].get("orderId")):
            print("DEBUG IN ELIF!!!")
            oldOrder = self.trade_history[pair].get(order_id)
            print("OLD ORDER; ", oldOrder)
            print("COMPARE ORDERS: ", oldOrder["orderId"], order_id)
            print("die order: ", self.trade_history[pair][order_id])
            qty = self.trade_history[pair][order_id]["executedQty"]
            print("got quant! ", qty)
            order["executedQty"] = float(order["executedQty"]) + float(qty)
            print("New qty is: ", order["executedQty"])

        # print("ORDER DICT", self.trade_history[pair], "\n")
        self.set_save(self.trade_history[pair], order["orderId"], order)



    def initial_history(self, progress_callback=None):
        pair = self.mw.data.current.pair
        history = self.mw.api_manager.api_my_trades(pair)

        for entry in history:
            entry["symbol"] = pair
            entry["executedQty"] = float(entry["qty"])
            self.add_to_history(entry)
            if entry["isBuyer"] is True:
                entry["side"] = "BUY"
            else:
                entry["side"] = "SELL"

        # TODO COME BACK
        if progress_callback:
            print("HISTORY CALLBACK UPDATE")
            progress_callback.emit("update")

        else:
            print("INIT HIST W/O PROGRESS_CALLBACK")
        # self.mw.trade_history_view.websocket_update()


    def create_history_df(self):
        """Create a pandas dataframe containing user trade information."""
        # print("CREATE HISTORY DF")
        history = dict()
        for _, historical_trade in self.trade_history.items():

            for item in historical_trade.items():
                values = item[1]
                order_id = item[0]

                history[order_id] = values


            # print(historical_trade[0])
            # print(historical_trade[1])
            # print("#############")

        if self.trade_history:
            print("CREATE HISTORY DF")
            df = pd.DataFrame.from_dict(history, orient='index')

            df = df[["time", "symbol", "side", "price", "executedQty", "total", "orderId"]]
            df.columns = ["Date & Time", "Pair", "Side", "Price", "Quantity", "Total", "id"]
            final_df = df.apply(pd.to_numeric, errors='ignore')
            # final_df = df
            # print(final_df)
            return final_df

        print("NO TRADE HIST!new")
        return pd.DataFrame()

        #     order["filled_percent"] = '{number:.{digits}f}'.format(number=(float(order["executedQty"]) / float((order["origQty"])) * 100), digits=2) + "%"
        #     order["total_btc"] = '{number:.{digits}f}'.format(number=float(order["origQty"]) * float(order["price"]), digits=8) + " BTC"
        #     order["cancel"] = "cancel"

        #     order_id = order["orderId"]
        #     self.set_save(self.open_orders, order_id, order)

        # if self.open_orders:
        #     df = pd.DataFrame.from_dict(self.open_orders, orient='index')
        #     df = df[["time", "symbol", "type", "side", "price", "origQty", "filled_percent", "total_btc", "orderId", "cancel"]]
        #     df.columns = ["Date & Time", "Pair", "Type", "Side", "Price", "Quantity", "Filled %", "Total", "id", "cancel"]
        #     return df
        # else:
        #     # return an empty dataframe if no orders are open.
        #     return pd.DataFrame()


    #################################################################
    # ACCOUNT HOLDINGS
    #################################################################

    def set_accholdings(self, holdings):
        """Receives a dict of holdings.
        Stores values in dictionary self.holdings."""
        print("set_accholdings")
        for holding in holdings.items():
            coin = holding[0]
            free = holding[1]["free"]
            locked = holding[1]["locked"]


            values = self.get_holdings_array(coin, free, locked)

            self.set_save(self.holdings, coin, values)


    def update_holdings(self, holdings_list):
        """Receives a list of updated holdings and updates
        self.holdings dict."""
        for holding in holdings_list:
            coin = holding["a"]
            free = holding["f"]
            locked = holding["l"]
            values = self.get_holdings_array(coin, free, locked)

            self.set_save(self.holdings, coin, values)

        # update table
        self.mw.holdings_view.websocket_update()

        # update limit pane values
        self.mw.limit_pane.set_holding_values()


    def get_holdings_array(self, coin, free, locked):
        # print("TICKERS", self.mw.data.tickers)
        total = float(free) + float(locked)
        if coin != "BTC":
            # TODO: Fix race condition! This needs current btc price
            coin_price = float(self.mw.data.tickers.get(coin + "BTC", dict()).get("lastPrice", 0))
            total_btc = total * coin_price
            name = str(self.mw.data.pairs.get(coin + "BTC", dict()).get("baseAssetName", 0))
            # print("name", name)
        elif coin == "BTC":
            total_btc = total
            name = "Bitcoin"


        values = {"coin": coin,
                  "free": free,
                  "locked": locked,
                  "total": total,
                  "total_btc": total_btc,
                  "name": name}
        return values



    def initial_holdings(self):
        print("INIT HOLDINGS:")
        holdings = self.mw.api_manager.getHoldings()
        self.set_accholdings(holdings)


    def create_holdings_df(self):
        print("CREATE HOLDIGNS DF")
        if self.holdings:
            df = pd.DataFrame.from_dict(self.holdings, orient='index')

            df = df[["coin", "name", "free", "locked", "total", "total_btc"]]
            df.columns = ["Asset", "Name", "Free", "Locked", "Total", "Total BTC"]
            df = df.apply(pd.to_numeric, errors='ignore')
            # Filter dataframe by total_btc column
            mask = df["Total BTC"].values >= 0.001
            return df[mask]

        # else:
        #     print("No holdings")
        #     return pd.DataFrame()
