# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""A collection of methods that rely on the Python-Binance API
implementation to communicate with Binance."""

# methods should conform to this:
# - interact with binance api
# - return a value
# - do not store data
# - do not interact with the gui

from functools import partial
import time

from binance.exceptions import BinanceAPIException
from binance.client import Client
from requests.exceptions import ReadTimeout
import app
from app.workers import Worker
from app.charts import welcome_page, time_error_page, Webpages

class ApiCalls:
    """Collection of api related methods."""
    def __init__(self, mw, tp):
        self.mw = mw

        self.threadpool = tp
        self.banned_until = None
        self.error = None
        self.client = None
        self.init_authentication()
        # app.client = self.client

        # self.initialize()

        self.counter = 0


    def init_authentication(self):
        self.client = self.authenticate_client()
        app.client = self.client
        self.initialize()
        self.parse_error()

    def authenticate_client(self):
        print("Authenticate client")
        try:
            api_key = self.mw.cfg_manager.api_key
            api_secret = self.mw.cfg_manager.api_secret
        except Exception as e:
            self.error = "no-api-key"
            print("api key/secret not found!")
            print(e)
            return
        try:
            return Client(api_key, api_secret, {"verify": True, "timeout": 5})
        except BinanceAPIException as e:
            if "IP banned until" in str(e):
                self.banned_until = str(self.get_ban_duration(e))

    @staticmethod
    def get_ban_duration(error_msg):
        banned_until = str(error_msg).replace("APIError(code=-1003): Way too many requests; IP banned until ", "").replace(". Please use the websocket for live updates to avoid bans.", "")
        return int(banned_until)


    # TODO: Rebuild
    def initialize(self):

        if self.client:
            try:
                self.account_info()
                self.mw.is_connected = True
            except (BinanceAPIException, NameError, AttributeError) as e:
                print("API ERROR")
                print(str(e))
                if "code=-1003" in str(e):
                    print("ja ein api error :)")

                    self.banned_until = self.get_ban_duration(e)
                    self.error = "banned"
                elif "code=-2014" in str(e):

                    print("API KEY INVALID")
                    api_key = self.mw.cfg_manager.api_key
                    api_secret = self.mw.cfg_manager.api_secret
                    print("key:", api_key, "secret:", api_secret)
                    if api_key == "" or api_secret == "" or api_key == "key" or api_secret == "secret":
                        self.error = "no-api-key"
                elif "code=0" in str(e):
                    print("BINANCE API DOWN!!!")
                elif "get_products" in str(e):
                    print("PUBLIC API DOWN")
                elif "code=-1021" in str(e):
                    print("ZEITFUCK")
                    self.error = "time"
        else:
            print("CLIENT NOT DEFINED! BANNED!")
            if not self.error == "no-api-key":
                self.error = "banned"

    def parse_error(self):
        if self.error == "time":
            self.mw.chart.setHtml(time_error_page())
        elif self.error == "no-api-key":
            self.mw.chart.setHtml(welcome_page())
            self.mw.gui_mgr.first_time_setup()
        else:
            # If there were no errors, display the chart of the current pair
            pair = self.mw.data.current.pair
            self.mw.chart.setHtml(Webpages.build_chart2(pair, self.mw.cfg_manager.defaultTimeframe))
            

    def getHoldings(self):
        """Make an inital API call to get BTC and coin holdings."""
        # API Call:
        order = self.client.get_account()
        accHoldings = dict()
        for i in range(len(order["balances"])):
            accHoldings[order["balances"][i]["asset"]] = {"free": order["balances"][i]["free"], "locked": order["balances"][i]["locked"]}

        return accHoldings


    def api_create_order(self, side, pair, price, amount, progress_callback):
        print("create order: " + str(price) + " " + str(amount))
        try:
            if side == "Buy":
                order = self.client.order_limit_buy(
                    symbol=pair,
                    quantity=str(amount),
                    price=str(price))


            elif side == "Sell":
                order = self.client.order_limit_sell(
                    symbol=pair,
                    quantity=str(amount),
                    price=str(price))

            print("order status: " + str(order))
            return order
        except BinanceAPIException as e:
            print("create order failed: " + str(e))
            print("side:", side, "symbol:", pair, "quantity", str(amount), "price", str(price))


    # TODO: This is work in progress;
    # Think of ways to verify websocket response time
    def api_cancel_order(self, order_id, symbol, progress_callback):
        print("cancel order " + str(symbol) + " " + str(order_id))
        try:
            self.client.cancel_order(symbol=symbol, orderId=order_id)
        except BinanceAPIException as e:
            print("cancel order failed:", e)
            if "APIError(code=-2011)" in str(e):
                print("orders seem out of sync, manually querying...")

                progress_callback.emit("query")


    def api_my_trades(self, pair, progress_callback=None):
        my_trades = self.client.get_my_trades(symbol=pair)
        if progress_callback:
            progress_callback.emit([my_trades, pair])
        else:
            return my_trades



    def api_all_orders(self, progress_callback=None):
        print("API ALL ORDERS")
        orders = self.client.get_open_orders()

        if progress_callback:
            progress_callback.emit(orders)
        else:
            print("api_all_orders blocking")
            return orders


    def cancel_order_byId(self, order_id, symbol):
        """Cancel an order by id from within a separate thread."""
        worker = Worker(partial(self.mw.api_manager.api_cancel_order, order_id, symbol))
        worker.signals.progress.connect(self.cancel_callback)
        self.threadpool.start(worker)


    def cancel_callback(self, order="empty"):
        if order == "query":
            print("CANCEL FAILED, doing manually")
            self.mw.open_orders_view.query_update()
            return
        
        print("SUCCESSFULLY CANCELLED ORDER: ", order)


    def exchange_info(self):
        info = self.client.get_exchange_info()
        return info

    def account_info(self):
        account_info = self.client.get_account()
        return account_info
