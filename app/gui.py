# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


import logging
from datetime import datetime
from functools import partial

import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import yappi
from PyQt5.QtWebEngineWidgets import QWebEngineView  # QWebEnginePage
from PyQt5.uic import loadUi
from twisted.internet import reactor
from twisted.internet.error import ReactorNotRunning

# from app.charts import Webpages as Webpages
# from app.gui_functions import (calc_wavg, calc_all_wavgs)
# filter_coin_index, global_filter, filter_confirmed,
# from app.strategies.fishing_bot import FishingBot
# from app.strategies.limit_order import LimitOrder
import app
from app.api.apiFunctions import ApiCalls
# from app.data.historical_data import HistoricalData
from app.data.user_data import UserData
from app.elements.config import ConfigManager
# from app.elements.hotkeys import HotKeys
# from app.elements.kline_data import KlineManager
# from app.elements.test_class import TestKlasse
# from app.elements.init_manager import InitManager
from app.elements.custom_logger import BotLogger
from app.elements.gui_manager import GuiManager
# from app.tables.table_manager import TableManager
from app.api.websocket_manager import WebsocketManager

from app.data.datamanager import DataManager
from app.api.new_api_data import ApiManager

from app.new_gui import GuiMgr

import platform
import os
from pathlib import Path

from app.helpers import resource_path

# from PyQt5.QtMultimedia import QSoundEffect, QMediaPlayer, QMediaContent, QSound
# from app.data.index_data import IndexData


class beeserBot(QtWidgets.QMainWindow):
    """Main ui class."""

    def __init__(self):
        
        # Move out as much as possible. Init gui first, load data later.

        # self.data = DataManager()
        """Main gui init method."""

        super(beeserBot, self).__init__()


        # Set application icon; TODO: Change to minimalistic version

        self.data = None
        app.mw = self
        self.version = "alpha 0.1"

        self.client = app.client
        
        # has to be defined in init
        self.threadpool = QtCore.QThreadPool()
        self.mutex = QtCore.QMutex()
        app.threadpool = self.threadpool
        app.mutex = self.mutex

        self.error = None
        self.index_data = None

        self.trade_history = list()

        self.tickers = None


        self.orderbook = dict()
        self.klines = dict()
        self.klines["1m"] = dict()
        self.is_connected = False
        self.new_coin_table = False

        self.dict_update = False
        self.np_update = False
        self.pd_update = False

        self.decimals = 0
        self.assetDecimals = 0


        self.load_ui_files()
        print("### END GUI INIT ###")


    def load_fonts(self):
        name = "SourceSansPro-"
        variations = ["Black", "Bold", "Light", "Regular", "Semibold"]

        for v in variations:
            path = resource_path("ui/" + name + v + ".ttf")
            QtGui.QFontDatabase.addApplicationFont(path)

    def load_ui_files(self):
        """Load ui files/ stylesheet."""

        self.setWindowIcon(QtGui.QIcon(resource_path("images/assets/ico.ico")))

        # Load external ui files in such a way that they are expected next to the executable if bundled.
        uifile_path = resource_path("ui/MainWindow.ui")
        uistyle_path = resource_path("ui/style.qss")
        # uifont_path = resource_path("ui/SourceSansPro-Regular.ttf")
        
        # Add external font
        # QtGui.QFontDatabase.addApplicationFont(uifont_path)
        self.load_fonts()


        # Load ui file
        loadUi(uifile_path, self)

        # Set external stylesheet
        with open(uistyle_path, "r") as fh:
            self.setStyleSheet(fh.read())

        self.set_corner_widgets()


    def set_corner_widgets(self):
        self.tabsBotLeft.setCornerWidget(self.coin_index_filter)
        self.tabsBotLeft.adjustSize()

        self.coin_index_filter.adjustSize()

        self.ChartTabs.setCornerWidget(self.volume_widget)
        self.ChartTabs.adjustSize()

    def setup(self):
        """One time ui setup after load. Moved out of __init__ to display
        UI asap."""

        print("### BEGIN SETUP")

        # Set System Time
        if platform.system() == "Windows":
            from app.elements.timescript import set_system_time
            set_system_time()
        
        

        print("I AM SELF", self)

        self.data = DataManager()


        # instantiate various helper classes
        self.init_basics()

        self.init_api_classes()

        self.centerOnScreen()

        # connect limit pane ui elements to functions
        # this is done outside __init__ since not all ui elements are loaded then
        self.limit_pane.connect_elements()


        print("### END SETUP")


    def init_basics(self):
        """General stuff that has to be initialized,
        that does not rely on the gui nor is api related."""
        
        # Todo: Refactor
        self.log_manager = BotLogger(self)
        self.log_manager.init_logging()

        self.cfg_manager = ConfigManager(self)
        self.cfg_manager.initialize()


        # new gui
        self.gui_mgr = GuiMgr(self)
        self.gui_mgr.set_api_dependant()

        # TODO: Add sound manager / data manager

        # self.hotkey_manager = HotKeys(self)
        # self.hotkey_manager.init_hotkeys()

        

    def init_api_classes(self):
        # TODO: Refactor whacky order

        self.api_manager = ApiCalls(self, self.threadpool)
        # self.api_manager.initialize()

        self.api_manager.new_api()

        self.new_api = ApiManager(self, self.api_manager.client, self.threadpool)


        self.check_connection()


        # newer not newest


        # self.init_manager = InitManager(self)
        # self.init_manager.initialize()

        
    # TODO: Refactor; 4 states: offline, binance unreachable, banned, authenticated
    # move to different file
    def check_connection(self):
        """Check if an api connection has been established. If so, initialize
        several helper classes."""
        if self.is_connected:
            self.initialize_user_data()
            self.instantiate_api_managers()
            # self.coin_selector.activated.connect(self.gui_manager.change_pair)
            self.initialize_tables()

        else:
            self.gui_mgr.disable_ui()

            # TODO: Implement error pages
            # if self.api_manager.error == "banned":
            #     self.init_manager.show_banned_page()

            # elif self.api_manager.error == "time":
            #     self.init_manager.show_time_error_page()

            # else:
                # self.init_manager.show_error_page()

    def instantiate_api_managers(self):
        self.websocket_manager = WebsocketManager(
            self, self.threadpool, app.client, self.mutex)

        # self.table_manager = TableManager(self)
        # self.table_manager.init_filter()

        self.gui_manager = GuiManager(self, self.threadpool)
        self.gui_manager.initialize()


        

        
    def initialize_tables(self):
        # self.coin_index.initialize()
        # self.open_orders.initialize()
        # self.history_table.initialize()
        # self.holdings_table.initialize()

        # new:
        # self.test_table_view.setup()

        # self.test_table_view_2.setup()

        # This is used
        self.open_orders_view.setup()
        self.trade_history_view.setup()
        # self.index_view.setup()
        self.holdings_view.setup()

        # Bottom table filtering
        self.coinindex_filter.textChanged.connect(
            self.open_orders_view.my_model.setFilter)
        self.coinindex_filter.textChanged.connect(
            self.trade_history_view.my_model.setFilter)
        self.coinindex_filter.textChanged.connect(
            self.holdings_view.my_model.setFilter)
        self.coinindex_filter.textChanged.connect(
            self.index_view.my_model.setFilter)

        self.hide_pairs.stateChanged.connect(
            self.index_view.my_model.set_current_coin)
        self.cancel_all.clicked.connect(self.user_data.cancel_all)

        # self.init_asks_btn.clicked.connect(self.asks_view.setup)
        # self.init_asks_btn.clicked.connect(self.bids_rebuild.setup)
        # self.btn_ud.clicked.connect(self.bids_rebuild.update)
        # self.asks_view.setup()
        # self.new_asks.setup()
        # self.new_bids.setup()

        # self.new_asks.setup()

    def initialize_user_data(self):
        # TEST/REFACTOR
        # self.index_data = IndexData(self, self.threadpool)
        # self.historical = HistoricalData(self, app.client, self.threadpool)

        self.user_data = UserData(self, self.mutex)
        self.user_data.initialize()
        # INITITALIZE API HEAVY STUFF TODO refactor; skip api parameter
        # if not val["jirrik"]:
        # self.user_data.initial_open_orders()


    # refactor: move; global ui

    # refactor into tables, config etc

    def delayed_stuff(self):

        print("delayed")

        # self.asks_table.scrollToBottom()
        self.new_asks.scrollToBottom()

        # start periodic historical data loop # TODO FIX; REENABLE
        # self.historical.get_kline_values()
        self.gui_mgr.set_api_dependant()

        self.timer.stop()
        logging.info('Finishing setup...')

    def centerOnScreen(self):
        """Centers the main window on the screen."""
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

    def shutdown_bot(self):
        # func_stats = yappi.get_func_stats()
        # func_stats.save('callgrind.out.' +
        #                 datetime.now().isoformat(), 'CALLGRIND')
        # yappi.stop()
        # yappi.clear_stats()
        self.cfg_manager.write_stats()
        self.cfg_manager.write_config()
        # api error workaround
        try:
            self.websocket_manager.socket_mgr.close()
        except AttributeError:
            pass
        # self.chart.stop()
        # self.btc_chart.stop()
        try:
            reactor.stop()
        except ReactorNotRunning:
            pass

    def slider_value(self):
        # self.setProperty("value", value)
        value = self.test_slider_value.value()
        self.test_slider.setSliderPosition(value)
        self.test_slider_label.setText(str(int(value)))

    def spinbox_value(self, value):
        self.test_slider_value.setValue(float(value))


# class DataManager:
#     """Class to hold and manage api and websocket data."""

#     def __init__(self, mw):
#         """Initialize storage variables."""

#         self.mw = mw

#         self.coins = dict()

#         self.trade_history = list()
#         self.tickers = dict()
#         self.klines = dict()
#         self.bids = list()
#         self.asks = list()

#         self.my_trades = list()
#         self.open_orders = list()

#         self.account_holdings = dict()

#         self.decimals = 0
#         self.assetDecimals = 0

#     def get_specific(self, kind, coin):
#         pass