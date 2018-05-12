# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""A collection of methods that rely on the Python-Binance API
implementation to communicate with Binance."""

from functools import partial
from app.init import val
from binance.exceptions import BinanceAPIException
# from requests.exceptions import InvalidHeader
import app
from app.workers import Worker
# from app.initApi import set_pair_values
from binance.client import Client
from requests.exceptions import ReadTimeout
import time


class ApiCalls:
    """Collection of api related methods."""
    def __init__(self, mw, tp):
        self.mw = mw

        self.threadpool = tp
        self.banned_until = None
        self.error = None
        self.client = self.init_client()
        app.client = self.client

        self.counter = 0

    def init_client(self):
        try:
            api_key = self.mw.cfg_manager.api_key
            api_secret = self.mw.cfg_manager.api_secret
            return Client(api_key, api_secret, {"verify": True, "timeout": 10})
        except BinanceAPIException as e:
            if "IP banned until" in str(e):
                print("first")
                self.banned_until = str(self.get_ban_duration(e))
                self.error = "banned"
            return None


    def get_ban_duration(self, error_msg):
        banned_until = str(error_msg).replace("APIError(code=-1003): Way too many requests; IP banned until ", "").replace(". Please use the websocket for live updates to avoid bans.", "")
        return int(banned_until)

    def initialize(self):

        if self.client:
            try:
                # print("get account:", self.client.get_account())
                # print("get account status:", self.client.get_account_status())

                

                val["coins"] = self.availablePairs()

                val["accHoldings"] = self.getHoldings()

                val["tickers"] = self.getTickers()

                val["apiCalls"] += 3
                # userMsg = dict()
                # accHoldings = dict()

                self.set_pair_values()
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
                elif "code=0" in str(e):
                    print("BINANCE API DOWN!!!")
                elif "get_products" in str(e):
                    print("PUBLIC API DOWN")

        else:
            print("CLIENT NOT DEFINED! BANNED!")
            self.error = "banned"
    # def get_tether(client):
    #     tether_info = client.get_ticker(symbol="BTCUSDT")
    #     return tether_info


    # TODO remove val references
    def set_pair_values(self):
        """Set various values based on the chosen pair."""
        pair = self.mw.cfg_manager.pair
        val["decimals"] = len(str(val["coins"][pair]["tickSize"])) - 2
        self.mw.decimals = len(str(val["coins"][pair]["tickSize"])) - 2
        if int(val["coins"][pair]["minTrade"]) == 1:
            val["assetDecimals"] = 0
            self.mw.assetDecimals = 0
        else:
            val["assetDecimals"] = len(str(val["coins"][pair]["minTrade"])) - 2
            self.mw.assetDecimals = len(str(val["coins"][pair]["minTrade"])) - 2


    # TODO: replace; get_products is depreciated.
    def availablePairs(self):
        """
        Create a dictonary containing all BTC tradepairs excluding USDT.

        Keys are:
        {'symbol': 'ETHBTC', 'tradedMoney': 3024.89552855, 'baseAssetUnit': 'Ξ', 'active': True, 'minTrade': '0.00100000', 'baseAsset': 'ETH', 'activeSell': 66254.102, 'withdrawFee': '0', 'tickSize': '0.000001', 'prevClose': 0.044214, 'activeBuy': 0, 'volume': '66254.102000', 'high': '0.047998', 'lastAggTradeId': 2809764, 'decimalPlaces': 8, 'low': '0.043997', 'quoteAssetUnit': '฿', 'matchingUnitType': 'STANDARD', 'close': '0.047656', 'quoteAsset': 'BTC', 'open': '0.044214', 'status': 'TRADING', 'minQty': '1E-8'}
        """
        # create a local dictionary
        coins = dict()

        # API Call
        products = self.client.get_products()
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


    def getHoldings(self):
        """Make an inital API call to get BTC and coin holdings."""
        # API Call:
        order = self.client.get_account()
        accHoldings = dict()
        for i in range(len(order["balances"])):
            accHoldings[order["balances"][i]["asset"]] = {"free": order["balances"][i]["free"], "locked": order["balances"][i]["locked"]}

        return accHoldings

    def getTickers(self):
        """Make an initial API call to get ticker data."""

        ticker = self.client.get_ticker()
        # print(str(ticker))
        all_tickers = dict()
        for ticker_data in ticker:
            if "BTC" in ticker_data["symbol"]:
                # print(str(ticker_data))
                all_tickers[ticker_data["symbol"]] = ticker_data

        return all_tickers


    def getTradehistory(self, pair):
        """Make an initial API call to get the trade history of a given pair. This is used until updated by websocket data."""
        # API call
        globalList = list()
        trades = self.client.get_aggregate_trades(symbol=pair, limit=50)
        for trade in (reversed(trades)):
            globalList.insert(0, {"price": str(trade["p"]), "quantity": str(trade["q"]), "maker": bool(trade["m"]), "time": str(trade["T"])})

        return globalList


    def getTrades(self, pair):
        """Return trade history unmodified."""
        trades = self.client.get_aggregate_trades(symbol=pair, limit=50)
        return trades

    def getDepth(self, symbol):
        """Make an initial API call to get market depth (bids and asks)."""
        # API Call
        depth = self.client.get_order_book(symbol=symbol, limit=20)

        asks = depth["asks"]
        bids = depth["bids"]
        return {"bids": bids, "asks": asks}



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



    def api_cancel_order(self, client, order_id, symbol, progress_callback):
        print("cancel order " + str(symbol) + " " + str(order_id))
        try:
            self.client.cancel_order(symbol=symbol, orderId=order_id)
        except BinanceAPIException:
            print("cancel failed")


    def api_order_history(self, pair, progress_callback):
        orders = self.client.get_all_orders(symbol=pair)
        progress_callback.emit(orders)
        val["apiCalls"] += 1

    def api_my_trades(self, pair, progress_callback=None):
        my_trades = self.client.get_my_trades(symbol=pair)
        
        if progress_callback:
            progress_callback.emit([my_trades, pair])
        else:
            return my_trades

    def api_history(self, progress_callback):
        trade_history = self.getTradehistory(self.mw.cfg_manager.pair)
        progress_callback.emit({"history": list(reversed(trade_history))})
        val["apiCalls"] += 1


    def api_depth(self, progress_callback):
        depth = self.getDepth(self.mw.cfg_manager.pair)
        progress_callback.emit(depth)
    



    def api_all_orders(self, progress_callback=None):
        orders = self.client.get_open_orders()

        if progress_callback:
            progress_callback.emit(orders)
        else:
            return orders
        

    def api_calls(self):
        """Initial and coin specific api calls"""
        worker = Worker(self.api_history)
        worker.signals.progress.connect(self.mw.live_data.batch_history)
        self.mw.threadpool.start(worker)

        worker = Worker(self.api_depth)
        worker.signals.progress.connect(self.save_depth)
        
        # worker.signals.progress.connect(self.mw.live_data.batch_orderbook)
        # worker.signals.finished.connect(self.mw.limit_pane.t_complete)
        self.mw.threadpool.start(worker)

        self.get_trade_history(self.mw.cfg_manager.pair)


    def save_depth(self, depth):
        # print("save depth", depth)
        self.mw.orderbook = depth
        self.mw.new_asks.setup()
        self.mw.new_bids.setup()


    def get_trade_history(self, pair):
        worker = Worker(partial(self.api_my_trades, pair))
        worker.signals.progress.connect(self.mw.history_table.orders_received)
        self.mw.threadpool.start(worker)

    def get_kline(self, pair, progress_callback):
        """Make an API call to get historical data of a coin pair."""
        interval = "1m"
        val["apiCalls"] += 1
        try:  # try since this is used heavily
            klines = self.client.get_klines(symbol=pair, interval=interval)
            progress_callback.emit([klines, pair, interval])

        except (ConnectionError, ReadTimeout) as e:
            print("KLINE ERROR: " + str(e))

    def cancel_order_byId(self, order_id, symbol):
        """Cancel an order by id from within a separate thread."""
        worker = Worker(partial(self.mw.api_manager.api_cancel_order, app.client, order_id, symbol))
        # worker.signals.progress.connect(self.cancel_callback)
        self.threadpool.start(worker)


#############################################################

    def new_api(self):
        print("NEW API CALLS")
        api_calls = 1
        btc_pairs = self.get_btc_pairs()

        tickers = self.add_ticker_data(btc_pairs)
        self.mw.tickers = tickers
        api_calls += (self.all_pairs / 2)



    def exchange_info(self):
        info = self.client.get_exchange_info()
        return info


    def get_btc_pairs(self):
        """Return a dictionary containing all BTC trade pairs.
        Calculate decimal values for every pair."""

        print("NEW API")
        coin_dict = dict()
        all_pairs = 0
        btc_pairs = 0
        self.number_api_calls = 0
        # self.number
        info = self.exchange_info()
        self.number_api_calls += 1
        for symbol_data in info["symbols"]:
            all_pairs += 1
            # print("SYMBOL DATA", symbol_data)
            if symbol_data["quoteAsset"] == "BTC":
                btc_pairs += 1
                pair = symbol_data["symbol"]

                coin_dict[pair] = dict()
                tickSize = str(symbol_data["filters"][0]["tickSize"])
                minTrade = str(symbol_data["filters"][1]["minQty"])
                decimals = self.calculate_decimals(tickSize, minTrade)
                coin_dict[pair]["decimals"] = decimals[0]
                coin_dict[pair]["assetDecimals"] = decimals[1]
                coin_dict[pair]["tickSize"] = tickSize.rstrip("0")

        self.all_pairs = all_pairs
        # print("ALL PAIRS", all_pairs)
        # self.request_open_orders(coin_dict)
        return coin_dict


    def calculate_decimals(self, tickSize, minTrade):
        """Returns asset and quote asset decimal precision."""
        decimals = len(str(tickSize.rstrip("0"))) - 2
        assetDecimals = len(str(minTrade.rstrip("0"))) - 2
        return [decimals, assetDecimals]


    def add_ticker_data(self, btc_pairs):
        # TODO change
        tickers = val["tickers"]
        self.number_api_calls += 1


        for pair in btc_pairs:
            # print("allpairs", pair)

            ticker_pair = tickers.get(pair)
            for item in ticker_pair.items():
                # print("ITEM", item)
                btc_pairs[pair][item[0]] = item[1]
            # print("TICKER PAIR", ticker_pair)

        # print(btc_pairs)
        return btc_pairs


    def request_open_orders(self, coin_dict):
        # order_dict = dict
        self.start_time = time.time()
        for pair in coin_dict:
            self.counter += 1
            # print(pair)
            # print(type(pair))
            # orders = self.client.get_open_orders(symbol=pair)
            worker = Worker(partial(self.requests_per_pair, pair))
            worker.signals.progress.connect(self.requests_callback)
            self.threadpool.start(worker)
            # order_dict[pair] = orders
        print("DONE")


    def requests_per_pair(self, pair, progress_callback):
        trades = self.client.get_recent_trades(symbol=pair)
        progress_callback.emit([pair, trades])

    def requests_callback(self, payload):
        # print("callbakc received")
        self.counter -= 1
        # print(self.counter)
        # print(payload)
        # print("################")

        if self.counter == 0:
            print("FINISHED")
            print(self.start_time - time.time())