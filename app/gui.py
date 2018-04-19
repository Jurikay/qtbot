# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Main gui class."""


import logging
from functools import partial
import PyQt5.QtCore as QtCore
# import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWebEngineWidgets import QWebEngineView  # QWebEnginePage

# from PyQt5.QtMultimedia import QSoundEffect, QMediaPlayer, QMediaContent, QSound

from app.apiFunctions import ApiCalls
from app.charts import Webpages as Webpages
from app.gui_functions import (calc_wavg, calc_all_wavgs)
# filter_coin_index, global_filter, filter_confirmed,
from app.init import val
# from app.strategies.fishing_bot import FishingBot
# from app.strategies.limit_order import LimitOrder
import app
from app.elements.config import ConfigManager
from app.elements.hotkeys import HotKeys
# from app.elements.kline_data import KlineManager
from app.elements.test_class import TestKlasse
from app.elements.init_manager import InitManager
from app.elements.custom_logger import BotLogger
from app.elements.gui_manager import GuiManager
from app.elements.table_filters import TableFilters
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

        self.centerOnScreen()

        self.initialize_tables()

        # initialize limit order signals and slots
        self.limit_pane.initialize()

        self.fishbot_table.initialize()


        # self.chart_button.clicked.connect(self.chart.inject_script)

        # belongs into filters class
        # filter

        # connect elements to functions
        self.chart.inject_script()
        self.debug2_button.clicked.connect(self.limit_pane.test_func)
        self.coin_selector.activated.connect(self.gui_manager.change_pair)
        self.wavg_button.clicked.connect(calc_wavg)
        self.calc_all_wavg_button.clicked.connect(partial(calc_all_wavgs, self))
        self.button_wavg.clicked.connect(calc_wavg)

        # connect buttons to fishing bot methods (refactor)

        # Fix a linter error...
        self.linterfix = QWebEngineView()


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
        self.cfg_manager.read_config()

        self.websocket_manager = WebsocketManager(self)

        self.api_manager = ApiCalls(self, self.threadpool)
        self.api_manager.initialize()

        # instantiate fishing bot class
        # self.fishbot_table = FishingBot(self)

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


    def initialize_tables(self):
        self.coin_index.initialize()
        self.open_orders.initialize()
        self.open_orders.initialize()
        self.holdings_table.initialize()


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



    def centerOnScreen(self):
        """Centers the main window on the screen."""
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))


    def shutdown_bot(self):
        self.cfg_manager.write_stats()
