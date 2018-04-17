# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
import time
from functools import partial
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import app
from app.init import val
from app.table_items import CoinDelegate
from app.colors import Colors
from app.workers import Worker


"""CoinIndex main class."""


class CoinIndex(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super(QtWidgets.QTableWidget, self).__init__(parent)
        self.mw = app.mw
        self.threadpool = QtCore.QThreadPool()


    def filter_coin_index(self, text, state):
        for i in range(self.rowCount()):
            if state == 2 and not self.item(i, 1).text().startswith(val["coin"]):
                self.setRowHidden(i, True)
            elif not self.item(i, 1).text().startswith(text.upper()):
                self.setRowHidden(i, True)
            else:
                self.setRowHidden(i, False)


    def build_coinindex(self):
        self.setRowCount(0)
        print("setze delegate")
        self.setItemDelegate(CoinDelegate(self))

        for pair in val["tickers"]:
            if "USDT" not in pair:
                coin = str(val["tickers"][pair]["symbol"]).replace("BTC", "")
                # print(str(holding))

                icon = QtGui.QIcon("images/ico/" + coin + ".svg")

                icon_item = QtWidgets.QTableWidgetItem()
                icon_item.setIcon(icon)

                # price_change = float(val["tickers"][pair]["priceChangePercent"])
                # if price_change > 0:
                #     operator = "+"
                # else:
                #     operator = ""

                last_price = QtWidgets.QTableWidgetItem()
                last_price.setData(QtCore.Qt.EditRole, QtCore.QVariant(val["tickers"][pair]["lastPrice"]))

                price_change = QtWidgets.QTableWidgetItem()
                price_change_value = float(val["tickers"][pair]["priceChangePercent"])
                price_change.setData(QtCore.Qt.EditRole, QtCore.QVariant(price_change_value))

                btc_volume = QtWidgets.QTableWidgetItem()
                btc_volume.setData(QtCore.Qt.EditRole, QtCore.QVariant(round(float(val["tickers"][pair]["quoteVolume"]), 2)))

                zero_item = QtWidgets.QTableWidgetItem()
                zero_item.setData(QtCore.Qt.EditRole, QtCore.QVariant(0))
                # price_change.setData(Qt.DisplayRole, QtCore.QVariant(str(val["tickers"][pair]["priceChangePercent"]) + "%"))

                self.insertRow(0)
                self.setItem(0, 0, icon_item)
                self.setItem(0, 1, QtWidgets.QTableWidgetItem(coin))
                self.setItem(0, 2, last_price)
                self.setItem(0, 3, QtWidgets.QTableWidgetItem(price_change))
                self.setItem(0, 4, QtWidgets.QTableWidgetItem(btc_volume))

                for i in (number + 6 for number in range(7)):
                    self.setItem(0, i, QtWidgets.QTableWidgetItem(zero_item))

                if price_change_value < 0:
                    self.item(0, 3).setForeground(QtGui.QColor(Colors.color_pink))
                else:
                    self.item(0, 3).setForeground(QtGui.QColor(Colors.color_green))

                self.btn_trade = QtWidgets.QPushButton("Trade " + coin)
                self.btn_trade.clicked.connect(self.gotoTradeButtonClicked)
                self.setCellWidget(0, 5, self.btn_trade)

        self.model().sort(5, QtCore.Qt.AscendingOrder)
        self.setIconSize(QtCore.QSize(25, 25))
        self.setIconSize(QtCore.QSize(25, 25))

        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.setColumnWidth(2, 120)
        self.setColumnWidth(5, 130)
        self.model().sort(4, QtCore.Qt.DescendingOrder)



    def gotoTradeButtonClicked(self):
        button_text = self.sender().text()
        coin = button_text.replace("Trade ", "")

        coinIndex = self.mw.coin_selector.findText(coin)
        self.mw.coin_selector.setCurrentIndex(coinIndex)

        self.mw.change_pair()

    def update_coin_index_prices(self):
        for i in range(self.rowCount()):
            coin = self.item(i, 1).text()
            price = self.item(i, 2).text()
            price_change = self.item(i, 3).text()
            btc_volume = self.item(i, 4).text()

            new_price = QtWidgets.QTableWidgetItem()
            new_price_change = QtWidgets.QTableWidgetItem()
            new_btc_volume = QtWidgets.QTableWidgetItem()

            new_price_value = "{0:.8f}".format(float(val["tickers"][coin + "BTC"]["lastPrice"]))
            new_price_change_value = float(val["tickers"][coin + "BTC"]["priceChangePercent"])
            new_btc_volume_value = float(val["tickers"][coin + "BTC"]["quoteVolume"])

            new_price.setData(QtCore.Qt.EditRole, QtCore.QVariant(new_price_value))
            new_price_change.setData(QtCore.Qt.EditRole, QtCore.QVariant(new_price_change_value))
            new_btc_volume.setData(QtCore.Qt.EditRole, QtCore.QVariant(new_btc_volume_value))

            if price != new_price_value:
                self.setItem(i, 2, new_price)

            if float(price_change) != new_price_change_value:

                self.setItem(i, 3, new_price_change)

            if float(btc_volume) != new_btc_volume_value:

                self.setItem(i, 4, new_btc_volume)
            ##########################################
        # kline api calls
        ##########################################


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
                worker = Worker(partial(self.mw.api_manager.get_kline, str(i)))
                worker.signals.progress.connect(self.klines_received)
                self.threadpool.tryStart(worker)

            time.sleep(longSleep)


    # wip
    @staticmethod
    def iterate_through_klines(progress_callback):
        """Iterate through the global klines dict and calculate values based on historical data."""
        for _, kline in enumerate(dict(val["klines"]["1m"])):
            coin = kline.replace("BTC", "")
            # items = self.findItems(coin, QtCore.Qt.MatchExactly)
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

            items = self.findItems(coin, QtCore.Qt.MatchExactly)

            # findItems returns a list hence we iterate through it. We only expect one result though.
            for item in items:

                # get current row of coin to check
                row = item.row()

            # iterate through received kline data
            for kline_data in kline_dataset[1].items():
                colIndex = int(kline_data[0])
                new_data = kline_data[1]

                # read old data from table
                old_data = self.item(row, colIndex).text()

                # if data differs from old data, create an item, set new data and update.
                if float(old_data) != float(new_data):
                    newItem = QtWidgets.QTableWidgetItem()
                    newItem.setData(QtCore.Qt.EditRole, QtCore.QVariant(new_data))
                    self.setItem(row, colIndex, newItem)


    def klines_received(self, klines_pair):
        """Save kline data received from api call callback in array."""
        kline_data = klines_pair[0]
        pair = klines_pair[1]
        timeframe = klines_pair[2]

        val["klines"][timeframe][str(pair)] = kline_data
