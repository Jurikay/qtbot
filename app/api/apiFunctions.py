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


class ApiCalls:
    """Collection of api related methods."""
    def __init__(self, mw, tp):
        self.mw = mw

        self.threadpool = tp
        self.banned_until = None
        self.error = None
        self.client = self.authenticate_client()
        app.client = self.client

        self.initialize()


        self.counter = 0
        # self.api_calls_counter = 0


    def authenticate_client(self):
        print("Authenticate client")
        try:
            api_key = self.mw.cfg_manager.api_key
            api_secret = self.mw.cfg_manager.api_secret
        except Exception as e:
            print("api key/secret not found!")
            print(e)
            return
        
        try:
            return Client(api_key, api_secret, {"verify": True, "timeout": 10})
        except BinanceAPIException as e:
            if "IP banned until" in str(e):
                self.banned_until = str(self.get_ban_duration(e))
        


    # Either move out or at least improve drastically
    def init_client(self):
        try:
            api_key = self.mw.cfg_manager.api_key
            api_secret = self.mw.cfg_manager.api_secret
            print("CREATE CLIENT")
            return Client(api_key, api_secret, {"verify": True, "timeout": 10})
        
        except BinanceAPIException as e:
            if "IP banned until" in str(e):
                self.banned_until = str(self.get_ban_duration(e))
                self.error = "banned"
            return None


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
                elif "code=0" in str(e):
                    print("BINANCE API DOWN!!!")
                elif "get_products" in str(e):
                    print("PUBLIC API DOWN")
                elif "code=-1021" in str(e):
                    print("ZEITFUCK")
                    self.error = "time"
            

        else:
            print("CLIENT NOT DEFINED! BANNED!")
            self.error = "banned"


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


    # def api_order_history(self, pair, progress_callback):
    #     orders = self.client.get_all_orders(symbol=pair)
    #     progress_callback.emit(orders)
        # self.api_calls_counter += 1

    def api_my_trades(self, pair, progress_callback=None):
        my_trades = self.client.get_my_trades(symbol=pair)
        if progress_callback:
            progress_callback.emit([my_trades, pair])
        else:
            return my_trades

    def api_history(self, progress_callback):
        trade_history = self.getTradehistory(self.mw.data.current.pair)
        progress_callback.emit({"history": list(reversed(trade_history))})
        # self.api_calls_counter += 1


    def api_depth(self, progress_callback):
        depth = self.getDepth(self.mw.data.current.pair)
        progress_callback.emit(depth)




    def api_all_orders(self, progress_callback=None):
        print("API ALL ORDERS")
        orders = self.client.get_open_orders()

        if progress_callback:
            progress_callback.emit(orders)
        else:
            print("api_all_orders blocking")
            return orders


    # Initial api calls old data;
    # TODO: Fully replace
    def api_calls(self):
        print("apiFunctions api_calls")
        """Initial and coin specific api calls"""
        

        worker = Worker(self.api_history)
        worker.signals.progress.connect(self.mw.live_data.batch_history)
        self.threadpool.start(worker)
        
        worker = Worker(self.api_depth)
        worker.signals.progress.connect(self.save_depth)

        # worker.signals.progress.connect(self.mw.live_data.batch_orderbook)
        # worker.signals.finished.connect(self.mw.limit_pane.t_complete)
        self.threadpool.start(worker)
        return
        # TODO: COme back to 
        # worker = Worker(self.mw.user_data.initial_history)
        # worker.signals.progress.connect(self.updateHistTable)
        # self.threadpool.start(worker)


        # self.get_trade_history(self.mw.data.current.pair)


    # Websocket history table update
    # TODO: Move out of apiFunctions
    def updateHistTable(self):
        print("apiFunctions update histTable")
        # self.mw.trade_history_view.websocket_update()

    def save_depth(self, depth):
        print("SET DEPTH")
        # print("save depth", depth)
        self.mw.data.set_depth(depth)
        # self.mw.orderbook = depth

        # self.mw.new_asks.setup()
        # self.mw.new_bids.setup()

        # self.mw.asks_view.setup()


    def get_trade_history(self, pair):
        worker = Worker(partial(self.api_my_trades, pair))
        worker.signals.progress.connect(self.mw.history_table.orders_received)
        self.mw.threadpool.start(worker)

    def get_kline(self, pair, progress_callback):
        """Make an API call to get historical data of a coin pair."""
        interval = "1m"
        # self.api_calls_counter += 1
        try:  # try since this is used heavily
            klines = self.client.get_klines(symbol=pair, interval=interval)
            progress_callback.emit([klines, pair, interval])

        except (ConnectionError, ReadTimeout) as e:
            print("KLINE ERROR: " + str(e))

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


#############################################################

    def new_api(self):
        print("NEW API CALLS <- blocking")
        # TODO Move to thread
        # btc_pairs = self.get_btc_pairs()
        # tickers = self.add_ticker_data(btc_pairs)


        # self.mw.data.set_tickers(tickers)



        # self.mw.tickers = tickers
        # api_calls += (self.all_pairs / 2)



    def exchange_info(self):
        info = self.client.get_exchange_info()
        return info

    def account_info(self):
        account_info = self.client.get_account()
        return account_info


    def get_btc_pairs(self):
        """Return a dictionary containing all BTC trade pairs.
        Calculate decimal values for every pair."""

        print("get_btc_pairs")
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
            if symbol_data["quoteAsset"] == "BTC" or symbol_data["symbol"] == "BTCUSDT":
                btc_pairs += 1
                pair = symbol_data["symbol"]

                coin_dict[pair] = dict()
                tickSize = str(symbol_data["filters"][0]["tickSize"])
                minTrade = str(symbol_data["filters"][2]["minQty"])
                decimals = self.calculate_decimals(tickSize, minTrade)
                coin_dict[pair]["decimals"] = decimals[0]
                coin_dict[pair]["assetDecimals"] = decimals[1]
                coin_dict[pair]["tickSize"] = tickSize.rstrip("0")
                coin_dict[pair]["minTrade"] = minTrade

        # self.all_pairs = all_pairs
        return coin_dict


    @staticmethod
    def calculate_decimals(tickSize, minTrade):
        """Returns asset and quote asset decimal precision. As integers"""
        decimals = len(str(tickSize.rstrip("0"))) - 2
        assetDecimals = len(str(minTrade.rstrip("0"))) - 2
        return [decimals, assetDecimals]


    def add_ticker_data(self, btc_pairs):
        # TODO change
        tickers = self.getTickers()
        coins = self.availablePairs()

        self.number_api_calls += 1


        for pair in btc_pairs:

            ticker_pair = tickers.get(pair)
            coin_name = coins.get(pair, dict()).get("baseAssetName", "-")
            for item in ticker_pair.items():
                btc_pairs[pair][item[0]] = item[1]
            btc_pairs[pair]["baseAssetName"] = coin_name

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
