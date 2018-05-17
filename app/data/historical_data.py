# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


import numpy as np
# from binance.client import Client
import PyQt5.QtCore as QtCore
from app.workers import Worker
from functools import partial
import time
from binance.exceptions import BinanceAPIException


class HistoricalData(QtCore.QObject):
    """Fetch and store historical price data.
    Takes an optional list of pairs; Instantiate like this:
    historical = HistoricalData(["ADABTC", "TRXBTC"])

    Access numpy arrays like this:
    historical.data["BNBBTC"].tf["1m"][999]["time"]

    accepted keywords are:
    "time", "open", "high", "low", "close", "volume", "close time",
    "quote volume", "number trades", "asset volume" and "quote asset volume"
    """

    # pairs = ["BNBBTC"]

    def __init__(self, mw, client, tp, parent=None):
        super(HistoricalData, self).__init__(parent)

        self.mw = mw
        self.threadpool = tp
        self.client = client

        self.pairs = ["BNBBTC"]

        self.data = dict()
        # self.process_pairs()
        self.process_in_thread(self.mw.cfg_manager.pair)



    def get_kline_values(self):
        worker = Worker(self.test_all)
        self.mw.threadpool.start(worker)


    def get_kline(self, symbol, interval):
        """Make an API call to get historical candlestick data in list form."""

        # print("gettting", symbol, interval)
        klines = self.client.get_klines(symbol=symbol, interval=interval)
        return klines


    def process_pairs(self):
        for pair in self.pairs:
            self.data[pair] = HistoricalPair(pair, self)


    def process_this(self, pair, progress_callback=None):
        # print("getting historical", pair)
        # implement check if is valid
        self.data[pair] = HistoricalPair(pair, self)
        progress_callback.emit(pair)

    def test_all(self, progress_callback=None):
        while True:
            # print("GETTING ALL PAIRS")
            try:
                # current_coin = self.mw.cfg_manager.pair
                ticker_data = self.mw.api_manager.getTickers()
                pairs = list(ticker_data)
                pair_count = 0

                for pair in pairs:
                    if "BTC" in pair:
                        pair_count += 1
                        self.process_in_thread(pair)
                    time.sleep(0.1)
                time.sleep(15)
            except BinanceAPIException as e:
                print("TEST ALL ERROR:", e)

    def process_in_thread(self, pair):
        worker = Worker(partial(self.process_this, pair))
        worker.signals.progress.connect(self.mw.index_data.callback_calc)
        self.mw.threadpool.tryStart(worker)


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

        self.parent = parent
        timeframes = ["1m"]
        self.tf = dict()
        self.get_klines(timeframes, pair)

    def get_klines(self, timeframes, pair):
        for timeframe in timeframes:
            try:
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
            except BinanceAPIException:
                print("BINANCE API EXCEPTION!!!")
