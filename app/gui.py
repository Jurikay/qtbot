# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Main gui class."""

# import configparser
import time
import logging

from datetime import timedelta
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
                               init_filter, calc_all_wavgs)
# filter_coin_index, global_filter, filter_confirmed,
from app.init import val
from app.strategies.fishing_bot import FishingBot
# from app.strategies.limit_order import LimitOrder
import app
from app.elements.config import ConfigManager
from app.elements.hotkeys import HotKeys
# from app.elements.kline_data import KlineManager
from app.elements.test_class import TestKlasse


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

        init_logging(self)

        # INIT THREADING
        self.threadpool = QtCore.QThreadPool()
        app.threadpool = self.threadpool
        logging.info('Enable multithreading with %d threads.' % self.threadpool.maxThreadCount())


        # instantiate various helper classes

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

        # self.kline_manager = KlineManager(self)
        # self.kline_manager.start_kline_check()
        self.coin_index.start_kline_check()

        set_modes(self)

        main_init(self)

        # initialize open orders table
        self.open_orders.initialize()

        # initialize limit order signals and slots
        self.limit_pane.initialize()


        # connect elements to functions

        # self.reset_vol_direct.clicked.connect(self.reset_vol_direction)

        self.debug2_button.clicked.connect(self.limit_pane.test_func)

        # self.open_orders.cellClicked.connect(self.limit_pane.open_orders_cell_clicked)

        self.coin_selector.activated.connect(self.change_pair)

        self.hide_pairs.stateChanged.connect(partial(partial(filter_table, self), self.coinindex_filter.text(), self.hide_pairs.checkState()))

        self.tabsBotLeft.setCornerWidget(self.coin_index_filter, corner=QtCore.Qt.TopRightCorner)
        # self.debug_corner.clicked.connect(self.set_corner_widget)

        # debug
        self.wavg_button.clicked.connect(calc_wavg)
        self.calc_all_wavg_button.clicked.connect(partial(calc_all_wavgs, self))

        self.button_wavg.clicked.connect(calc_wavg)



        # connect buttons to fishing bot methods
        self.fish_add_trade.clicked.connect(self.fish_bot.add_order)

        self.fish_clear_all.clicked.connect(partial(self.fish_bot.clear_all_orders, self))


        # self.button_klines.clicked.connect(self.iterate_through_klines)

        # filter
        self.hide_pairs.stateChanged.connect(partial(init_filter, self))
        self.coinindex_filter.textChanged.connect(partial(init_filter, self))

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

            self.initialize()

        # api credentials not valid; display welcome page
        else:
            self.chart.setHtml(Webpages.welcome_page())
            self.chart.show()
            self.bot_tabs.setCurrentIndex(4)

            self.api_key.setStyleSheet("border: 2px solid #f3ba2e;")
            self.api_secret.setStyleSheet("border: 2px solid #f3ba2e;")



    # gui init
    def initialize(self):
        """One-time gui initialization."""
        self.api_manager.api_calls()

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

    # main gui
    def change_pair(self):
        newcoin = self.coin_selector.currentText()

        if any(newcoin + "BTC" in s for s in val["coins"]) and newcoin != val["coin"]:
            val["pair"] = newcoin + "BTC"
            val["bm"].stop_socket(val["aggtradeWebsocket"])
            val["bm"].stop_socket(val["depthWebsocket"])
            val["bm"].stop_socket(val["klineWebsocket"])
            logging.info('Switching to %s' % newcoin + " / BTC")

            self.api_manager.set_pair_values()

            initial_values(self)

            self.websockets_symbol()

            self.history_table.setRowCount(0)

            self.api_manager.api_calls()

            init_filter(self)


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
            self.holdings_table.update_holding_prices()
            val["indexTabOpen"] = False
        elif tab_index_botLeft == 0:
            self.coin_index.update_coin_index_prices()

            # decouple eventually
            self.coin_index.start_kline_iterator()
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
    # def play_sound_effect(self):
    #     # self.sound_1.play()
    #     print("playung sound")

    # debug
    # def reset_vol_direction(self):
    #     val["volDirection"] = 0


    # global ui
    def schedule_work(self):

        # Pass the function to execute
        worker = Worker(self.check_for_update)

        # Any other args, kwargs are passed to the run function
        # worker.signals.result.connect(self.print_output)
        worker.signals.progress.connect(self.tick)

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


    def shutdown_bot(self):
        self.cfg_manager.write_stats()

#################################


# gui init
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
    """One time gui initialization."""
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


# logging
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
