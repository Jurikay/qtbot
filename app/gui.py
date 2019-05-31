# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


import os
import platform
from datetime import datetime
from functools import partial
from pathlib import Path

import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import yappi
from PyQt5.QtWebEngineWidgets import QWebEngineView  # QWebEnginePage
from PyQt5.uic import loadUi
from twisted.internet import reactor
from twisted.internet.error import ReactorNotRunning

import app
from app.api.apiFunctions import ApiCalls
from app.api.new_api_data import ApiManager
from app.api.websocket_manager import WebsocketManager
from app.data.datamanager import DataManager
from app.data.user_data import UserData
from app.elements.telegram_bot import TelegramBot
from app.elements.custom_logger import BotLogger
from app.helpers import resource_path
from app.new_gui import GuiMgr
from app.sounds import Sounds


class beeserBot(QtWidgets.QMainWindow):
    """Main ui class."""

    def __init__(self, cfg_manager):
        
        # Move out as much as possible. Init gui first, load data later.

        # self.data = DataManager()
        """Main gui init method."""

        super(beeserBot, self).__init__()


        # Set application icon; TODO: Change to minimalistic version

        self.data = None
        app.mw = self
        self.cfg_manager = cfg_manager
        self.version = "beta 0.1"

        self.client = app.client
        
        # has to be defined in init
        self.threadpool = QtCore.QThreadPool()
        self.mutex = QtCore.QMutex()
        app.threadpool = self.threadpool
        app.mutex = self.mutex

        self.error = None

        self.trade_history = list()
        self.is_connected = False

        # self.dict_update = False
        # self.np_update = False
        # self.pd_update = False

        self.load_ui_files()
        
        self.klines = dict()  # TODO: remove
        self.klines["1m"] = dict()

        self.sound_manager = None
        self.log_manager = None
        self.user_data = None
        print("### END GUI INIT ###")
        self.setup()


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
        self.centerOnScreen()


    def set_corner_widgets(self):
        self.tabsBotLeft.setCornerWidget(self.coin_index_filter)
        self.ChartTabs.setCornerWidget(self.volume_widget)
        # self.ChartTabs.adjustSize()

    def setup(self):
        """One time ui setup after load. Moved out of __init__ to display
        UI asap."""

        print("### BEGIN SETUP")

        # Set System Time
        if platform.system() == "Windows":
            from app.elements.timescript import set_system_time
            set_system_time()
        
        
        self.data = DataManager()


        # instantiate various helper classes
        self.init_basics()

        self.init_api_classes()

        

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

        # self.cfg_manager = ConfigManager(self)
        # self.cfg_manager.initialize()


        # new gui
        self.gui_mgr = GuiMgr(self)
        self.gui_mgr.set_api_independant()



        self.sound_manager = Sounds(self)

        self.telegram_bot = TelegramBot("845873423:AAE-w23y9a_BU4ARGwoQzCE-0RHOKaZa-5s", "97886168")


        # TODO: Add sound manager / data manager

        # self.hotkey_manager = HotKeys(self)
        # self.hotkey_manager.init_hotkeys()

        

    def init_api_classes(self):
        # TODO: Refactor whacky order



        self.api_manager = ApiCalls(self, self.threadpool)
        # self.api_manager.initialize()

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
            print("is_connected: TRUE")

            self.instantiate_api_managers()
            self.initialize_user_data()

        else:
            print("NOT CONNECTED!")
            self.gui_mgr.disable_ui()
            # self.chart.setHtml(welcome_page())

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

        # self.gui_manager = GuiManager(self, self.threadpool)
        
        # self.gui_manager.api_init()
        self.websocket_manager.schedule_websockets()
        self.gui_mgr.setup()

        # TODO set worker thread for api data from here,
        # on callback, get user_data
        self.new_api.threaded_setup()
        # self.new_api.data_setup()
        # self.new_api.api_calls()


    def initialize_tables(self):
        """The following is needed:
        user_data, live_data"""
        # self.open_orders_view.setup()
        # # self.index_view.setup()
        # self.holdings_view.setup()
        # self.trade_history_view.setup()


        # self.new_asks.setup()
        # self.new_bids.setup()
        # self.tradeTable.setup()

        # Bottom table filtering
        self.coinindex_filter.textChanged.connect(
            self.open_orders_view.my_model.set_filter)
        self.coinindex_filter.textChanged.connect(
            self.trade_history_view.my_model.set_filter)
        self.coinindex_filter.textChanged.connect(
            self.holdings_view.my_model.set_filter)
        self.coinindex_filter.textChanged.connect(
            self.index_view.my_model.set_filter)


        search_text = self.coinindex_filter.text()
        print("search_text:", search_text)
        self.cb_history_time.currentIndexChanged.connect(self.trade_history_view.my_model.set_filter)


        self.hide_pairs.stateChanged.connect(
            self.holdings_view.my_model.set_current_coin)

        self.btn_cancel_all.clicked.connect(self.user_data.cancel_all)



    def initialize_user_data(self):
        self.user_data = UserData(self, self.mutex, self.threadpool)
        # self.user_data.initialize()



    # refactor: move; global ui

    # refactor into tables, config etc

    # def delayed_stuff(self):

    #     print("delayed")

    #     # self.asks_table.scrollToBottom()
    #     self.new_asks.scrollToBottom()

    #     # start periodic historical data loop # TODO FIX; REENABLE
    #     # self.historical.get_kline_values()
    #     self.gui_mgr.set_api_dependant()

        # self.timer.stop()
        # logging.info('Finishing setup...')

    def centerOnScreen(self):
        """Centers the main window on the screen."""
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

    def shutdown_bot(self):
        """Called immediately before the application terminates."""
        self.telegram_bot.stop_message()
        # self.cfg_manager.write_stats()
        self.gui_mgr.save_stats()
        self.gui_mgr.save_config()

        # api error workaround
        try:
            self.websocket_manager.socket_mgr.close()
        except AttributeError:
            pass

        try:
            reactor.stop()
        except ReactorNotRunning:
            pass
