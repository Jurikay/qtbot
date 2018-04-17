# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
# import PyQt5.QtGui as QtGui
import time
from functools import partial
from app.workers import Worker
from app.init import val
import app


class KlineManager():

    def __init__(self):
        # self.mw = mw
        self.client = app.client
    #     self.threadpool2 = QtCore.QThreadPool()
    #     self.threadpool = app.threadpool

    @classmethod    
    def rec_func(self):
        print("CALLBACK WHOOP")

    # kline data coin index
    def start_kline_check(self):
        print("start kline check")
        worker = Worker(self.schedule_kline_check)
        # worker.signals.progress.connect(self.rec_func)
        self.threadpool.start(worker)

    def start_kline_iterator(self):
        worker = Worker(self.iterate_through_klines)
        worker.signals.progress.connect(self.draw_kline_changes)
        self.threadpool.start(worker)

    def schedule_kline_check(self, progress_callback):
        print("schedule kline check")
        maxThreads = self.threadpool.maxThreadCount()
        if maxThreads <= 2:
            sleepTime = 1
        elif maxThreads <= 4:
            sleepTime = 0.33
            longSleep = 30
        else:
            sleepTime = 0.15
            longSleep = 15

        # kline api call loop
        while True:
            print("Spawning api call workers")
            for i in val["coins"]:
                time.sleep(sleepTime)
                worker = Worker(partial(self.api_manager.get_kline, str(i)))
                worker.signals.progress.connect(self.klines_received)
                self.threadpool.tryStart(worker)

            time.sleep(longSleep)


    # wip
    @classmethod
    def iterate_through_klines(self, progress_callback):
        """Iterate through the global klines dict and calculate values based on historical data."""
        for i, kline in enumerate(dict(val["klines"]["1m"])):
            coin = kline.replace("BTC", "")
            # items = self.coin_index.findItems(coin, QtCore.Qt.MatchExactly)
            change_dict = dict()

            new_volume_1m_value = 0
            new_volume_5m_value = 0
            new_volume_15m_value = 0
            new_volume_1h_value = 0

            new_volume_1m_value = float(val["klines"]["1m"][kline][-1][7])

            # sum up 1m volume up to 1 hour.
            for minute in range(60):
                if minute < 6:
                    new_volume_5m_value += float(val["klines"]["1m"][kline][-(1 + minute)][7])
                if minute < 16:
                    new_volume_15m_value += float(val["klines"]["1m"][kline][-(1 + minute)][7])

                # sum 60 minutes to get 1 hour volume
                new_volume_1h_value += float(val["klines"]["1m"][kline][-(1 + minute)][7])

            new_change_5m_value = ((float(val["tickers"][kline]["lastPrice"]) / float(val["klines"]["1m"][kline][-5][4])) - 1) * 100
            new_change_15m_value = ((float(val["tickers"][kline]["lastPrice"]) / float(val["klines"]["1m"][kline][-15][4])) - 1) * 100
            new_change_1h_value = ((float(val["tickers"][kline]["lastPrice"]) / float(val["klines"]["1m"][kline][-60][4])) - 1) * 100

            change_dict[6] = new_volume_1m_value
            change_dict[7] = new_volume_5m_value
            change_dict[8] = new_volume_15m_value
            change_dict[9] = new_volume_1h_value
            change_dict[10] = new_change_5m_value
            change_dict[11] = new_change_15m_value
            change_dict[12] = new_change_1h_value

            progress_callback.emit({coin: change_dict})


    def draw_kline_changes(self, kline_list):
        """Update coin_index values as needed."""
        for kline_dataset in kline_list.items():
            coin = kline_dataset[0]

            items = self.coin_index.findItems(coin, QtCore.Qt.MatchExactly)

            # findItems returns a list hence we iterate through it. We only expect one result though.
            for item in items:

                # get current row of coin to check
                row = item.row()

            # iterate through received kline data
            for kline_data in kline_dataset[1].items():
                colIndex = int(kline_data[0])
                new_data = kline_data[1]

                # read old data from table
                old_data = self.coin_index.item(row, colIndex).text()

                # if data differs from old data, create an item, set new data and update coin_index.
                if float(old_data) != float(new_data):
                    newItem = QtWidgets.QTableWidgetItem()
                    newItem.setData(QtCore.Qt.EditRole, QtCore.QVariant(new_data))
                    self.coin_index.setItem(row, colIndex, newItem)


    @classmethod
    def klines_received(self, klines_pair):
        """Save kline data received from api call callback in array."""
        kline_data = klines_pair[0]
        pair = klines_pair[1]
        timeframe = klines_pair[2]

        val["klines"][timeframe][str(pair)] = kline_data

    @staticmethod
    def test():
        print("rec")
