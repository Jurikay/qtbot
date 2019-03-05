# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
import configparser
import os

from binance.exceptions import BinanceAPIException
from binance.client import Client

# from app.helpers import write_file


"""Methods that make use of the binance API."""

class ApiManager:

    """Api related methods."""

    def __init__(self, mw, client):

        self.client = client
        self.mw = mw
        self.data = mw.data

        self.store_initial_data()
        # return super().__init__(*args, **kwargs)

    def store_initial_data(self):
        """Makes inital api calls and stores received data in data class."""
        symbol = self.data.current.symbol
        print("NEW API MANAGER: storing data for:", symbol)

        self.data.set_depth(self.getDepth(symbol))
        self.data.set_tickers(self.get_tickers())
        self.data.set_hist(self.getTradehistory(symbol))


    def get_tickers(self):
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