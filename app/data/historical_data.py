# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


import numpy as np
from binance.client import Client




class HistoricalData:
    """Fetch and store historical price data.
    Takes an optional list of pairs. Instantiate like this:
    historical = HistoricalData(["ADABTC", "TRXBTC"])

    And access numpy arrays like this:
    historical.data["BNBBTC"].tf["1m"][999]["time"]

    accepted keywords are:
    "time", "open", "high", "low", "close", "volume", "close time",
    "quote volume", "number trades", "asset volume" and "quote asset volume"
    """

    pairs = ["BNBBTC", "NEOBTC"]

    def __init__(self, client, pairs=pairs):
        """Initialize client and pairs; Mostly debug stuff."""

        self.client = self.init_client()

        self.pairs = pairs
        self.data = dict()
        self.process_pairs()


    def init_client(self):
        """Create a binance Client object."""

        key = "ws7MEQkmFBf6kJIFpUeCBDxPotoi5eUNodbNZTgJzMhw04p6jJjBkwu6dggTMmZm"
        secret = "FFArS2rojmCE9iRHX7k4cYaFuYySCH6doy5aMAPOz560YLj62tqPENBC5SShzvUQ"
        return Client(key, secret, {"verify": True, "timeout": 10})


    def get_kline(self, symbol, interval):
        """Make an API call to get historical candlestick data in list form."""

        print("gettting", symbol, interval)
        klines = self.client.get_klines(symbol=symbol, interval=interval)
        return klines


    def process_pairs(self):
        for pair in self.pairs:
            self.data[pair] = HistoricalPair(pair, self)


    def process_this(self, pair):
        # implement check if is valid
        self.data[pair] = HistoricalPair(pair, self)


""" WORK IN PROGRESS:
    def ordered_process(self):
        if current_pair in all_coins:
            self.process_this(current_pair)
            allcoins.find(current_pair).remove()

        for holding in holdings:
            if holding in all_coins:
                self.process_this(holding)
                allcoins.find(current_pair).remove()

        while len(all_coins) > 0:
            self.process_this(all_coins[0])
            all_coins[0].pop()
"""


class HistoricalPair:
    """Class that holds historical price information of a pair.
    Several timeframes are available including "1m", "5m" and "15m"
    """

    def __init__(self, pair, parent):
        self.pair = pair
        self.parent = parent
        timeframes = ["1m", "5m", "15m"]
        self.tf = dict()

        for timeframe in timeframes:
            klines = self.parent.get_kline(pair, timeframe)
            value_array = np.array([tuple(x) for x in klines], dtype=[
                ("time", "i8"),
                ("open", "f8"),
                ("high", "f8"),
                ("low", "f8"),
                ("close", "f8"),
                ("volume", "f8"),
                ("close time", "f8"),
                ("quote volume", "f8"),
                ("number trades", "f8"),
                ("asset volume", "f8"),
                ("quote asset volume", "f8"),
                ("ignore", "f8")])
            self.tf[timeframe] = value_array


def debug(self):
    self.client = "CLIENT"
    historical = HistoricalData(self.client, ["ADABTC", "TRXBTC"])
    print("#######")
    # print(historical.data["BNBBTC"].tf["1m"][999]["time"])

    historical.process_this("LTCBTC")

    print(historical.data["LTCBTC"].tf["1m"][999]["close"])
