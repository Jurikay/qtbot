# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Main gui class."""

import configparser
import time
import logging

from datetime import datetime, timedelta
from functools import partial
from binance.websockets import BinanceSocketManager

import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWebEngineWidgets import QWebEngineView

# from PyQt5.QtMultimedia import QSoundEffect, QMediaPlayer, QMediaContent, QSound


from app.apiFunctions import ApiCalls
from app.callbacks import (Worker,
                           depthCallback, directCallback, tickerCallback,
                           userCallback, klineCallback)
# api_order_history
from app.charts import Webpages as Webpages
from app.colors import Colors
from app.gui_functions import (calc_total_btc,
                               calc_wavg, initial_values, filter_table,
                               update_holding_prices, update_coin_index_prices, init_filter, calc_all_wavgs)
# filter_coin_index, global_filter, filter_confirmed,
from app.init import val
from app.strategies.fishing_bot import FishingBot
# from app.strategies.limit_order import LimitOrder
from app.bot import BotClass
import app
from app.elements.config import ConfigManager
from app.elements.hotkeys import HotKeys
from binance.client import Client


class beeserBot(QtWidgets.QMainWindow):

    """Main ui class."""

    def __init__(self):
        """Init method."""
        app.mw = self
        self.client = app.client
        super(beeserBot, self).__init__()
        loadUi("ui/MainWindow.ui", self)

        # set external stylesheet
        with open("ui/style.qss", "r") as fh:
            self.setStyleSheet(fh.read())


        cfg = ConfigManager(self)
        cfg.connect_cfg()
        cfg.read_config()


        init_logging(self)

        print("setting client: " + str(val["api_key"]))
        client = Client(val["api_key"], val["api_secret"], {"verify": True, "timeout": 61})


        self.api_calls_obj = ApiCalls(self, client)
        self.api_calls_obj.initialize()

        hot_keys = HotKeys(self)

        hot_keys.init_hotkeys()

        set_modes(self)
        set_config_values(self)

        main_init(self)


        

        # instantiate ApiCalls object
        

        # initialize limit order signals and slots
        self.limit_pane.initialize()

        # connect elements to functions
        

        self.reset_vol_direct.clicked.connect(self.reset_vol_direction)

    
        # instantiate LimitOrder
        # limit_order = LimitOrder(self)
        # from app.strategies.limit_order_pane import LimitOrderPane


        self.debug2_button.clicked.connect(self.limit_pane.test_func)

        # initialize open orders table
        self.open_orders.initialize()
        # self.open_orders.cellClicked.connect(self.limit_pane.open_orders_cell_clicked)

        self.coin_selector.activated.connect(self.change_pair)

        self.hide_pairs.stateChanged.connect(partial(partial(filter_table, self), self.coinindex_filter.text(), self.hide_pairs.checkState()))

        self.tabsBotLeft.setCornerWidget(self.coin_index_filter, corner=QtCore.Qt.TopRightCorner)
        # self.debug_corner.clicked.connect(self.set_corner_widget)

        self.wavg_button.clicked.connect(calc_wavg)
        self.calc_all_wavg_button.clicked.connect(partial(calc_all_wavgs, self))

        # instantiate fishing bot class
        fish_bot = FishingBot(self)

        # connect buttons to fishing bot methods
        self.fish_add_trade.clicked.connect(fish_bot.add_order)

        self.fish_clear_all.clicked.connect(partial(fish_bot.clear_all_orders, self))


        self.button_klines.clicked.connect(self.iterate_through_klines)
        # self.player = QMediaPlayer()
        # sound = QMediaContent(QtCore.QUrl.fromLocalFile("sounds/Tink.wav"))
        # self.player.setMedia(sound)
        # self.player.setVolume(1)


        self.button_wavg.clicked.connect(calc_wavg)

        # self.coinindex_filter.textChanged.connect(partial(filter_table, self))
        # self.coinindex_filter.returnPressed.connect(partial(filter_confirmed, self))
        self.hide_pairs.stateChanged.connect(partial(init_filter, self))
        self.coinindex_filter.textChanged.connect(partial(init_filter, self))

        # change corner widget bottom left tabs
        # self.tabsBotLeft.currentChanged.connect(self.set_corner_widget)

        # self.get_all_orders_button.clicked.connect(self.get_all_orders)
        # Fix a linter error...
        self.chartLOL = QWebEngineView()


        # check if coin is an empty dict. If yes, api calls have not been answered.
        current_coin = val.get("coin", None)
        if current_coin is not None:
            print("authenticated!")

            self.initialize()

        # api credentials not valid; display welcome page
        else:
            self.chart.setHtml(Webpages.welcome_page())
            self.chart.show()
            self.bot_tabs.setCurrentIndex(4)

            self.api_key.setStyleSheet("border: 2px solid #f3ba2e;")
            self.api_secret.setStyleSheet("border: 2px solid #f3ba2e;")


    def initialize(self):
        """One-time gui initialization."""
        self.api_calls_obj.api_calls()

        for coin in val["coins"]:

            icon = QtGui.QIcon("images/ico/" + coin[:-3] + ".svg")
            self.coin_selector.addItem(icon, coin[:-3])

        self.coin_selector.model().sort(0)
        self.coin_selector.setIconSize(QtCore.QSize(25, 25))

        coinIndex = self.coin_selector.findText(val["coin"])
        self.coin_selector.setCurrentIndex(coinIndex)

        icon = QtGui.QIcon("images/ico/" + "BTC" + ".svg")
        self.quote_asset_box.addItem(icon, "BTC")
        self.quote_asset_box.setIconSize(QtCore.QSize(25, 25))
        self.quote_asset_box.setIconSize(QtCore.QSize(25, 25))

        initial_values(self)

        self.schedule_websockets()
        self.schedule_work()

        self.holdings_table.initialize()

        self.coin_index.build_coinindex()

        self.start_kline_check()

        # self.sound_1 = QSound('sounds/Tink.wav')
        self.btc_chart.setHtml(Webpages.build_chart_btc("BTCUSD", val["defaultTimeframe"], "COINBASE"))
        self.btc_chart.show()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.delayed_stuff)
        self.timer.start()


    # refactor into tables, config etc
    def delayed_stuff(self):

        print("delayed")

        self.asks_table.setColumnWidth(1, 75)
        self.bids_table.setColumnWidth(1, 75)

        self.tradeTable.setColumnWidth(0, 100)
        self.tradeTable.setColumnWidth(1, 75)

        self.open_orders.setColumnWidth(0, 130)
        self.open_orders.setColumnWidth(3, 120)
        self.open_orders.setColumnWidth(7, 120)
        self.open_orders.setColumnWidth(9, 120)
        # self.open_orders.setColumnWidth(10, 0)

        self.history_table.setColumnWidth(0, 130)
        self.history_table.setColumnWidth(2, 75)
        self.history_table.setColumnWidth(3, 75)
        self.history_table.setColumnWidth(6, 120)

        self.fishbot_table.setColumnWidth(0, 100)
        self.fishbot_table.setColumnWidth(1, 60)
        self.fishbot_table.setColumnWidth(2, 60)
        self.fishbot_table.setColumnWidth(4, 100)
        self.fishbot_table.setColumnWidth(5, 120)


        orders_header = self.open_orders.horizontalHeader()

        orders_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        orders_header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        orders_header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)

        history_header = self.history_table.horizontalHeader()
        history_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        # self.check_buy_amount()
        # self.check_sell_ammount()

        # val["sound_1"] = QSoundEffect()
        # val["sound_1"].setSource(QtCore.QUrl.fromLocalFile("sounds/Tink.wav"))
        # val["sound_1"].setVolume(1)
        print("scroll")

        self.asks_table.scrollToBottom()

        self.set_stats()
        self.timer.stop()
        logging.info('Finishing setup...')

    # this is used often; See if it fits somewhere though
    def percentage_amount(self, total_btc, price, percentage, decimals):
        """Calculate the buy/sell amount based on price and percentage value."""
        try:
            maxSize = (float(total_btc) / float(price)) * (percentage / 100)
        except ZeroDivisionError:
            maxSize = 0


        if decimals == 0:
            return int(maxSize)


        maxSizeRounded = int(maxSize * 10**decimals) / 10.0**decimals
        return maxSizeRounded

    # this is used often
    def set_pair_values(self):
        """Set various values based on the chosen pair."""
        val["coin"] = val["pair"][:-3]
        val["decimals"] = len(str(val["coins"][val["pair"]]["tickSize"])) - 2

        if int(val["coins"][val["pair"]]["minTrade"]) == 1:
            val["assetDecimals"] = 0
        else:
            val["assetDecimals"] = len(str(val["coins"][val["pair"]]["minTrade"])) - 2



    # filter tables
    def hide_other_pairs(self):
        for row in range(self.open_orders.rowCount()):
            self.open_orders.setRowHidden(row, True)
        for row in range(self.holdings_table.rowCount()):
            self.holdings_table.setRowHidden(row, True)
        for row in range(self.coin_index.rowCount()):
            self.coin_index.setRowHidden(row, True)
        items = self.open_orders.findItems(str(val["coin"]), QtCore.Qt.MatchContains)
        for item in items:
            row = item.row()
            self.open_orders.setRowHidden(row, False)

        items = self.holdings_table.findItems(str(val["coin"]), QtCore.Qt.MatchContains)
        for item in items:
            row = item.row()
            self.holdings_table.setRowHidden(row, False)

        items = self.coin_index.findItems(str(val["coin"]), QtCore.Qt.MatchContains)
        for item in items:
            row = item.row()
            self.coin_index.setRowHidden(row, False)

    # filter tables
    def show_other_pairs(self):
        for row in range(self.open_orders.rowCount()):
            self.open_orders.setRowHidden(row, False)
        for row in range(self.holdings_table.rowCount()):
            self.holdings_table.setRowHidden(row, False)
        for row in range(self.coin_index.rowCount()):
            self.coin_index.setRowHidden(row, False)

    # stats
    def set_stats(self):
        self.total_running.setText(str(val["stats"]["timeRunning"]))
        self.total_trades.setText(str(val["stats"]["execTrades"]))
        self.total_bot_trades.setText(str(val["stats"]["execBotTrades"]))
        self.total_api_calls.setText(str(val["stats"]["apiCalls"]))
        self.total_api_updates.setText(str(val["stats"]["apiUpdates"]))


    def change_pair(self):

        newcoin = self.coin_selector.currentText()

        if any(newcoin + "BTC" in s for s in val["coins"]) and newcoin != val["coin"]:
            val["pair"] = newcoin + "BTC"
            val["bm"].stop_socket(val["aggtradeWebsocket"])
            val["bm"].stop_socket(val["depthWebsocket"])
            val["bm"].stop_socket(val["klineWebsocket"])
            logging.info('Switching to %s' % newcoin + " / BTC")

            self.set_pair_values()
            initial_values(self)

            self.websockets_symbol()

            self.history_table.setRowCount(0)

            self.api_calls_obj.api_calls()

            init_filter(self)

    # debug
    def reset_vol_direction(self):
        val["volDirection"] = 0

    # global ui
    def tick(self, payload):
        if payload == 1:
            self.one_second_update()


        elif payload == 15:
            print("scroll to bottom")
            self.asks_table.scrollToBottom()


    # global ui
    def one_second_update(self):
        self.session_running.setText(str(timedelta(seconds=val["timeRunning"])))
        val["timeRunning"] += 1

        self.current_time.setText(str(time.strftime('%a, %d %b %Y %H:%M:%S')))

        self.explicit_api_calls_label.setText(str(val["apiCalls"]))
        self.explicit_api_updates.setText(str(val["apiUpdates"]))

        total_btc_value = calc_total_btc()
        self.total_btc_label.setText("<span style='font-size: 14px; color: #f3ba2e; font-family: Arial Black;'>" + total_btc_value + "</span>")

        total_usd_value = '{number:,.{digits}f}'.format(number=float(total_btc_value.replace(" BTC", "")) * float(val["tickers"]["BTCUSDT"]["lastPrice"]), digits=2) + "$"

        self.total_usd_label.setText("<span style='font-size: 14px; color: white; font-family: Arial Black;'>" + total_usd_value + "</span>")

        self.btc_price_label.setText('{number:,.{digits}f}'.format(number=float(val["tickers"]["BTCUSDT"]["lastPrice"]), digits=2) + "$")

        operator = ""
        percent_change = float(val["tickers"]["BTCUSDT"]["priceChangePercent"])
        if percent_change > 0:
            operator = "+"

        btc_percent = operator + '{number:,.{digits}f}'.format(number=percent_change, digits=2) + "%"

        self.btc_percent_label.setText(btc_percent)

        self.debug.setText(str(val["volDirection"]))

        self.debug.setText('{number:.{digits}f}'.format(number=float(val["volDirection"]), digits=4) + "BTC")

        self.percent_changes()

        self.check_websocket()

        # only update the currently active table
        tab_index_botLeft = self.tabsBotLeft.currentIndex()

        if tab_index_botLeft == 3:
            update_holding_prices(self)
            val["indexTabOpen"] = False
        elif tab_index_botLeft == 0:
            update_coin_index_prices(self)
            self.start_kline_iterator()
            val["indexTabOpen"] = True
            # self.start_kline_iterator()
        else:
            val["indexTabOpen"] = False

    # global ui / logic
    def check_websocket(self):
        if self.update_count == int(val["apiUpdates"]):
            self.no_updates += 1
        else:
            self.no_updates = 0

        self.update_count = int(val["apiUpdates"])

        if self.no_updates >= 2 and self.no_updates < 10:
            self.status.setText("<span style='color:" + Colors.color_yellow + "'>warning</span>")
        elif self.no_updates >= 10:
            self.status.setText("<span style='color:" + Colors.color_pink + "'>disconnected</span>")
        else:
            self.status.setText("<span style='color:" + Colors.color_green + "'>connected</span>")

    # global ui
    def percent_changes(self):
        try:
                close_5m = float(val["klines"]["1m"][val["pair"]][-5][4])
                close_15m = float(val["klines"]["1m"][val["pair"]][-15][4])
                # close_30m = float(val["klines"]["1m"][val["pair"]][-30][4])
                close_1h = float(val["klines"]["1m"][val["pair"]][-60][4])
                close_4h = float(val["klines"]["1m"][val["pair"]][-240][4])

                change_5m_value = ((float(val["tickers"][val["pair"]]["lastPrice"]) / float(close_5m)) - 1) * 100
                change_15m_value = ((float(val["tickers"][val["pair"]]["lastPrice"]) / float(close_15m)) - 1) * 100
                # change_30m_value = ((float(val["tickers"][val["pair"]]["lastPrice"]) / float(close_30m)) - 1) * 100
                change_1h_value = ((float(val["tickers"][val["pair"]]["lastPrice"]) / float(close_1h)) - 1) * 100
                change_4h_value = ((float(val["tickers"][val["pair"]]["lastPrice"]) / float(close_4h)) - 1) * 100

                change_1d_value = float(val["tickers"][val["pair"]]["priceChangePercent"])


                changes = [self.change_5m, self.change_15m, self.change_1h, self.change_4h, self.change_1d]
                change_values = [change_5m_value, change_15m_value, change_1h_value, change_4h_value, change_1d_value]

                for i, change in enumerate(changes):
                    if change_values[i] > 0:
                        operator = "+"
                        color = Colors.color_green
                    elif change_values[i] < 0:
                        operator = ""
                        color = Colors.color_pink
                    else:
                        operator = ""
                        color = Colors.color_grey

                    # print(str(change))
                    change.setText("<span style='color: " + color + "'>" + operator + "{0:.2f}".format(change_values[i]) + "%</span")

        except Exception as e:
            print(str(e))

    # debug
    def play_sound_effect(self):
        # self.sound_1.play()
        print("playung sound")


    def schedule_work(self):

        # Pass the function to execute
        worker = Worker(self.check_for_update)

        # Any other args, kwargs are passed to the run function
        # worker.signals.result.connect(self.print_output)
        worker.signals.progress.connect(self.tick)

        # start thread
        self.threadpool.start(worker)


    def schedule_websockets(self):
        # Pass the function to execute
        worker = Worker(self.start_sockets)

        worker.signals.progress.connect(self.live_data.progress_fn)

        # Execute
        self.threadpool.start(worker)

    def start_kline_check(self):
        worker = Worker(self.schedule_kline_check)
        # worker.signals.progress.connect(self.klines_received)
        self.threadpool.start(worker)

    def start_kline_iterator(self):
        worker = Worker(self.iterate_through_klines)
        worker.signals.progress.connect(self.draw_kline_changes)
        self.threadpool.start(worker)

    def schedule_kline_check(self, progress_callback):
        maxThreads = self.threadpool.maxThreadCount()
        if maxThreads <= 2:
            sleepTime = 1
        elif maxThreads <= 4:
            sleepTime = 0.33
            longSleep = 30
        else:
            sleepTime = 0.1
            longSleep = 15

        while True:

            print("Spawning api call workers")
            for i in val["coins"]:
                # print(str(i))
                time.sleep(sleepTime)
                worker = Worker(partial(self.api_calls_obj.get_kline, str(i)))
                worker.signals.progress.connect(self.klines_received)
                self.threadpool.tryStart(worker)

            time.sleep(longSleep)



        # worker = Worker(partial(get_kline, self, ))



    # wip
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


    def klines_received(self, klines_pair):
        """Save kline data received from api call callback in array."""
        kline_data = klines_pair[0]
        pair = klines_pair[1]
        timeframe = klines_pair[2]

        val["klines"][timeframe][str(pair)] = kline_data



    # WIP


    



    # cancel an order from a separate thread
    def cancel_order_byId(self, order_id, symbol):
        worker = Worker(partial(self.api_calls_obj.api_cancel_order, app.client, order_id, symbol))
        # worker.signals.progress.connect(self.cancel_callback)
        self.threadpool.start(worker)



    # global ui
    def check_for_update(self, progress_callback):
        current_height = self.frameGeometry().height()
        while True:
            if current_height > self.frameGeometry().height():
                progress_callback.emit(15)

            current_height = self.frameGeometry().height()
            progress_callback.emit(1)
            time.sleep(1)


    # sockets
    def start_sockets(self, progress_callback):
        val["bm"] = BinanceSocketManager(app.client)
        self.websockets_symbol()
        # start user and ticker websocket separately since it does not need to be restarted
        val["userWebsocket"] = val["bm"].start_user_socket(partial(userCallback, self))
        val["tickerWebsocket"] = val["bm"].start_ticker_socket(partial(tickerCallback, self))
        val["bm"].start()

    def websockets_symbol(self):
        """Symbol specific websockets. This gets called on pair change."""
        val["aggtradeWebsocket"] = val["bm"].start_aggtrade_socket(val["pair"], partial(directCallback, self))
        val["depthWebsocket"] = val["bm"].start_depth_socket(val["pair"], partial(depthCallback, self), depth=20)
        val["klineWebsocket"] = val["bm"].start_kline_socket(val["pair"], partial(klineCallback, self))
        # logging.info('Starting websockets for %s' % str(val["pair"]))



    
    # stats
    def write_stats(self):
        total_running = int(val["stats"]["timeRunning"]) + int(val["timeRunning"])
        total_trades = int(val["stats"]["execTrades"]) + int(val["execTrades"])
        total_bot_trades = int(val["stats"]["execBotTrades"]) + int(val["execBotTrades"])
        api_updates = int(val["stats"]["apiUpdates"]) + int(val["apiUpdates"])
        api_calls = int(val["stats"]["apiCalls"]) + int(val["apiCalls"])

        config = configparser.ConfigParser()

        config["Stats"] = {"timeRunning": total_running,
                           "execTrades": total_trades,
                           "execBotTrades": total_bot_trades,
                           "apiUpdates": api_updates,
                           "apiCalls": api_calls}

        print("WRITING CONFIG")
        print(str(total_running) + " " + str(api_updates))

        with open('stats.ini', 'w') as configfile:
                    config.write(configfile)


    # config
    def set_button_text(self):
        self.limit_button0.setText(str(val["buttonPercentage"][0]) + "%")
        self.limit_button1.setText(str(val["buttonPercentage"][1]) + "%")
        self.limit_button2.setText(str(val["buttonPercentage"][2]) + "%")
        self.limit_button3.setText(str(val["buttonPercentage"][3]) + "%")
        self.limit_button4.setText(str(val["buttonPercentage"][4]) + "%")

        self.limit_sbutton0.setText(str(val["buttonPercentage"][0]) + "%")
        self.limit_sbutton1.setText(str(val["buttonPercentage"][1]) + "%")
        self.limit_sbutton2.setText(str(val["buttonPercentage"][2]) + "%")
        self.limit_sbutton3.setText(str(val["buttonPercentage"][3]) + "%")
        self.limit_sbutton4.setText(str(val["buttonPercentage"][4]) + "%")

    def shutdown_bot(self):
        self.write_stats()

#################################

# config
def set_config_values(self):
    try:
        self.default_pair.setText(val["defaultPair"])

        self.api_key.setText(val["api_key"])
        self.api_secret.setText(val["api_secret"])

        self.percent_1.setText(str(int(val["buttonPercentage"][0])))
        self.percent_2.setText(str(int(val["buttonPercentage"][1])))
        self.percent_3.setText(str(int(val["buttonPercentage"][2])))
        self.percent_4.setText(str(int(val["buttonPercentage"][3])))
        self.percent_5.setText(str(int(val["buttonPercentage"][4])))
        self.set_button_text()

        # self.default_timeframe.setText(str(val["defaultTimeframe"]))

        raw_timeframes = [1, 3, 5, 15, 30, 45, 60, 120, 180, 240, 1440]

        # dtf = self.dtf_selector.currentText()
        for i, tf in enumerate(raw_timeframes):
            if val["defaultTimeframe"] == str(tf):
                self.dtf_selector.setCurrentIndex(i)

    except (TypeError, KeyError):
        pass


def set_modes(self):
    if val["debug"] is False:
        # self.tabsBotLeft.setTabEnabled(0, False)
        self.tabsBotLeft.removeTab(0)
        self.ChartTabs.removeTab(5)
        self.ChartTabs.removeTab(4)
        self.ChartTabs.removeTab(3)
        self.ChartTabs.setTabEnabled(1, False)

        self.tabsBotLeft.setCurrentIndex(0)
        self.ChartTabs.setCurrentIndex(0)
        self.bot_tabs.setCurrentIndex(0)
    else:
        logging.info("DEBUG mode enabled")


def main_init(self):
    # set default locale
    QtCore.QLocale.setDefault(QtCore.QLocale(QtCore.QLocale.C))

    logging.info('Initializing GUI')

    self.setWindowTitle("Juris beeser Bot")

    self.setWindowIcon(QtGui.QIcon('images/assets/256.png'))

    self.restart_warning.setStyleSheet("color: transparent;")
    # self.spread_area.setStyleSheet("background: #2e363d;")

    self.holdings_table.setStyleSheet("alternate-background-color: #2e363d;")

    self.counter = 0
    self.counter2 = 0

    self.update_count = 0
    self.no_updates = 0


    for _ in range(20):
        self.bids_table.insertRow(0)
        self.asks_table.insertRow(0)
        self.new_table.insertRow(0)

    for _ in range(50):
        self.tradeTable.insertRow(0)


    # INIT THREADING
    self.threadpool = QtCore.QThreadPool()
    logging.info('Enable multithreading with %d threads.' % self.threadpool.maxThreadCount())


class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)
        self.widget.update()
        # print(msg)


def init_logging(self):
    qtLogger = QPlainTextEditLogger(self)
    qtLogger.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(qtLogger)

    # You can control the logging level
    logging.getLogger().setLevel(logging.INFO)

    self.widget_2.setWidget(qtLogger.widget)
