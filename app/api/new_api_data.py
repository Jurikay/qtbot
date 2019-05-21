# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
import configparser
import os

from binance.exceptions import BinanceAPIException
from binance.client import Client

from app.workers import Worker
# from app.helpers import write_file
from functools import partial

"""Methods that make use of the binance API."""

class ApiManager:

    """Api related methods."""

    def __init__(self, mw, client, tp):

        self.client = client
        self.mw = mw
        self.data = mw.data
        print("NEW API MGR")
        self.store_initial_data()
        self.threadpool = tp

        # return super().__init__(*args, **kwargs)

    def store_initial_data(self):
        """Makes inital api calls and stores received data in data class."""
        # Move to threads maybe
        self.data.set_tickers(self.get_tickers())
        # self.get_acc_info()

        print("PRODUCT INFO#######")
        products = self.products_info()
        pair_info = self.pair_info()
        

        self.data.set_info(products, pair_info)
        # self.data.set
        self.store_pair_data()

    def store_pair_data(self, progress_callback=None):
        """This is called whenever the current pair is changed."""
        symbol = self.data.current.pair

        print("store_pair_data:", symbol)

        self.data.set_hist(self.getTradehistory(symbol))

        self.data.set_depth(self.getDepth(symbol))

        # !new trade history update
        self.mw.user_data.initial_history()
        self.mw.user_data.initial_holdings()
        

        if progress_callback:
            progress_callback.emit(1)


    def threaded_pair_update(self):
        print("Threaded pair update:")
        worker = Worker(self.store_pair_data)
        worker.signals.progress.connect(self.set_thread)
        self.threadpool.start(worker)


    def set_thread(self, callback):
        print("CALLBACK:", callback)
        self.mw.tradeTable.update()
        self.mw.new_asks.update()
        self.mw.new_bids.update()

        # !new update
        self.mw.trade_history_view.update()
        self.mw.holdings_view.update()


    # Debug; Testing only, TODO: Replace
    def get_acc_info(self):
        print("GET ACC INFO")
        info = self.client.get_account()


        balance = self.client.get_asset_balance(asset='BTC')
        print("balance#############")
        print(balance)
        print()

        details = self.client.get_asset_details()
        print("details#############")
        print(details)
        print()

    def get_tickers(self):
        print("new api get_tickers")
        """Make an initial API call to get ticker data."""

        ticker = self.client.get_ticker()  # API call
        return ticker

        # all_tickers = dict()
        # for ticker_data in ticker:
        #     if "BTC" in ticker_data["symbol"]:
        #         all_tickers[ticker_data["symbol"]] = ticker_data

        # return all_tickers

    def getDepth(self, symbol):
        """Make an initial API call to get market depth (bids and asks)."""
        depth = self.client.get_order_book(symbol=symbol, limit=20)  # API Call
        return depth

    def getTradehistory(self, symbol):
        """Make an initial API call to get the trade history of a given pair.
        This is used until updated by websocket data."""
        # API call
        tradelist = list()
        trades = self.client.get_aggregate_trades(symbol=symbol, limit=50)
        for trade in (reversed(trades)):
            tradelist.insert(0, {"price": str(trade["p"]), "quantity": str(trade["q"]), "maker": bool(trade["m"]), "time": str(trade["T"])})

        return tradelist
    
    def products_info(self):
        """Get static information of every trade pair.
        The get_products() api call is marked obsolote, but some information like base and quoteAssetName
        are only available here."""
        products = self.client.get_products()
        
        product_dict = dict()

        # Restructure data so that the pair serves as index
        for product in products["data"]:
            product_dict[product["symbol"]] = product

        return product_dict


    def pair_info(self):
        """Extract relevant information from get_exchange_info api call.
        Return a dictionary containing all BTC trade pairs.
        Calculate decimal values for every pair."""

        coin_dict = dict()

        # API Call
        info = self.client.get_exchange_info()

        for symbol_data in info["symbols"]:
            pair = symbol_data["symbol"]


            coin_dict[pair] = dict()
            tickSize = str(symbol_data["filters"][0]["tickSize"])
            minTrade = str(symbol_data["filters"][2]["minQty"])

            decimals = len(str(tickSize.rstrip("0"))) - 2
            assetDecimals = len(str(minTrade.rstrip("0"))) - 2

            # It is not really necessary to calculate these 'filters' manually but the
            # API call to retrieve these (get_products) is marked obsolete so it does not hurt do do it anyway.
            coin_dict[pair]["decimals"] = decimals
            coin_dict[pair]["assetDecimals"] = assetDecimals
            coin_dict[pair]["tickSize"] = tickSize.rstrip("0")
            coin_dict[pair]["minTrade"] = minTrade

        return coin_dict
    
    # Currently unused
    def initial_tickers(self):
        """This is a temporary method that is used to fix a race condition.
        Get btc price data before ticker websocket data arrives."""
        tickers = self.get_tickers()

        self.data.set_tickers(tickers)

