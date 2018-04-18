# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
from functools import partial
from app.init import val
from binance.exceptions import BinanceAPIException
# from requests.exceptions import InvalidHeader
import app
from app.workers import Worker
# from app.initApi import set_pair_values
from binance.client import Client


class ApiCalls:
    """Class containing api related methods."""
    def __init__(self, mw):
        self.mw = mw

        self.client = Client(val["api_key"], val["api_secret"], {"verify": True, "timeout": 61})

        app.client = self.client

    def initialize(self):

        # print("setting client: " + str(self.client))

        try:
            val["coins"] = self.availablePairs(self.client)

            val["accHoldings"] = self.getHoldings(self.client)

            # val["tether"] = get_tether(self.client)

            val["tickers"] = self.getTickers(self.client)

            val["apiCalls"] += 3
            # userMsg = dict()
            # accHoldings = dict()

            self.set_pair_values()
        except (BinanceAPIException, NameError) as e:
            print("API ERROR")
            print(str(e))
            if "code=-1003" in str(e):
                print("ja ein api error :)")



    # def get_tether(client):
    #     tether_info = client.get_ticker(symbol="BTCUSDT")
    #     return tether_info
    @staticmethod
    def set_pair_values():
        """Set various values based on the chosen pair."""
        val["coin"] = val["pair"][:-3]
        val["decimals"] = len(str(val["coins"][val["pair"]]["tickSize"])) - 2

        if int(val["coins"][val["pair"]]["minTrade"]) == 1:
            val["assetDecimals"] = 0
        else:
            val["assetDecimals"] = len(str(val["coins"][val["pair"]]["minTrade"])) - 2


    @classmethod
    def availablePairs(self, client):
        """
        Create a dictonary containing all BTC tradepairs excluding USDT.

        Keys are:
        {'symbol': 'ETHBTC', 'tradedMoney': 3024.89552855, 'baseAssetUnit': 'Ξ', 'active': True, 'minTrade': '0.00100000', 'baseAsset': 'ETH', 'activeSell': 66254.102, 'withdrawFee': '0', 'tickSize': '0.000001', 'prevClose': 0.044214, 'activeBuy': 0, 'volume': '66254.102000', 'high': '0.047998', 'lastAggTradeId': 2809764, 'decimalPlaces': 8, 'low': '0.043997', 'quoteAssetUnit': '฿', 'matchingUnitType': 'STANDARD', 'close': '0.047656', 'quoteAsset': 'BTC', 'open': '0.044214', 'status': 'TRADING', 'minQty': '1E-8'}
        """
        # create a local dictionary
        coins = dict()

        # API Call
        products = client.get_products()

        # For every entry in API answer:
        for i, pair in enumerate(products["data"]):

            # Check if pair contains BTC, does not contain USDT and if volume is >0
            if "BTC" in pair["symbol"] and "USDT" not in pair["symbol"] and float(products["data"][i]["volume"]) > 0.0:
                # Create a temporary dictionary to store keys and values
                tempdict = dict()

                # Add every key-value pair to the temp dictionary
                for key, value in pair.items():
                    tempdict[key] = value
                # Add every temp dictionary to the coin dictionary
                coins[tempdict["symbol"]] = tempdict

        return coins


    @classmethod
    def getHoldings(self, client):
        """Make an inital API call to get BTC and coin holdings."""
        # API Call:
        order = client.get_account()
        accHoldings = dict()
        for i in range(len(order["balances"])):
            accHoldings[order["balances"][i]["asset"]] = {"free": order["balances"][i]["free"], "locked": order["balances"][i]["locked"]}

        return accHoldings

    @classmethod
    def getTickers(self, client):
        """Make an initial API call to get ticker data."""
        ticker = client.get_ticker()
        # print(str(ticker))
        all_tickers = dict()
        for _, ticker_data in enumerate(ticker):
            if "BTC" in ticker_data["symbol"]:
                # print(str(ticker_data))
                all_tickers[ticker_data["symbol"]] = ticker_data

        return all_tickers


    @classmethod
    def getTradehistory(self, client, pair):
        """Make an initial API call to get the trade history of a given pair. This is used until updated by websocket data."""
        # API call
        globalList = list()
        trades = client.get_aggregate_trades(symbol=pair, limit=50)
        for _, trade in enumerate(reversed(trades)):
            globalList.insert(0, {"price": str(trade["p"]), "quantity": str(trade["q"]), "maker": bool(trade["m"]), "time": str(trade["T"])})

        return list(reversed(globalList))


    @classmethod
    def getDepth(self, client, symbol):
        """Make an initial API call to get market depth (bids and asks)."""
        # API Call
        depth = client.get_order_book(symbol=symbol, limit=20)

        asks = depth["asks"]
        bids = depth["bids"]
        return {"bids": bids, "asks": asks}


    @classmethod
    def api_create_order(self, client, side, pair, price, amount, progress_callback):
        print("create order: " + str(price) + " " + str(amount))
        try:
            if side == "Buy":
                order = client.order_limit_buy(
                    symbol=pair,
                    quantity=str(amount),
                    price=str(price))


            elif side == "Sell":
                order = client.order_limit_sell(
                    symbol=pair,
                    quantity=str(amount),
                    price=str(price))
            return order
        except BinanceAPIException:
            print("create order failed")


    @classmethod
    def api_cancel_order(self, client, order_id, symbol, progress_callback):
        print("cancel order " + str(symbol) + " " + str(order_id))
        try:
            client.cancel_order(symbol=symbol, orderId=order_id)
        except BinanceAPIException:
            print("cancel failed")

    @classmethod
    def api_order_history(self, pair, progress_callback):
        orders = app.client.get_all_orders(symbol=pair)
        progress_callback.emit(orders)
        val["apiCalls"] += 1


    def api_history(self, progress_callback):
        val["globalList"] = self.getTradehistory(self.client, val["pair"])
        progress_callback.emit({"history": reversed(val["globalList"])})
        val["apiCalls"] += 1


    def api_depth(self, progress_callback):
        depth = self.getDepth(self.client, val["pair"])
        val["asks"] = depth["asks"]
        progress_callback.emit({"asks": val["asks"]})
        val["bids"] = depth["bids"]
        progress_callback.emit({"bids": val["bids"]})
        val["apiCalls"] += 1




    def api_all_orders(self, progress_callback):
        print("CLEINT;" + str(self.client))
        orders = self.client.get_open_orders()
        progress_callback.emit(orders)
        numberPairs = sum(val["pairs"].values())
        print("number pairs: " + str(numberPairs))


    def api_calls(self):
        """Inital and coin specific api calls"""
        worker = Worker(self.api_history)
        worker.signals.progress.connect(self.mw.live_data.progress_fn)
        self.mw.threadpool.start(worker)

        worker = Worker(self.api_depth)
        worker.signals.progress.connect(self.mw.live_data.progress_fn)
        worker.signals.finished.connect(self.mw.limit_pane.t_complete)
        self.mw.threadpool.start(worker)

        self.get_trade_history(val["pair"])


    def get_trade_history(self, pair):
        worker = Worker(partial(self.api_order_history, pair))
        worker.signals.progress.connect(self.mw.history_table.orders_received)
        self.mw.threadpool.start(worker)

    def get_kline(self, pair, progress_callback):
        """Make an API call to get historical data of a coin pair."""
        interval = "1m"

        klines = self.client.get_klines(symbol=pair, interval=interval)
        # progress_callback.emit([klines, pair, interval])
        progress_callback.emit([klines, pair, interval])
        val["apiCalls"] += 1
