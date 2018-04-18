# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Main gui class."""

# import configparser
# import time
import logging

# from datetime import timedelta
from functools import partial

import PyQt5.QtCore as QtCore
# import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWebEngineWidgets import QWebEngineView  # QWebEnginePage

# from PyQt5.QtMultimedia import QSoundEffect, QMediaPlayer, QMediaContent, QSound


from app.apiFunctions import ApiCalls
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
from app.elements.websocket_manager import WebsocketManager


class beeserBot(QtWidgets.QMainWindow):

    """Main ui class."""

    def __init__(self):

        """Main gui init method."""

        super(beeserBot, self).__init__()

        self.client = app.client
        self.threadpool = QtCore.QThreadPool()
        app.threadpool = self.threadpool
        app.mw = self

        # load QtDesigner UI file
        loadUi("ui/MainWindow.ui", self)

        # set external stylesheet
        with open("ui/style.qss", "r") as fh:
            self.setStyleSheet(fh.read())

        # instantiate various helper classes
        self.instantiate_managers()

        # self.kline_manager = KlineManager(self)
        # self.kline_manager.start_kline_check()
        self.coin_index.start_kline_check()



        # initialize open orders table
        self.open_orders.initialize()

        # initialize limit order signals and slots
        self.limit_pane.initialize()


        # belongs into filters class
        self.tabsBotLeft.setCornerWidget(self.coin_index_filter, corner=QtCore.Qt.TopRightCorner)
        # filter
        self.hide_pairs.stateChanged.connect(self.filter_manager.init_filter)
        self.coinindex_filter.textChanged.connect(self.filter_manager.init_filter)

        # connect elements to functions

        self.debug2_button.clicked.connect(self.limit_pane.test_func)
        self.coin_selector.activated.connect(self.gui_manager.change_pair)
        self.hide_pairs.stateChanged.connect(partial(self.filter_manager.filter_table, self.coinindex_filter.text(), self.hide_pairs.checkState()))

        # debug
        self.wavg_button.clicked.connect(calc_wavg)
        self.calc_all_wavg_button.clicked.connect(partial(calc_all_wavgs, self))

        self.button_wavg.clicked.connect(calc_wavg)

        # connect buttons to fishing bot methods (refactor)
        self.fish_add_trade.clicked.connect(self.fish_bot.add_order)

        self.fish_clear_all.clicked.connect(partial(self.fish_bot.clear_all_orders, self))

        # Fix a linter error...
        self.chartLOL = QWebEngineView()


        # check if coin is an empty dict. If yes, api calls have not been answered.
        # TODO: refactor move into init manager
        current_coin = val.get("coin", None)
        if current_coin is not None:
            print("authenticated!")

            self.init_manager.api_init()

        # api credentials not valid; display welcome page
        else:
            self.show_error_page()


    def instantiate_managers(self):
        self.log_manager = BotLogger(self)
        self.log_manager.init_logging()

        self.cfg_manager = ConfigManager(self)
        # self.cfg.connect_cfg()
        self.cfg_manager.read_config()

        self.websocket_manager = WebsocketManager(self)

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

    # refactor: move; global ui
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


        # self.open_orders.setColumnWidth(10, 0)


        history_header = self.history_table.horizontalHeader()
        history_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)


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


    # cancel an order from a separate thread
    def cancel_order_byId(self, order_id, symbol):
        worker = Worker(partial(self.api_manager.api_cancel_order, app.client, order_id, symbol))
        # worker.signals.progress.connect(self.cancel_callback)
        self.threadpool.start(worker)



    def shutdown_bot(self):
        self.cfg_manager.write_stats()
