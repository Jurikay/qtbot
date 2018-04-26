# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


import logging
# from functools import partial
import PyQt5.QtCore as QtCore
# import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWebEngineWidgets import QWebEngineView  # QWebEnginePage
# from PyQt5.QtMultimedia import QSoundEffect, QMediaPlayer, QMediaContent, QSound

from app.apiFunctions import ApiCalls
# from app.charts import Webpages as Webpages
from app.gui_functions import (calc_wavg, calc_all_wavgs)
# filter_coin_index, global_filter, filter_confirmed,
# from app.init import val
# from app.strategies.fishing_bot import FishingBot
# from app.strategies.limit_order import LimitOrder
import app
from app.elements.config import ConfigManager
from app.elements.hotkeys import HotKeys
# from app.elements.kline_data import KlineManager
# from app.elements.test_class import TestKlasse
from app.elements.init_manager import InitManager
from app.elements.custom_logger import BotLogger
from app.elements.gui_manager import GuiManager
from app.tables.table_manager import TableManager
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

        self.trade_history = list()
        self.klines = dict()
        self.klines["1m"] = dict()
        self.is_connected = False
        self.new_coin_table = False

        # load QtDesigner UI file
        loadUi("ui/MainWindow.ui", self)


        # set external stylesheet
        with open("ui/style.qss", "r") as fh:
            self.setStyleSheet(fh.read())


        # instantiate various helper classes
        self.init_basics()

        self.centerOnScreen()

        # initialize limit order signals and slots
        self.limit_pane.initialize()

        self.fishbot_table.initialize()


        # connect elements to functions
        self.chart.inject_script()

        self.debug2_button.clicked.connect(self.limit_pane.test_func)
        self.wavg_button.clicked.connect(calc_wavg)
        self.calc_all_wavg_button.clicked.connect(calc_all_wavgs)
        self.btn_reload_api.clicked.connect(self.init_basics)

        # Fix a linter error...
        self.linterfix = QWebEngineView()


        self.table_view_btn.clicked.connect(self.test_table_view.setup)
        self.add_btn.clicked.connect(self.test_table_view.my_model.new_append)



    def init_basics(self):
        self.log_manager = BotLogger(self)
        self.log_manager.init_logging()

        self.cfg_manager = ConfigManager(self)
        self.cfg_manager.initialize()

        self.hotkey_manager = HotKeys(self)
        self.hotkey_manager.init_hotkeys()

        self.init_api_classes()

    def init_api_classes(self):

        self.api_manager = ApiCalls(self, self.threadpool)
        self.api_manager.initialize()

        self.init_manager = InitManager(self)
        self.init_manager.initialize()

        self.check_connection()


    def check_connection(self):
        if self.is_connected is True:
            self.instantiate_api_managers()
            self.coin_selector.activated.connect(self.gui_manager.change_pair)
            self.initialize_tables()
        else:
            self.init_manager.show_error_page()



    def instantiate_api_managers(self):
        self.websocket_manager = WebsocketManager(self, self.threadpool, self.client)

        self.table_manager = TableManager(self)
        self.table_manager.init_filter()

        self.gui_manager = GuiManager(self)
        self.gui_manager.initialize()



    def initialize_tables(self):
        self.coin_index.initialize()
        self.open_orders.initialize()
        self.history_table.initialize()
        self.holdings_table.initialize()


    # refactor: move; global ui


    # refactor into tables, config etc
    def delayed_stuff(self):

        print("delayed")


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
        self.cfg_manager.write_config()
