# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


import pandas as pd
# import app
from PyQt5.QtCore import QObject as QObject
import numpy as np
import time


class IndexData(QObject):
    """Create and update a pandas DataFrame with latest
    price data from various sources:
    Initial API call, websocket callbacks and calculated
    kline data."""

    volumes = [5, 15, 60, 240, 720]

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
        self.differences = dict()

        self.initialize()
        # self.mw.test_ud_btn.clicked.connect(self.calculate_historical)
        

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
        timen = time.time()
        print("FILTER TICKERS")
        for coin, values in data.items():
            if "USDT" not in coin:
                if self.volumes.get(coin):
                    volumes = self.volumes.get(coin)
                    differences = self.differences.get(coin)
                else:
                    volumes = [0, 0, 0, 0, 0]
                    differences = [0, 0, 0, 0, 0]

                filtered[coin] = {"Pair": str(values["symbol"]),
                                  "Price Change": float(values["priceChangePercent"]),
                                  "Price": float(values["lastPrice"]),
                                  "Volume": float(values["quoteVolume"]),
                                  "5m volume": float(volumes[0]),
                                  "15m volume": float(volumes[1]),
                                  "1h volume": float(volumes[2]),
                                  "4h volume": float(volumes[3]),
                                  "12h volume": float(volumes[4]),
                                  "5m difference": float(differences[0]),
                                  "15m difference": float(differences[1]),
                                  "1h difference": float(differences[2]),
                                  "4h difference": float(differences[3]),
                                  "12h difference": float(differences[4])}
        print("filter took", timen - time.time())
        return filtered


    def callback_calc(self, pair, volumes=volumes):
        """Callback from historical data."""
        volume_sums = list()
        differences = list()
        for volume in volumes:
            volume_sum = self.get_sum(pair, volume)
            volume_sums.append(volume_sum)
            difference = self.get_difference(pair, volume)
            differences.append(difference)
        # vol_5 = self.get_sum(pair, 10)
        self.volumes[pair] = volume_sums
        self.differences[pair] = differences



    def get_sum(self, symbol, time):
        print("get sum")
        try:
            volume_slice = self.mw.historical.data[symbol].tf["1m"][-time:]["quote volume"]
            volume_sum = np.sum(volume_slice)

            return volume_sum
        except (AttributeError, KeyError) as e:
            print("SUM ERROR", e)
            return None

    def get_difference(self, symbol, time):
        print("get difference")
        historical_price = self.mw.historical.data[symbol].tf["1m"][-time]["close"]
        last_price = self.ticker_data[symbol]["lastPrice"]
        if historical_price != 0:
            difference = (float(last_price) / float(historical_price) - 1) * 100
            return difference
        else:
            return 0