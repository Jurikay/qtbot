# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Main gui class."""

# import configparser
# import time
import logging

# from datetime import timedelta
from functools import partial
from binance.websockets import BinanceSocketManager

import PyQt5.QtCore as QtCore
# import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWebEngineWidgets import QWebEngineView

# from PyQt5.QtMultimedia import QSoundEffect, QMediaPlayer, QMediaContent, QSound


from app.apiFunctions import ApiCalls
from app.callbacks import (depth_callback, trade_callback, ticker_callback,
                           user_callback, kline_callback)
# api_order_history
from app.charts import Webpages as Webpages
# from app.colors import Colors
from app.gui_functions import (calc_wavg, calc_all_wavgs)
# filter_coin_index, global_filter, filter_confirmed,
from app.workers import Worker
from app.init import val
from app.strategies.fishing_bot import FishingBot
# from app.strategies.limit_order import LimitOrder
import app
from app.elements.config import ConfigManager
from app.elements.hotkeys import HotKeys
# from app.elements.kline_data import KlineManager
from app.elements.test_class import TestKlasse
from app.elements.init_manager import InitManager
from app.elements.custom_logger import BotLogger
from app.elements.gui_manager import GuiManager
from app.gui_functions import TableFilters


class beeserBot(QtWidgets.QMainWindow):

    """Main ui class."""

    def __init__(self):

        """Main gui init method."""

        super(beeserBot, self).__init__()

        app.mw = self
        self.client = app.client
        loadUi("ui/MainWindow.ui", self)

        # set external stylesheet
        with open("ui/style.qss", "r") as fh:
            self.setStyleSheet(fh.read())

        self.update_count = 0
        self.no_updates = 0


        # INIT THREADING
        self.threadpool = QtCore.QThreadPool()
        app.threadpool = self.threadpool
        logging.info('Enable multithreading with %d threads.' % self.threadpool.maxThreadCount())


        # instantiate various helper classes

        self.log_manager = BotLogger(self)
        self.log_manager.init_logging()


        self.cfg_manager = ConfigManager(self)
        # self.cfg.connect_cfg()
        self.cfg_manager.read_config()

        self.api_manager = ApiCalls(self)
        self.api_manager.initialize()

        # instantiate fishing bot class
        self.fish_bot = FishingBot(self)

        self.hotkey_manager = HotKeys(self)
        self.hotkey_manager.init_hotkeys()

        self.test_klasse = TestKlasse(self)
        self.test_klasse.create_signal()

        self.init_manager = InitManager(self)
        self.init_manager.initialize()

        self.gui_manager = GuiManager(self)
        self.gui_manager.initialize()

        self.filter_manager = TableFilters(self)
        self.filter_manager.init_filter()

        # self.kline_manager = KlineManager(self)
        # self.kline_manager.start_kline_check()
        self.coin_index.start_kline_check()



        # initialize open orders table
        self.open_orders.initialize()

        # initialize limit order signals and slots
        self.limit_pane.initialize()


        # connect elements to functions

        self.debug2_button.clicked.connect(self.limit_pane.test_func)
        self.coin_selector.activated.connect(self.gui_manager.change_pair)
        self.hide_pairs.stateChanged.connect(partial(self.filter_manager.filter_table, self.coinindex_filter.text(), self.hide_pairs.checkState()))
        self.tabsBotLeft.setCornerWidget(self.coin_index_filter, corner=QtCore.Qt.TopRightCorner)

        # debug
        self.wavg_button.clicked.connect(calc_wavg)
        self.calc_all_wavg_button.clicked.connect(partial(calc_all_wavgs, self))

        self.button_wavg.clicked.connect(calc_wavg)

        # connect buttons to fishing bot methods (refactor)
        self.fish_add_trade.clicked.connect(self.fish_bot.add_order)

        self.fish_clear_all.clicked.connect(partial(self.fish_bot.clear_all_orders, self))


        # filter
        self.hide_pairs.stateChanged.connect(self.filter_manager.init_filter)
        self.coinindex_filter.textChanged.connect(self.filter_manager.init_filter)

        # change corner widget bottom left tabs
        # self.tabsBotLeft.currentChanged.connect(self.set_corner_widget)

        # self.get_all_orders_button.clicked.connect(self.get_all_orders)

        # Fix a linter error...
        self.chartLOL = QWebEngineView()


        # check if coin is an empty dict. If yes, api calls have not been answered.
        # TODO: refactor
        current_coin = val.get("coin", None)
        if current_coin is not None:
            print("authenticated!")

            self.init_manager.api_init()

        # api credentials not valid; display welcome page
        else:
            self.show_error_page()


    def show_error_page(self):
        self.chart.setHtml(Webpages.welcome_page())
        self.chart.show()
        self.bot_tabs.setCurrentIndex(4)

        self.api_key.setStyleSheet("border: 2px solid #f3ba2e;")
        self.api_secret.setStyleSheet("border: 2px solid #f3ba2e;")

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

        self.timer.stop()
        logging.info('Finishing setup...')

    # this is used often; See if it fits somewhere though
    @staticmethod
    def percentage_amount(total_btc, price, percentage, decimals):
        """Calculate the buy/sell amount based on price and percentage value."""
        try:
            maxSize = (float(total_btc) / float(price)) * (percentage / 100)
        except ZeroDivisionError:
            maxSize = 0


        if decimals == 0:
            return int(maxSize)


        maxSizeRounded = int(maxSize * 10**decimals) / 10.0**decimals
        return maxSizeRounded


    # global ui
    def schedule_work(self):

        # Pass the function to execute
        worker = Worker(self.gui_manager.check_for_update)

        # Any other args, kwargs are passed to the run function
        # worker.signals.result.connect(self.print_output)
        worker.signals.progress.connect(self.gui_manager.tick)

        # start thread
        self.threadpool.start(worker)

    # websockets
    def schedule_websockets(self):
        # Pass the function to execute
        worker = Worker(self.start_sockets)

        worker.signals.progress.connect(self.live_data.progress_fn)

        # Execute
        self.threadpool.start(worker)




    # cancel an order from a separate thread
    def cancel_order_byId(self, order_id, symbol):
        worker = Worker(partial(self.api_manager.api_cancel_order, app.client, order_id, symbol))
        # worker.signals.progress.connect(self.cancel_callback)
        self.threadpool.start(worker)


    # sockets
    def start_sockets(self, progress_callback):
        val["bm"] = BinanceSocketManager(app.client)
        self.websockets_symbol()
        # start user and ticker websocket separately since it does not need to be restarted
        val["userWebsocket"] = val["bm"].start_user_socket(partial(user_callback, self))
        val["tickerWebsocket"] = val["bm"].start_ticker_socket(partial(ticker_callback, self))
        val["bm"].start()

    def websockets_symbol(self):
        """Symbol specific websockets. This gets called on pair change."""
        val["aggtradeWebsocket"] = val["bm"].start_aggtrade_socket(val["pair"], partial(trade_callback, self))
        val["depthWebsocket"] = val["bm"].start_depth_socket(val["pair"], partial(depth_callback, self), depth=20)
        val["klineWebsocket"] = val["bm"].start_kline_socket(val["pair"], partial(kline_callback, self))
        # logging.info('Starting websockets for %s' % str(val["pair"]))


    def shutdown_bot(self):
        self.cfg_manager.write_stats()
