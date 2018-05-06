# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


import pandas as pd
# import app
from PyQt5.QtCore import QObject as QObject
import numpy as np


class IndexData(QObject):
    """Create and update a pandas DataFrame with latest
    price data from various sources:
    Initial API call, websocket callbacks and calculated
    kline data."""

    def __init__(self, mw, parent=None):
        super(IndexData, self).__init__(parent)
        print("INIT IndexData")
        self.mw = mw
        # self.threadpool = tp

        # coin index DataFrame
        self.coin_index = None
        self.ticker_data = None
        self.filtered = None

        self.volumes = dict()

        self.initialize()
        self.mw.test_ud_btn.clicked.connect(self.calculate_historical)
        

    def initialize(self):
        print("INIT")
        self.ticker_data = self.mw.api_manager.getTickers()
        self.filtered = self.filter_tickers(self.ticker_data)

        df = pd.DataFrame.from_dict(self.filtered, orient='index')
        # print(df)
        self.coin_index = df


    def merge_df(self, update_data):
        filtered = self.filter_tickers(update_data)
        update_df = pd.DataFrame.from_dict(filtered, orient='index')
        self.coin_index.update(update_df)


    def filter_tickers(self, data):
        """Expects an dictionary containing dictionaries.
        Returns a dictonary with selected keys."""
        filtered = dict()
        for coin, values in data.items():
            if "USDT" not in coin:
                if self.volumes.get(coin):
                    vol_5m = self.volumes.get(coin)
                else:
                    vol_5m = 0

                filtered[coin] = {"Pair": str(values["symbol"]),
                                  "Price Change": float(values["priceChangePercent"]),
                                  "Price": float(values["lastPrice"]),
                                  "Volume": float(values["quoteVolume"]), "5m volume": vol_5m}

        return filtered


    def callback_calc(self, pair):
        vol_5 = self.get_sum(pair, 10)
        self.volumes[pair] = vol_5

    def calculate_historical(self):
        if self.ticker_data:
            for symbol in self.ticker_data:
                vol_5 = self.get_sum(symbol, 5)

                if vol_5:
                    print("set vol")
                    self.volumes[symbol] = vol_5


    def get_sum(self, symbol, lastx):
        try:
            aslice = self.mw.historical.data[symbol].tf["1m"][-lastx:]["quote volume"]
            suml = np.sum(aslice)
            # print(aslice)
            # print(suml)
            return suml
        except (AttributeError, KeyError) as e:
            print("SUM ERROR", e)
            return None
        
