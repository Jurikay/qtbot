# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


import logging
from functools import partial
# from app.init import val


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
# from app.tables.table_manager import TableManager
from app.elements.websocket_manager import WebsocketManager

from app.data.index_data import IndexData
from app.data.historical_data import HistoricalData
from app.data.user_data import UserData
# from app.init import val


class beeserBot(QtWidgets.QMainWindow):
    """Main ui class."""

    def __init__(self):

        """Main gui init method."""

        super(beeserBot, self).__init__()

        self.version = "alpha 0.1"

        self.client = app.client
        self.threadpool = QtCore.QThreadPool()
        self.mutex = QtCore.QMutex()
        app.threadpool = self.threadpool
        app.mw = self
        app.mutex = self.mutex

        self.error = None
        self.index_data = None

        self.trade_history = list()

        self.tickers = None

        # kann weg:
        # self.trade_history = list()
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

        # load QtDesigner UI file
        loadUi("ui/MainWindow.ui", self)

        # self.button_testgo.clicked.connect(self.new_asks.setup)
        # self.button_testgo.clicked.connect(self.new_bids.setup)

        # self.delayer0 = DelayedUpdater(self.chart)
        self.delayer1 = DelayedUpdater(self.open_orders_view)

        self.delayer2 = DelayedUpdater(self.tradeTable)
        # self.delayer3 = DelayedUpdater(self.volumes_widget)
        self.delayer4 = DelayedUpdater(self.new_asks)
        self.delayer5 = DelayedUpdater(self.new_bids)


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

        # self.debug2_button.clicked.connect(self.limit_pane.test_func)
        self.wavg_button.clicked.connect(calc_wavg)
        self.calc_all_wavg_button.clicked.connect(calc_all_wavgs)
        self.btn_reload_api.clicked.connect(self.init_basics)

        # Fix a linter error...
        self.linterfix = QWebEngineView()

        self.test_slider.valueChanged.connect(self.spinbox_value)
        self.test_slider_value.valueChanged.connect(self.slider_value)
        self.btn_my_trades.clicked.connect(partial(self.api_manager.api_my_trades, self.cfg_manager.pair))

        self.table_test_btn.clicked.connect(self.open_orders_view.setup)
        self.table_test_btn.clicked.connect(self.trade_history_view.setup)
        self.table_test_btn.clicked.connect(self.index_view.setup)
        self.table_test_btn.clicked.connect(self.holdings_view.setup)

        # connect filter
        # self.coinindex_filter.textChanged.connect(self.open_orders_view.my_model.setFilter)


        # self.table_view_btn.clicked.connect(self.test_table_view.setup)
        # self.add_btn.clicked.connect(self.historical.test_all)
        # self.jirrik_search.textEdited.connect(self.test_table_view.search_edited)
        # self.btn_init_new.clicked.connect(self.newer_index.setup)
        # self.test_ud_btn.clicked.connect(self.dict_index.update_model_data)
        # self.btn_init_pd.clicked.connect(self.user_data.initial_history)

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

        # new
        self.api_manager.new_api()

        self.init_manager = InitManager(self)
        self.init_manager.initialize()


        self.check_connection()


    def check_connection(self):
        if self.is_connected is True:
            self.initialize_data()
            self.instantiate_api_managers()
            self.coin_selector.activated.connect(self.gui_manager.change_pair)
            self.initialize_tables()

        else:
            if self.api_manager.error == "banned":
                self.init_manager.show_banned_page()
            
            elif self.api_manager.error == "time":
                self.init_manager.show_time_error_page()
            
            else:
                self.init_manager.show_error_page()




    def instantiate_api_managers(self):
        self.websocket_manager = WebsocketManager(self, self.threadpool, app.client, self.mutex)

        # self.table_manager = TableManager(self)
        # self.table_manager.init_filter()

        self.gui_manager = GuiManager(self)
        self.gui_manager.initialize()



    def initialize_tables(self):
        # self.coin_index.initialize()
        # self.open_orders.initialize()
        # self.history_table.initialize()
        # self.holdings_table.initialize()

        # new:
        # self.test_table_view.setup()

        # self.test_table_view_2.setup()
        self.open_orders_view.setup()
        self.trade_history_view.setup()
        self.index_view.setup()
        self.holdings_view.setup()

        self.coinindex_filter.textChanged.connect(self.open_orders_view.my_model.setFilter)
        self.coinindex_filter.textChanged.connect(self.trade_history_view.my_model.setFilter)
        self.coinindex_filter.textChanged.connect(self.holdings_view.my_model.setFilter)
        self.coinindex_filter.textChanged.connect(self.index_view.my_model.setFilter)

        self.hide_pairs.stateChanged.connect(self.index_view.my_model.set_current_coin)
        self.cancel_all.clicked.connect(self.user_data.cancel_all)

        # self.init_asks_btn.clicked.connect(self.asks_view.setup)
        # self.init_asks_btn.clicked.connect(self.bids_rebuild.setup)
        # self.btn_ud.clicked.connect(self.bids_rebuild.update)
        # self.asks_view.setup()
        # self.new_asks.setup()
        # self.new_bids.setup()

        # self.new_asks.setup()


    def initialize_data(self):
        self.index_data = IndexData(self, self.threadpool)
        self.historical = HistoricalData(self, app.client, self.threadpool)


        self.user_data = UserData(self, self.mutex)
        self.user_data.initialize()
        # INITITALIZE API HEAVY STUFF TODO refactor; skip api parameter
        # if not val["jirrik"]:
        # self.user_data.initial_open_orders()
        # self.historical.get_kline_values()

        self.create_df_btn.clicked.connect(self.user_data.create_history_df)



    # refactor: move; global ui


    # refactor into tables, config etc
    def delayed_stuff(self):

        print("delayed")


        # self.asks_table.scrollToBottom()
        self.new_asks.scrollToBottom()

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
        # api error workaround
        self.websocket_manager.socket_mgr.close()

        from twisted.internet import reactor

        reactor.stop()



    def slider_value(self):
        # self.setProperty("value", value)
        value = self.test_slider_value.value()
        self.test_slider.setSliderPosition(value)
        self.test_slider_label.setText(str(int(value)))

    def spinbox_value(self, value):
        self.test_slider_value.setValue(float(value))



class DataManager:
    """Class to hold and manage api and websocket data."""

    def __init__(self, mw):
        """Initialize storage variables."""

        self.mw = mw

        self.coins = dict()

        self.trade_history = list()
        self.tickers = dict()
        self.klines = dict()
        self.bids = list()
        self.asks = list()

        self.my_trades = list()
        self.open_orders = list()

        self.account_holdings = dict()

        self.decimals = 0
        self.assetDecimals = 0


    def get_specific(self, kind, coin):
        pass


class DelayedUpdater(QtCore.QObject):

    def __init__(self, target, parent=None):
        super(DelayedUpdater, self).__init__(parent)
        self.target = target
        target.installEventFilter(self)

        self.delayEnabled = True
        self.delayTimeout = 200

        self._resizeTimer = QtCore.QTimer()
        self._resizeTimer.timeout.connect(self._delayedUpdate)

    def eventFilter(self, obj, event):
        if self.delayEnabled and obj is self.target:
            if event.type() == event.Resize:
                self._resizeTimer.start(self.delayTimeout)
                self.target.setUpdatesEnabled(False)

        return False

    def _delayedUpdate(self):
        self._resizeTimer.stop()
        self.target.setUpdatesEnabled(True)
