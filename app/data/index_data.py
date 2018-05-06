# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


import pandas as pd
# import app
from PyQt5.QtCore import QObject as QObject
import numpy as np
import time
from app.workers import Worker
from functools import partial


class IndexData(QObject):
    """Create and update a pandas DataFrame with latest
    price data from various sources:
    Initial API call, websocket callbacks and calculated
    kline data."""

    volumes = [6, 16, 61]

    def __init__(self, mw, tp, parent=None):
        super(IndexData, self).__init__(parent)
        print("INIT IndexData")
        self.mw = mw
        # self.threadpool = tp

        # coin index DataFrame
        self.coin_index = None
        self.ticker_data = None
        self.filtered = None

        self.volumes = dict()
        self.changes = dict()

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

        # worker = Worker(partial(self.filter_tickers, update_data))
        # worker.signals.progress.connect(self.filter_callback)
        # self.mw.threadpool.start(worker)


    def filter_callback(self, filtered):
        update_df = pd.DataFrame.from_dict(filtered, orient='index')
        self.coin_index.update(update_df)


    def filter_tickers(self, data, progress_callback=None):
        """Expects an dictionary containing dictionaries.
        Returns a dictonary with selected keys."""
        filtered = dict()
        # timen = time.time()
        # print("FILTER TICKERS")
        for coin, values in data.items():
            if "USDT" not in coin:
                if self.volumes.get(coin):
                    volumes = self.volumes.get(coin)
                    changes = self.changes.get(coin)
                else:
                    volumes = [0, 0, 0]
                    changes = [0, 0, 0]

                filtered[coin] = {"Pair": str(values["symbol"]),
                                  "Price": float(values["lastPrice"]),
                                  "24h Change": float(values["priceChangePercent"]),
                                  "24h Volume": float(values["quoteVolume"]),
                                  "5m Volume": float(volumes[0]),
                                  "15m Volume": float(volumes[1]),
                                  "1h Volume": float(volumes[2]),
                                  # "4h volume": float(volumes[3]),
                                  # "12h volume": float(volumes[4]),
                                  "5m Change": float(changes[0]),
                                  "15m Change": float(changes[1]),
                                  "1h Change": float(changes[2]),
                                  # "4h difference": float(differences[3]),
                                  # "12h difference": float(differences[4])
                                  }
        # print("filter took", timen - time.time())
        # return filtered
        if progress_callback:
            progress_callback.emit(filtered)
        else:
            return filtered

    def callback_calc(self, pair, volumes=volumes):
        """Callback from historical data."""
        volume_sums = list()
        changes = list()
        for volume in volumes:
            volume_sum = self.get_sum(pair, volume)
            volume_sums.append(volume_sum)
            difference = self.get_difference(pair, volume)
            changes.append(difference)

        self.volumes[pair] = volume_sums
        self.changes[pair] = changes



    def get_sum(self, symbol, time_delta):
        try:
            volume_slice = self.mw.historical.data[symbol].tf["1m"][-time_delta:]["quote volume"]
            volume_sum = np.sum(volume_slice)

            return volume_sum
        except KeyError as e:
            print("get sum key error:", e)
            return 0


    def get_difference(self, symbol, time_delta):
        try:
            historical_price = self.mw.historical.data[symbol].tf["1m"][-time_delta]["close"]
            last_price = self.ticker_data[symbol]["lastPrice"]
            hist_formatted = '{number:.{digits}f}'.format(number=float(historical_price), digits=8)
            if historical_price != 0:
                difference = (float(last_price) / float(historical_price) - 1) * 100
                return difference
            else:
                return 0
        except KeyError as e:
            print("get difference key error", e)
            return 0
