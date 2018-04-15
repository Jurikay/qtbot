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
# import PyQt5.Qt as Qt
import PyQt5.QtGui as QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
import PyQt5.QtWidgets as QtWidgets
from PyQt5.uic import loadUi
# from PyQt5.QtMultimedia import QSoundEffect, QMediaPlayer, QMediaContent, QSound


from app.apiFunctions import percentage_ammount
from app.callbacks import (Worker, api_depth, api_history, api_order_history, api_all_orders,
                           depthCallback, directCallback, tickerCallback,
                           userCallback, klineCallback)
from app.charts import Webpages as Webpages
from app.colors import Colors
from app.gui_functions import (build_coinindex, build_holdings, calc_total_btc,
                               calc_wavg, filter_coin_index, global_filter, filter_confirmed, initial_values, filter_table,
                               update_holding_prices, update_coin_index_prices, init_filter)
from app.init import val
from app.initApi import (BinanceAPIException, client, read_config,
                         set_pair_values)
from app.strategies.fishing_bot import FishingBot



class beeserBot(QtWidgets.QMainWindow):

    """Main ui class."""

    def __init__(self):
        """Init method."""
        super(beeserBot, self).__init__()
        loadUi("ui/MainWindow.ui", self)

        # set external stylesheet
        with open("ui/style.qss", "r") as fh:
            self.setStyleSheet(fh.read())

        qtLogger = QPlainTextEditLogger(self)
        qtLogger.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(qtLogger)
        # You can control the logging level
        logging.getLogger().setLevel(logging.INFO)

        self.widget_2.setWidget(qtLogger.widget)

        QtCore.QLocale.setDefault(QtCore.QLocale(QtCore.QLocale.C))

        self.update_count = 0
        self.no_updates = 0


        if val["debug"] is False:
            # self.tabsBotLeft.setTabEnabled(0, False)
            self.tabsBotLeft.removeTab(0)
            self.ChartTabs.removeTab(3)
            self.ChartTabs.removeTab(4)
            self.ChartTabs.removeTab(5)
            self.ChartTabs.setTabEnabled(1, False)

            self.tabsBotLeft.setCurrentIndex(0)
            self.ChartTabs.setCurrentIndex(0)
            self.bot_tabs.setCurrentIndex(0)
        else:
            logging.info("DEBUG mode enabled")

        logging.info('Initializing GUI')

        self.setWindowTitle("Juris beeser Bot")

        self.setWindowIcon(QtGui.QIcon('images/assets/256.png'))

        self.restart_warning.setStyleSheet("color: transparent;")
        # self.spread_area.setStyleSheet("background: #2e363d;")

        self.holdings_table.setStyleSheet("alternate-background-color: #2e363d;")

        self.counter = 0
        self.counter2 = 0

        # THREADING
        self.threadpool = QtCore.QThreadPool()
        logging.info('Enable multithreading with %d threads.' % self.threadpool.maxThreadCount())

        # define hotkeys
        hotkey_F = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F), self)
        hotkey_F.activated.connect(partial(self.hotkey_pressed, "F"))

        hotkey_1 = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_1), self)
        hotkey_1.activated.connect(partial(self.hotkey_pressed, "1"))

        hotkey_2 = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_2), self)
        hotkey_2.activated.connect(partial(self.hotkey_pressed, "2"))

        hotkey_3 = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_3), self)
        hotkey_3.activated.connect(partial(self.hotkey_pressed, "3"))

        hotkey_4 = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_4), self)
        hotkey_4.activated.connect(partial(self.hotkey_pressed, "4"))

        hotkey_5 = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_5), self)
        hotkey_5.activated.connect(partial(self.hotkey_pressed, "5"))

        hotkey_6 = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_6), self)
        hotkey_6.activated.connect(partial(self.hotkey_pressed, "6"))

        hotkey_B = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_B), self)
        hotkey_B.activated.connect(partial(self.hotkey_pressed, "B"))

        hotkey_S = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_S), self)
        hotkey_S.activated.connect(partial(self.hotkey_pressed, "S"))

        hotkey_P = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_P), self)
        hotkey_P.activated.connect(partial(self.hotkey_pressed, "P"))

        hotkey_A = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_A), self)
        hotkey_A.activated.connect(partial(self.hotkey_pressed, "A"))


        # connect elements to functions

        self.limit_buy_slider.valueChanged.connect(self.buy_slider)
        self.limit_sell_slider.valueChanged.connect(self.sell_slider)

        self.limit_buy_input.valueChanged.connect(self.calc_total_buy)
        self.limit_sell_input.valueChanged.connect(self.calc_total_sell)

        self.limit_button0.clicked.connect(self.limit_percentage)
        self.limit_button1.clicked.connect(self.limit_percentage)
        self.limit_button2.clicked.connect(self.limit_percentage)
        self.limit_button3.clicked.connect(self.limit_percentage)
        self.limit_button4.clicked.connect(self.limit_percentage)

        self.limit_sbutton0.clicked.connect(self.limit_percentage_sell)
        self.limit_sbutton1.clicked.connect(self.limit_percentage_sell)
        self.limit_sbutton2.clicked.connect(self.limit_percentage_sell)
        self.limit_sbutton3.clicked.connect(self.limit_percentage_sell)
        self.limit_sbutton4.clicked.connect(self.limit_percentage_sell)

        self.reset_vol_direct.clicked.connect(self.reset_vol_direction)

        self.save_config.clicked.connect(self.write_config)

        self.tradeTable.cellClicked.connect(self.cell_was_clicked)
        self.bids_table.cellClicked.connect(self.bids_cell_clicked)
        self.asks_table.cellClicked.connect(self.asks_cell_clicked)

        self.open_orders.cellClicked.connect(self.open_orders_cell_clicked)

        self.coin_selector.activated.connect(self.change_pair)

        self.limit_outbid.clicked.connect(self.overbid_undercut)
        self.limit_undercut.clicked.connect(self.overbid_undercut)
        self.limit_high.clicked.connect(self.overbid_undercut)
        self.limit_low.clicked.connect(self.overbid_undercut)

        self.limit_sell_amount.valueChanged.connect(self.check_sell_ammount)
        self.limit_buy_amount.valueChanged.connect(self.check_buy_amount)

        self.limit_sell_input.valueChanged.connect(self.check_sell_ammount)
        self.limit_buy_input.valueChanged.connect(self.check_buy_amount)

        self.hide_pairs.stateChanged.connect(partial(partial(filter_table, self), self.coinindex_filter.text(), self.hide_pairs.checkState()))

        self.tabsBotLeft.setCornerWidget(self.coin_index_filter, corner=QtCore.Qt.TopRightCorner)
        self.debug_corner.clicked.connect(self.set_corner_widget)

        # instantiate fishing bot class
        fish_bot = FishingBot(self)

        # connect buttons to fishing bot methods
        self.fish_add_trade.clicked.connect(partial(fish_bot.add_order, self))
        self.fish_clear_all.clicked.connect(partial(fish_bot.clear_all_orders, self))


        self.button_klines.clicked.connect(self.iterate_through_klines)
        # self.player = QMediaPlayer()
        # sound = QMediaContent(QtCore.QUrl.fromLocalFile("sounds/Tink.wav"))
        # self.player.setMedia(sound)
        # self.player.setVolume(1)

        self.limit_buy_button.clicked.connect(self.create_buy_order)
        self.limit_sell_button.clicked.connect(self.create_sell_order)

        self.button_wavg.clicked.connect(calc_wavg)

        # self.coinindex_filter.textChanged.connect(partial(filter_table, self))
        # self.coinindex_filter.returnPressed.connect(partial(filter_confirmed, self))
        self.hide_pairs.stateChanged.connect(partial(init_filter, self))
        self.coinindex_filter.textChanged.connect(partial(init_filter, self))

        # change corner widget bottom left tabs
        self.tabsBotLeft.currentChanged.connect(self.set_corner_widget)

        self.get_all_orders_button.clicked.connect(self.get_all_orders)
        # Fix a linter error...
        self.chartLOL = QWebEngineView()

        url = Webpages.build_cmc(self)
        self.cmc_chart.load(QtCore.QUrl(url))

        # url = Webpages.build_binance_info(self)
        # self.binance_info.load(QtCore.QUrl(url))

        # set config values
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

        for _ in range(20):
            self.bids_table.insertRow(0)
            self.asks_table.insertRow(0)
            self.new_table.insertRow(0)

        for _ in range(50):
            self.tradeTable.insertRow(0)


    def initialize(self):

        self.api_calls()

        for coin in val["coins"]:

            icon = QtGui.QIcon("images/ico/" + coin[:-3] + ".svg")

            self.coin_selector.addItem(icon, coin[:-3])

        self.coin_selector.model().sort(0)
        self.coin_selector.setIconSize(QtCore.QSize(25, 25))

        coinIndex = self.coin_selector.findText(val["coin"])
        self.coin_selector.setCurrentIndex(coinIndex)

        initial_values(self)

        self.schedule_websockets()
        self.schedule_work()

        build_holdings(self)

        build_coinindex(self)

        self.start_kline_check()

        worker = Worker(api_all_orders)
        worker.signals.progress.connect(self.build_open_orders)
        self.threadpool.start(worker)

        # self.sound_1 = QSound('sounds/Tink.wav')

        self.timer = QtCore.QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.delayed_stuff)
        self.timer.start()


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
        self.history_table.setColumnWidth(2, 60)
        self.history_table.setColumnWidth(5, 120)
        self.holdings_table.setColumnWidth(0, 150)

        self.holdings_table.setColumnWidth(1, 75)
        self.holdings_table.setColumnWidth(7, 120)

        self.fishbot_table.setColumnWidth(1, 60)
        self.fishbot_table.setColumnWidth(2, 60)
        self.fishbot_table.setColumnWidth(4, 100)
        self.fishbot_table.setColumnWidth(5, 120)
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



    def shutdown_bot(self):
        self.write_stats()

    def set_corner_widget(self):
        tabIndex = self.tabsBotLeft.currentIndex()
        print("tab index: " + str(tabIndex))
        # time.sleep(0.1)
        # print(str(self))
        # if tabIndex <= 2:
        #     self.tabsBotLeft.setCornerWidget(self.corner_widget1, corner=QtCore.Qt.TopRightCorner)
        # else:
        # self.tabsBotLeft.setCornerWidget(QtWidgets.QPushButton("Teasdasdsdst"), corner=QtCore.Qt.TopRightCorner)
        # self.tabsBotLeft.tabBar().setExpanding(False)
        # self.tabsBotLeft.updateGeometry()
        # if tabIndex == 0:
            # self.hide_pairs.hide()
        # else:
        #     self.hide_pairs.show()
        if tabIndex == 0:
            self.index_buttons.show()
        else:
            self.index_buttons.hide()


    def toggle_other_pairs(self, state):
        print(str(state))
        if state == 2:
            filter_table(self, self.coinindex_filter.text(), state)
            # self.open_orders.setSortingEnabled(False)
        else:
            self.show_other_pairs()
            self.open_orders.setSortingEnabled(True)



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


    def show_other_pairs(self):
        for row in range(self.open_orders.rowCount()):
            self.open_orders.setRowHidden(row, False)
        for row in range(self.holdings_table.rowCount()):
            self.holdings_table.setRowHidden(row, False)
        for row in range(self.coin_index.rowCount()):
            self.coin_index.setRowHidden(row, False)


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

            set_pair_values()
            initial_values(self)

            self.websockets_symbol()

            self.history_table.setRowCount(0)
            # self.open_orders.setRowCount(0)
            val["history"] = dict()


            self.api_calls()

            url = Webpages.build_cmc(self)
            self.cmc_chart.load(QtCore.QUrl(url))

            # url = Webpages.build_binance_info(self)
            # self.binance_info.load(QtCore.QUrl(url))

            # state = self.hide_pairs.checkState()
            # self.toggle_other_pairs(state)
            init_filter(self)

    def reset_vol_direction(self):
        val["volDirection"] = 0

    def open_orders_cell_clicked(self, row, column):
        if column == 11:

            order_id = str(self.open_orders.item(row, 10).text())
            pair = str(self.open_orders.item(row, 2).text())

            # cancel = (cancel_order(client, id, pair))

            self.cancel_order_byId(order_id, pair)

            # if str(cancel["orderId"]) == str(id):
            #     self.open_orders.removeRow(row)


    def cell_was_clicked(self, row, column):

        try:
            self.limit_buy_input.setValue(float(val["globalList"][row]["price"]))
            self.limit_sell_input.setValue(float(val["globalList"][row]["price"]))
            # value = percentage_ammount(val["accHoldings"]["BTC"]["free"], self.limit_buy_input.value(), int(self.buy_slider_label.text().strip("%")), val["assetDecimals"])
            # self.limit_buy_amount.setValue(value)
        except IndexError:
            pass

    def bids_cell_clicked(self, row, column):
        self.limit_buy_input.setValue(float(val["bids"][row][0]))
        self.limit_sell_input.setValue(float(val["bids"][row][0]))
        # value = percentage_ammount(val["accHoldings"]["BTC"]["free"], self.limit_buy_input.value(), int(self.buy_slider_label.text().strip("%")), val["assetDecimals"])
        # self.limit_buy_amount.setValue(value)



    def asks_cell_clicked(self, row, column):
        self.limit_buy_input.setValue(float(val["asks"][19 - row][0]))
        self.limit_sell_input.setValue(float(val["asks"][19 - row][0]))
        # value = percentage_ammount(val["accHoldings"]["BTC"]["free"], self.limit_buy_input.value(), int(self.buy_slider_label.text().strip("%")), val["assetDecimals"])
        # self.limit_buy_amount.setValue(value)

    def overbid_undercut(self):
        try:
            if self.sender().text() == "outbid":
                self.limit_buy_input.setValue(float(val["bids"][0][0]) + float(val["coins"][val["pair"]]["tickSize"]))
            elif self.sender().text() == "undercut":
                self.limit_sell_input.setValue(float(val["asks"][0][0]) - float(val["coins"][val["pair"]]["tickSize"]))
            elif self.sender().text() == "daily low":
                self.limit_buy_input.setValue(float(val["coins"][val["pair"]]["low"]))
            elif self.sender().text() == "daily high":
                self.limit_sell_input.setValue(float(val["coins"][val["pair"]]["high"]))
        except KeyError:
            pass



    # def print_output(self, s):
    #     print("scroll print_o")
    #     # self.asks_table.scrollToBottom()

    def hotkey_pressed(self, key):
        if key == "F":
            print("F")
        elif key == "1":
            self.bot_tabs.setCurrentIndex(0)
        elif key == "2":
            self.bot_tabs.setCurrentIndex(1)
        elif key == "3":
            self.bot_tabs.setCurrentIndex(2)
        elif key == "4":
            self.bot_tabs.setCurrentIndex(3)
        elif key == "5":
            self.bot_tabs.setCurrentIndex(4)
        elif key == "6":
            self.bot_tabs.setCurrentIndex(5)

        elif key == "B":
            self.limit_buy_input.setFocus()
        elif key == "S":
            self.limit_sell_input.setFocus()

        elif key == "A":
            if self.limit_buy_input.hasFocus():
                self.limit_buy_amount.setFocus()
            elif self.limit_sell_input.hasFocus():
                self.limit_sell_amount.setFocus()


    def tick(self, payload):
        # logging.debug('damn, a bug')
        # logging.info('something to remember')
        # logging.warning('that\'s not right')
        # logging.error('foobar')
        if payload == 1:
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
            # new_5m_change_value = (str(val["klines"]["1m"]))
            # new_15m_change_value = (str(val["klines"]["1m"]))

            # new_1h_change_value = (str(val["klines"]["1m"]))
            # self.change_15m.setText(new_15m_change_value)
            # self.change_1h.setText(new_1h_change_value)
            self.check_websocket()

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


        elif payload == 15:
            print("scroll to bottom")
            self.asks_table.scrollToBottom()

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

    def play_sound_effect(self):
        # self.sound_1.play()
        print("playung sound")


    def add_to_open_orders(self, order):

        # play a sound file to indicate a new order
        # print("play sound")

        # val["sound_1"].play()
        # QSoundEffect.play("sounds/Tink.mp3")

        # only add to open orders table if the coin is currently selected.
        # if order["symbol"] == val["pair"]:
        self.open_orders.insertRow(0)
        self.open_orders.setItem(0, 0, QtWidgets.QTableWidgetItem(str(datetime.fromtimestamp(int(str(order["time"])[:-3])).strftime('%d.%m.%y - %H:%M:%S.%f')[:-7])))

        coin = order["symbol"].replace("BTC", "")
        icon = QtGui.QIcon("images/ico/" + coin + ".svg")
        icon_item = QtWidgets.QTableWidgetItem()
        icon_item.setIcon(icon)
        self.open_orders.setItem(0, 1, icon_item)

        self.open_orders.setItem(0, 2, QtWidgets.QTableWidgetItem(order["symbol"]))


        self.btn_trade = QtWidgets.QPushButton("Trade " + coin)
        self.btn_trade.clicked.connect(self.gotoTradeButtonClicked)


        self.open_orders.setCellWidget(0, 3, self.btn_trade)

        self.open_orders.setItem(0, 4, QtWidgets.QTableWidgetItem(order["type"]))
        self.open_orders.setItem(0, 5, QtWidgets.QTableWidgetItem(order["side"]))
        price = '{number:.{digits}f}'.format(number=float(order["price"]), digits=val["decimals"])
        self.open_orders.setItem(0, 6, QtWidgets.QTableWidgetItem(price))
        qty = '{number:.{digits}f}'.format(number=float(order["origQty"]), digits=val["assetDecimals"]) + " " + coin
        self.open_orders.setItem(0, 7, QtWidgets.QTableWidgetItem(qty))

        filled_percent = '{number:.{digits}f}'.format(number=float(order["executedQty"]) / float(order["origQty"]), digits=2) + "%"

        self.open_orders.setItem(0, 8, QtWidgets.QTableWidgetItem(filled_percent))

        total_btc = '{number:.{digits}f}'.format(number=float(order["origQty"]) * float(order["price"]), digits=8) + " BTC"


        self.open_orders.setItem(0, 9, QtWidgets.QTableWidgetItem(total_btc))

        self.open_orders.setItem(0, 10, QtWidgets.QTableWidgetItem(str(order["orderId"])))

        self.open_orders.setItem(0, 11, QtWidgets.QTableWidgetItem("cancel"))

        self.open_orders.item(0, 11).setForeground(QtGui.QColor(Colors.color_yellow))

        if order["side"] == "BUY":
            self.open_orders.item(0, 5).setForeground(QtGui.QColor(Colors.color_green))
        else:
            self.open_orders.item(0, 5).setForeground(QtGui.QColor(Colors.color_pink))

        orders_header = self.open_orders.horizontalHeader()

        orders_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        orders_header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        orders_header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)

    def remove_from_open_orders(self, order):
        # if order["symbol"] == val["pair"]:
        items = self.open_orders.findItems(str(order["orderId"]), QtCore.Qt.MatchExactly)

            # findItems returns a list hence we iterate through it. We only expect one result though.
        for item in items:

                # get current row of coin to check
            row = item.row()
            self.open_orders.removeRow(row)

        if order["status"] == "FILLED":
                        logging.info('[ ✓ ] ORDER FILLED! %s' % str(order["symbol"]) + " " + str(order["side"]) + " " + str(float(order["executedQty"])) + "/" + str(float(order["origQty"])) + " filled at " + str(order["price"]))

        elif order["status"] == "CANCELED":
            logging.info('[ ✘ ] ORDER CANCELED! %s' % str(order["symbol"]) + " " + str(order["side"]) + " " + str(float(order["executedQty"])) + "/" + str(float(order["origQty"])) + " filled at " + str(order["price"]))


    def add_to_history(self, order):

        if order["symbol"] == val["pair"]:

            self.history_table.insertRow(0)
            self.history_table.setItem(0, 0, QtWidgets.QTableWidgetItem(str(datetime.fromtimestamp(int(str(order["time"])[:-3])).strftime('%d.%m.%y - %H:%M:%S.%f')[:-7])))
            self.history_table.setItem(0, 1, QtWidgets.QTableWidgetItem(order["symbol"]))

            self.history_table.setItem(0, 2, QtWidgets.QTableWidgetItem(order["side"]))


            price = '{number:.{digits}f}'.format(number=float(order["price"]), digits=val["decimals"])
            self.history_table.setItem(0, 3, QtWidgets.QTableWidgetItem(price))

            qty = '{number:.{digits}f}'.format(number=float(order["executedQty"]), digits=val["assetDecimals"]) + " " + val["coin"]
            self.history_table.setItem(0, 4, QtWidgets.QTableWidgetItem(qty))


            # total = '{number:.{digits}f}'.format(number=float(order["price"]) * float(order["executedQty"]), digits=8)

            self.history_table.setItem(0, 5, QtWidgets.QTableWidgetItem('{number:.{digits}f}'.format(number=float(order["price"]) * float(order["executedQty"]), digits=8) + " BTC"))

            if order["side"] == "BUY":
                self.history_table.item(0, 2).setForeground(QtGui.QColor(Colors.color_green))
            else:
                self.history_table.item(0, 2).setForeground(QtGui.QColor(Colors.color_pink))


    def check_add_to_holdings(self, order):
        """Check if the coin has to be added to the holdings table"""
        pair = order["symbol"]
        symbol = pair.replace("BTC", "")
        holdings = list()

        # collect holdings from table
        for i in range(self.holdings_table.rowCount()):
            holdings.append(self.holdings_table.item(i, 1).text())

        # check if the symbol of the order is in the holdings table
        if not any(symbol in s for s in holdings):
            # if not, rebuild holdings table
            build_holdings(self)

    # remove canceled order from open orders table

    def update_open_order(self, order):
        logging.info('ORDER UPDATED! %s' % str(order))

        for i in range(self.open_orders.rowCount()):
            order_id = self.open_orders.item(i, 10).text()
            if str(order_id) == str(order["orderId"]):
                filled_percent = '{number:.{digits}f}'.format(number=(float(order["executedQty"]) / float(order["origQty"]) * 100), digits=2) + "%"

                self.open_orders.setItem(0, 8, QtWidgets.QTableWidgetItem(filled_percent))
                return

        # WIP check (fix)
        print("adde to open orders")
        self.add_to_open_orders(order)

    def orders_received(self, orders):
        """Callback function to draw order history."""
        for _, order in enumerate(orders):
            # if order["symbol"] == val["pair"]:
            if order["status"] == "FILLED":
                self.add_to_history(order)

    def build_open_orders(self, orders):
        """Callback function to draw list of open orders."""
        for _, order in enumerate(orders):
            if order["status"] == "NEW" or order["status"] == "PARTIALLY_FILLED":

                self.add_to_open_orders(order)


            # handle open orders
            # Date	Pair	Type	Side	Price	Amount	Filled%	Total	Trigger Conditions
            # elif order["status"] == "NEW" or  order["status"] == "PARTIALLY_FILLED":

            #     self.add_to_open_orders(order)

            # self.history_table.scrollToTop()
            # self.open_orders.scrollToTop()




    # do stuff once api data has arrived
    def t_complete(self):
        # print("We don now")
        self.limit_buy_input.setValue(float(val["bids"][0][0]))
        self.limit_sell_input.setValue(float(val["asks"][0][0]))
        value = percentage_ammount(val["accHoldings"]["BTC"]["free"], self.limit_buy_input.value(), int(self.buy_slider_label.text().strip("%")), val["assetDecimals"])
        self.limit_buy_amount.setValue(value)


        # print(val["accHoldings"][val["coin"]]["free"])
        sell_percent = str(self.limit_sell_slider.value())

        sell_size = round_sell_amount(sell_percent)

        self.limit_sell_amount.setValue(sell_size)


    # go to trade button
    def gotoTradeButtonClicked(self):

        button_text = self.sender().text()
        coin = button_text.replace("Trade ", "")

        coinIndex = self.coin_selector.findText(coin)
        self.coin_selector.setCurrentIndex(coinIndex)

        self.change_pair()

    def progress_history(self, trade):
        self.tradeTable.insertRow(0)
        price_item = QtWidgets.QTableWidgetItem('{number:.{digits}f}'.format(number=float(trade["price"]), digits=val["decimals"]))
        # price_item.setTextAlignment(QtCore.Qt.AlignHCenter)

        self.tradeTable.setItem(0, 0, price_item)

        qty_item = QtWidgets.QTableWidgetItem('{number:.{digits}f}'.format(number=float(trade["quantity"]), digits=val["assetDecimals"]))
        # qty_item.setTextAlignment(QtCore.Qt.AlignHCenter)
        self.tradeTable.setItem(0, 1, qty_item)

        time_item = QtWidgets.QTableWidgetItem(str(datetime.fromtimestamp(int(str(trade["time"])[:-3])).strftime('%H:%M:%S.%f')[:-7]))
        # time_item.setTextAlignment(QtCore.Qt.AlignHCenter)
        self.tradeTable.setItem(0, 2, time_item)

        if trade["maker"] is True:
            self.tradeTable.item(0, 0).setForeground(QtGui.QColor(Colors.color_pink))

            val["volDirection"] -= float(trade["price"]) * float(trade["quantity"])
        else:
            self.tradeTable.item(0, 0).setForeground(QtGui.QColor(Colors.color_green))
            val["volDirection"] += float(trade["price"]) * float(trade["quantity"])

        self.tradeTable.item(0, 2).setForeground(QtGui.QColor(Colors.color_lightgrey))


        # # set last price, color and arrow
        #
        try:
            if float(self.tradeTable.item(0, 0).text()) > float(self.tradeTable.item(1, 0).text()):
                arrow = QtGui.QPixmap("images/assets/2arrow_up.png")
                color = Colors.color_green
            elif float(self.tradeTable.item(0, 0).text()) == float(self.tradeTable.item(1, 0).text()):
                arrow = QtGui.QPixmap("images/assets/2arrow.png")
                color = Colors.color_yellow
            else:
                arrow = QtGui.QPixmap("images/assets/2arrow_down.png")
                color = Colors.color_pink

            formatted_price = '{number:.{digits}f}'.format(number=float(val["globalList"][0]["price"]), digits=val["decimals"])
            self.price_arrow.setPixmap(arrow)

            self.last_price.setText("<span style='font-size: 20px; font-family: Arial Black; color:" + color + "'>" + formatted_price + "</span>")

            usd_price = '{number:.{digits}f}'.format(number=float(val["globalList"][0]["price"]) * float(val["tickers"]["BTCUSDT"]["lastPrice"]), digits=2)

            self.usd_value.setText("<span style='font-size: 18px; font-family: Arial Black; color: " + Colors.color_yellow + "'>$" + usd_price + "</span>")
        except AttributeError:
            pass

        if self.tradeTable.rowCount() >= 50:
            self.tradeTable.removeRow(50)

    def progress_asks(self, asks):
        for i, _ in enumerate(asks):
            ask_price = '{number:.{digits}f}'.format(number=float(asks[i][0]), digits=val["decimals"])
            ask_quantity = '{number:.{digits}f}'.format(number=float(asks[i][1]), digits=val["assetDecimals"])
            total_btc_asks = '{number:.{digits}f}'.format(number=float(ask_price) * float(ask_quantity), digits=3)

            self.asks_table.setItem(19 - i, 0, QtWidgets.QTableWidgetItem(str(i + 1).zfill(2)))

            self.asks_table.setItem(19 - i, 1, QtWidgets.QTableWidgetItem(ask_price))
            self.asks_table.setItem(19 - i, 2, QtWidgets.QTableWidgetItem(ask_quantity))

            self.asks_table.setItem(19 - i, 3, QtWidgets.QTableWidgetItem(total_btc_asks + " BTC"))
            self.asks_table.item(19 - i, 1).setForeground(QtGui.QColor(Colors.color_pink))

            # self.asks_table.scrollToBottom()

        spread = ((float(val["asks"][0][0]) / float(val["bids"][0][0])) - 1) * 100
        spread_formatted = '{number:.{digits}f}'.format(number=spread, digits=2) + "%"

        self.spread_label.setText("<span style='font-size: 14px; font-family: Arial Black; color:" +
                                  Colors.color_lightgrey + "'>" + spread_formatted + "</span>")

    def progress_bids(self, bids):
        for i, _ in enumerate(bids):
            bid_price = '{number:.{digits}f}'.format(number=float(bids[i][0]), digits=val["decimals"])
            bid_quantity = '{number:.{digits}f}'.format(number=float(bids[i][1]), digits=val["assetDecimals"])
            total_btc_bids = '{number:.{digits}f}'.format(number=float(bid_price) * float(bid_quantity), digits=3)

            self.bids_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(i + 1).zfill(2)))

            self.bids_table.setItem(i, 1, QtWidgets.QTableWidgetItem(bid_price))
            self.bids_table.setItem(i, 2, QtWidgets.QTableWidgetItem(bid_quantity))

            self.bids_table.setItem(i, 3, QtWidgets.QTableWidgetItem(total_btc_bids + " BTC"))
            self.bids_table.item(i, 1).setForeground(QtGui.QColor(Colors.color_green))

    # Draw UI changes (bids, asks, history)
    def progress_fn(self, payload):
        # logging.info("progress FN")

        try:
            asks = payload["asks"]
            if len(asks) == 20:
                for _ in enumerate(asks):
                    self.progress_asks(asks)

        except (TypeError, KeyError):
            pass

        try:
            bids = payload["bids"]
            if len(bids) == 20:
                for _ in enumerate(bids):
                    self.progress_bids(bids)

        except (TypeError, KeyError):
            pass

        try:
            history = payload["history"]
            for trade in enumerate(history):
                self.progress_history(trade[1])

        except (TypeError, KeyError, ValueError):
            pass


    def limit_percentage(self):
        button_number = int(self.sender().objectName()[-1:])

        value = percentage_ammount(val["accHoldings"]["BTC"]["free"], self.limit_buy_input.value(), int(val["buttonPercentage"][button_number]), val["assetDecimals"])

        self.limit_buy_amount.setValue(float(value))

        self.limit_buy_slider.setValue(int(val["buttonPercentage"][button_number]))

    def limit_percentage_sell(self):
        button_number = int(self.sender().objectName()[-1:])
        # value = float(val["accHoldings"][val["coin"]]["free"]) * (float(val["buttonPercentage"][button_number]) / 100)

        # print(val["accHoldings"][val["coin"]]["free"])
        # self.limit_sell_amount.setValue(value)

        self.limit_sell_slider.setValue(int(val["buttonPercentage"][button_number]))


    def calc_total_buy(self):
        try:
            total = float(self.limit_buy_input.value()) * float(self.limit_buy_amount.text())
            total_formatted = '{number:.{digits}f}'.format(number=total, digits=8)

            self.limit_buy_total.setText(str(total_formatted) + " BTC")
        except ValueError:
            pass


    def calc_total_sell(self):
        try:
            total = float(self.limit_sell_input.value()) * float(self.limit_sell_amount.text())
            total_formatted = '{number:.{digits}f}'.format(number=total, digits=8)
            self.limit_sell_total.setText(str(total_formatted) + " BTC")
        except ValueError:
            pass


    def buy_slider(self):
        buy_percent_val = str(self.limit_buy_slider.value())
        self.buy_slider_label.setText(buy_percent_val + "%")

        buy_value = percentage_ammount(val["accHoldings"]["BTC"]["free"], self.limit_buy_input.value(), int(buy_percent_val), val["assetDecimals"])
        self.limit_buy_amount.setValue(float(buy_value))
        order_cost = float(buy_value) * float(self.limit_buy_input.value())
        self.limit_buy_total.setText('{number:.{digits}f}'.format(number=order_cost, digits=8) + " BTC")

        # if order_cost < 0.002:
        #     self.limit_buy_button.setStyleSheet("border: 2px solid #bf4a3d;")
        # else:
        #     self.limit_buy_button.setStyleSheet("border: 2px solid #151a1e;")

    def sell_slider(self):
        # Text to value
        print("ich slide")
        # print(val["accHoldings"][val["coin"]]["free"])
        sell_percent = str(self.limit_sell_slider.value())

        sell_size = round_sell_amount(sell_percent)

        self.limit_sell_amount.setValue(sell_size)


        self.sell_slider_label.setText(sell_percent + "%")


    ####################################
    #           VALIDATATION
    ####################################

    def check_sell_ammount(self):
        # total = float(self.limit_sell_amount.text()) *

        try:
            sell_amount = float(self.limit_sell_amount.text())
            free_amount = float(val["accHoldings"][val["coin"]]["free"])
            sell_price = float(self.limit_sell_input.text())

            if sell_amount > free_amount or sell_amount * sell_price < 0.001:
                self.limit_sell_button.setStyleSheet("border: 2px solid transparent; background: #ff077a; color: #f3f3f3;")
                self.limit_sell_button.setCursor(QtGui.QCursor(QtCore.Qt.ForbiddenCursor))
                val["sellAllowed"] = False
            else:
                self.limit_sell_button.setStyleSheet("border: 2px solid transparent;")
                self.limit_sell_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                val["sellAllowed"] = True

        except ValueError:
            print("val error")
            # pass
        self.calc_total_sell()

    def check_buy_amount(self):
        total = int(((float(self.limit_buy_amount.value()) * float(self.limit_buy_input.value())) / float(val["accHoldings"]["BTC"]["free"])) * 100)
        # print("check buy")
        self.calc_total_buy()

        try:
            total = float(self.limit_buy_input.value()) * float(self.limit_buy_amount.text())

            if total > float(val["accHoldings"]["BTC"]["free"]) or total < 0.001:
                self.limit_buy_button.setStyleSheet("border: 2px solid transparent; background: #70a800; color: #f3f3f3;")
                self.limit_buy_button.setCursor(QtGui.QCursor(QtCore.Qt.ForbiddenCursor))
                val["buyAllowed"] = False

            else:
                self.limit_buy_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                self.limit_buy_button.setStyleSheet("border: 2px solid transparent;")
                val["buyAllowed"] = True

        except ValueError as error:
            print(str(error))




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

        worker.signals.progress.connect(self.progress_fn)

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
                worker = Worker(partial(self.get_kline, str(i)))
                worker.signals.progress.connect(self.klines_received)
                self.threadpool.tryStart(worker)

            time.sleep(longSleep)



        # worker = Worker(partial(get_kline, self, ))
    def get_kline(self, pair, progress_callback):
        """Make an API call to get historical data of a coin pair."""
        interval = "1m"

        klines = client.get_klines(symbol=pair, interval=interval)

        progress_callback.emit([klines, pair, interval])
        val["apiCalls"] += 1


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
    def get_all_orders(self):
        orders = client.get_open_orders()
        # print(str(orders))
        for _, order in enumerate(orders):
            print(str(order))
            self.kline_table.insertRow(0)
            self.kline_table.setItem(0, 0, QtWidgets.QTableWidgetItem(order["symbol"]))
            self.kline_table.setItem(0, 1, QtWidgets.QTableWidgetItem(order["price"]))
            self.kline_table.setItem(0, 2, QtWidgets.QTableWidgetItem(order["origQty"]))
            self.kline_table.setItem(0, 3, QtWidgets.QTableWidgetItem(order["executedQty"]))


    def api_calls(self):
        worker = Worker(api_history)
        worker.signals.progress.connect(self.progress_fn)
        self.threadpool.start(worker)

        worker = Worker(api_depth)
        worker.signals.progress.connect(self.progress_fn)
        worker.signals.finished.connect(self.t_complete)
        self.threadpool.start(worker)

        worker = Worker(api_order_history)
        worker.signals.progress.connect(self.orders_received)
        self.threadpool.start(worker)


    # cancel an order from a separate thread
    def cancel_order_byId(self, order_id, symbol):

        worker = Worker(partial(api_cancel_order, order_id, symbol))
        # worker.signals.progress.connect(self.cancel_callback)
        self.threadpool.start(worker)




    def create_buy_order(self):
        if val["buyAllowed"] is True:
            pair = val["pair"]
            price = '{number:.{digits}f}'.format(number=self.limit_buy_input.value(), digits=val["decimals"])

            amount = '{number:.{digits}f}'.format(number=self.limit_buy_amount.value(), digits=val["assetDecimals"])
            side = "Buy"

            worker = Worker(partial(api_create_order, side, pair, price, amount))
            # worker.signals.progress.connect(self.create_order_callback)
            self.threadpool.start(worker)
            logging.info('[ + ] BUY ORDER CREATED! %s' % str(pair) + " " + str(amount) + " at " + str(price))


    def create_sell_order(self):
        if val["sellAllowed"] is True:
            pair = val["pair"]
            price = '{number:.{digits}f}'.format(number=self.limit_sell_input.value(), digits=val["decimals"])

            amount = '{number:.{digits}f}'.format(number=self.limit_sell_amount.value(), digits=val["assetDecimals"])

            side = "Sell"

            worker = Worker(partial(api_create_order, side, pair, price, amount))
            # worker.signals.progress.connect(self.create_order_callback)
            self.threadpool.start(worker)
            logging.info('[ - ] SELL ORDER CREATED! %s' % str(pair) + " " + str(amount) + " at " + str(price))





    def check_for_update(self, progress_callback):
        current_height = self.frameGeometry().height()
        while True:
            # print("check")
            # try:

            if current_height > self.frameGeometry().height():
                progress_callback.emit(15)


            # except (KeyError, UnboundLocalError):
            #     pass

            current_height = self.frameGeometry().height()

            progress_callback.emit(1)

            time.sleep(1)



    def start_sockets(self, progress_callback):

        val["bm"] = BinanceSocketManager(client)

        self.websockets_symbol()

        # start user websocket separately since it does not need to be restarted
        val["userWebsocket"] = val["bm"].start_user_socket(partial(userCallback, self))

        val["tickerWebsocket"] = val["bm"].start_ticker_socket(partial(tickerCallback, self))


        val["bm"].start()

    def websockets_symbol(self):
        val["aggtradeWebsocket"] = val["bm"].start_aggtrade_socket(val["pair"], partial(directCallback, self))

        val["depthWebsocket"] = val["bm"].start_depth_socket(val["pair"], partial(depthCallback, self), depth=20)

        val["klineWebsocket"] = val["bm"].start_kline_socket(val["pair"], partial(klineCallback, self))
        # logging.info('Starting websockets for %s' % str(val["pair"]))



    def write_config(self):
        key = self.api_key.text()
        secret = self.api_secret.text()
        defaultPair = self.default_pair.text()
        # defaultTimeframe = self.default_timeframe.text()

        raw_timeframes = [1, 3, 5, 15, 30, 45, 60, 120, 180, 240, 1440, "1w"]

        dtf = self.dtf_selector.currentText()
        for i, tf in enumerate(val["validTimeframes"]):
            if str(dtf) == str(tf):
                # self.dtf_selector.setCurrentIndex(i)
                tf_index = i

        copy_price = self.copy_price_box.isChecked()
        copy_qty = self.copy_qty_box.isChecked()
        print("checkbox state:" + str(copy_price) + " " + str(copy_qty))

        percent_texts = [self.percent_1, self.percent_2, self.percent_3, self.percent_4, self.percent_5]
        percent = val["buttonPercentage"]

        for i, _ in enumerate(percent):

            try:
                if float(percent_texts[i].text()) >= 0 and float(percent_texts[i].text()) <= 100:
                    percent[i] = percent_texts[i].text()
                    percent_texts[i].setStyleSheet("color: #f3f3f3;")
                else:
                    percent_texts[i].setStyleSheet("color: #ff077a;")
            except ValueError:
                percent_texts[i].setStyleSheet("color: #ff077a;")

        config = configparser.ConfigParser()

        if key != val["api_key"] or secret != val["api_secret"]:
            self.restart_warning.setStyleSheet("color: red;")

        print("saving config...")

        config['CONFIG'] = {'DefaultPair': defaultPair,
                            'ButtonPercentages': percent[0] + ", " + percent[1] + ", " + percent[2] + ", " + percent[3] + ", " + percent[4],
                            'DefaultTimeframe': raw_timeframes[tf_index],
                            'CopyPrice': copy_price,
                            'CopyQuantity': copy_qty,
                            }
        config["API"] = {"Key": key, "Secret": secret}

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        read_config()
        self.set_button_text()
        logging.info("Saving config.")

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

    def holding_updated(self):
        print("holding updated")
        self.limit_total_btc.setText(str(val["accHoldings"]["BTC"]["free"]) + " BTC")
        self.limit_total_coin.setText(str(val["accHoldings"][val["coin"]]["free"]) + " " + val["coin"])

        bold_font = QtGui.QFont()
        bold_font.setBold(True)

        for i in range(self.holdings_table.rowCount()):
            try:
                coin = self.holdings_table.item(i, 1).text()
                free = val["accHoldings"][coin]["free"]
                locked = val["accHoldings"][coin]["locked"]
                total = '{number:.{digits}f}'.format(number=float(free) + float(locked), digits=8)

                if coin != "BTC":
                    price = val["coins"][coin + "BTC"]["close"]
                    # print("wavg: " + str(wAvg))
                elif coin == "BTC":
                    price = 1

                total_btc = float(total) * float(price)
                total_btc_formatted = '{number:.{digits}f}'.format(number=total_btc, digits=8)

                self.holdings_table.setItem(i, 3, QtWidgets.QTableWidgetItem("{0:.8f}".format(float(total))))
                self.holdings_table.setItem(i, 4, QtWidgets.QTableWidgetItem("{0:g}".format(float(free))))
                self.holdings_table.setItem(i, 5, QtWidgets.QTableWidgetItem("{0:g}".format(float(locked))))
                self.holdings_table.setItem(i, 6, QtWidgets.QTableWidgetItem(total_btc_formatted))
                self.holdings_table.item(i, 6).setFont(bold_font)
                self.holdings_table.item(i, 6).setForeground(QtGui.QColor(Colors.color_lightgrey))


                if float(total) * float(price) < 0.001 and coin != "BTC":
                    self.holdings_table.removeRow(i)




            except AttributeError:
                print("attr error: " + str(i))

        self.check_buy_amount()
        self.check_sell_ammount()


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


####################################################################


def api_create_order(side, pair, price, amount, progress_callback):
    print("create order: " + str(price) + " " + str(amount))
    try:
        if side == "Buy":
            order = client.order_limit_buy(
                symbol=pair,
                quantity=str(amount),
                price=str(price))


        elif side == "Sell":
            order = client.order_limit_sell(
                symbol=pair,
                quantity=str(amount),
                price=str(price))
        return order
    except BinanceAPIException:
        print("create order failed")


def api_cancel_order(order_id, symbol, progress_callback):
    print("cancel order " + str(symbol) + " " + str(order_id))
    try:
        client.cancel_order(symbol=symbol, orderId=order_id)
    except BinanceAPIException:
        print("cancel failed")


def round_sell_amount(percent_val):
    holding = float(val["accHoldings"][val["coin"]]["free"]) * (float(percent_val) / 100)
    if val["coins"][val["pair"]]["minTrade"] == 1:
        sizeRounded = int(holding)
    else:
        sizeRounded = int(holding * 10**val["assetDecimals"]) / 10.0**val["assetDecimals"]
    return sizeRounded


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
