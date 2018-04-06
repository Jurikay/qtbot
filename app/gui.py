# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Main gui class."""


import configparser
import time
from datetime import datetime, timedelta
from functools import partial

from binance.websockets import BinanceSocketManager
from PyQt5.QtCore import QSize, Qt, QThreadPool, QTimer, QUrl
from PyQt5.QtGui import QColor, QCursor, QIcon, QPixmap, QFont
from PyQt5.QtMultimedia import QSoundEffect, QMediaPlayer, QMediaContent, QSound
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt5.uic import loadUi

from app.apiFunctions import percentage_ammount
from app.callbacks import (Worker, api_depth, api_history, api_order_history,
                           depthCallback, directCallback, tickerCallback,
                           userCallback)
from app.charts import welcome_page
from app.colors import colors
from app.gui_functions import (build_coinindex, build_holdings, calc_total_btc,
                               calc_wavg, filter_coinindex, initial_values,
                               update_holding_prices)
from app.init import val
from app.initApi import (BinanceAPIException, client, read_config,
                         set_pair_values)


class beeserBot(QMainWindow):

    """Main ui class."""

    def __init__(self):
        """Init method."""
        super(beeserBot, self).__init__()
        loadUi("ui/MainWindow.ui", self)

        # set external stylesheet
        with open("ui/style.qss", "r") as fh:
            self.setStyleSheet(fh.read())

        self.setWindowTitle("Juris beeser Bot")
        self.restart_warning.setStyleSheet("color: transparent;")
        # self.spread_area.setStyleSheet("background: #2e363d;")

        self.holdings_table.setStyleSheet("alternate-background-color: #2e363d;")

        self.counter = 0
        self.counter2 = 0

        # THREADING
        self.threadpool = QThreadPool()
        print("Multithreading with a maximum of %d threads" % self.threadpool.maxThreadCount())

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

        # self.player = QMediaPlayer()
        # sound = QMediaContent(QUrl.fromLocalFile("sounds/Tink.wav"))
        # self.player.setMedia(sound)
        # self.player.setVolume(1)

        self.limit_buy_button.clicked.connect(self.create_buy_order)
        self.limit_sell_button.clicked.connect(self.create_sell_order)

        self.button_wavg.clicked.connect(calc_wavg)

        self.coinindex_filter.textChanged.connect(partial(filter_coinindex, self))

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
            self.chart.setHtml(welcome_page())
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

            icon = QIcon("images/ico/" + coin[:-3] + ".svg")

            self.coin_selector.addItem(icon, coin[:-3])

        self.coin_selector.model().sort(0)
        self.coin_selector.setIconSize(QSize(25, 25))

        coinIndex = self.coin_selector.findText(val["coin"])
        self.coin_selector.setCurrentIndex(coinIndex)

        initial_values(self)

        self.schedule_websockets()
        self.schedule_work()

        build_holdings(self)

        build_coinindex(self)

        self.sound_1 = QSound('sounds/Tink.wav')

        self.timer = QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.delayed_stuff)
        self.timer.start()


    def delayed_stuff(self):

        print("delayed")

        self.asks_table.setColumnWidth(1, 75)
        self.bids_table.setColumnWidth(1, 75)
        self.tradeTable.setColumnWidth(1, 75)

        self.open_orders.setColumnWidth(0, 130)
        self.open_orders.setColumnWidth(7, 120)
        self.open_orders.setColumnWidth(10, 0)

        self.history_table.setColumnWidth(0, 130)
        self.history_table.setColumnWidth(2, 60)
        self.history_table.setColumnWidth(5, 120)
        self.holdings_table.setColumnWidth(0, 150)

        self.holdings_table.setColumnWidth(1, 75)
        self.holdings_table.setColumnWidth(7, 120)

        # self.check_buy_amount()
        # self.check_sell_ammount()

        # val["sound_1"] = QSoundEffect()
        # val["sound_1"].setSource(QUrl.fromLocalFile("sounds/Tink.wav"))
        # val["sound_1"].setVolume(1)
        print("scroll")

        self.asks_table.scrollToBottom()

        self.timer.stop()


    def change_pair(self):

        newcoin = self.coin_selector.currentText()

        if any(newcoin + "BTC" in s for s in val["coins"]) and newcoin != val["coin"]:
            val["pair"] = newcoin + "BTC"
            val["bm"].stop_socket(val["aggtradeWebsocket"])
            val["bm"].stop_socket(val["depthWebsocket"])

            set_pair_values()
            initial_values(self)

            self.websockets()

            self.history_table.setRowCount(0)
            self.open_orders.setRowCount(0)
            val["history"] = dict()


            self.api_calls()




    def open_orders_cell_clicked(self, row, column):
        if column == 9:

            order_id = str(self.open_orders.item(row, 8).text())
            pair = str(self.open_orders.item(row, 1).text())

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

    def tick(self, payload):
        if payload == 1:
            self.session_running.setText(str(timedelta(seconds=val["timeRunning"])))
            val["timeRunning"] += 1

            total_btc_value = calc_total_btc()
            self.total_btc_label.setText("<span style='font-size: 14px; color: #f3ba2e; font-family: Arial Black;'>" + total_btc_value + "</span>")

            total_usd_value = '{number:,.{digits}f}'.format(number=float(total_btc_value.replace(" BTC", "")) * float(val["tickers"]["BTCUSDT"]["lastPrice"]), digits=2) + "$"

            self.total_usd_label.setText(total_usd_value)

            self.btc_price_label.setText('{number:,.{digits}f}'.format(number=float(val["tickers"]["BTCUSDT"]["lastPrice"]), digits=2) + "$")

            operator = ""
            percent_change = float(val["tickers"]["BTCUSDT"]["priceChangePercent"])
            if percent_change > 0:
                operator = "+"

            btc_percent = operator + '{number:,.{digits}f}'.format(number=percent_change, digits=2) + "%"

            self.btc_percent_label.setText(btc_percent)

            update_holding_prices(self)
        elif payload == 15:
            self.asks_table.scrollToBottom()

    def play_sound_effect(self):
        # self.sound_1.play()
        print("playung sound")

    def add_to_open_orders(self, order):

        # play a sound file to indicate a new order
        # print("play sound")

        # val["sound_1"].play()
        # QSoundEffect.play("sounds/Tink.mp3")

        # only add to open orders table if the coin is currently selected.
        if order["symbol"] == val["pair"]:
            self.open_orders.insertRow(0)
            self.open_orders.setItem(0, 0, QTableWidgetItem(str(datetime.fromtimestamp(int(str(order["time"])[:-3])).strftime('%d.%m.%y - %H:%M:%S.%f')[:-7])))
            self.open_orders.setItem(0, 1, QTableWidgetItem(order["symbol"]))
            self.open_orders.setItem(0, 2, QTableWidgetItem(order["type"]))
            self.open_orders.setItem(0, 3, QTableWidgetItem(order["side"]))
            price = '{number:.{digits}f}'.format(number=float(order["price"]), digits=val["decimals"])
            self.open_orders.setItem(0, 4, QTableWidgetItem(price))
            qty = '{number:.{digits}f}'.format(number=float(order["origQty"]), digits=val["assetDecimals"]) + " " + val["coin"]
            self.open_orders.setItem(0, 5, QTableWidgetItem(qty))

            filled_percent = '{number:.{digits}f}'.format(number=float(order["executedQty"]) / float(order["origQty"]), digits=2) + "%"

            self.open_orders.setItem(0, 6, QTableWidgetItem(filled_percent))

            total_btc = '{number:.{digits}f}'.format(number=float(order["origQty"]) * float(order["price"]), digits=8) + " BTC"


            self.open_orders.setItem(0, 7, QTableWidgetItem(total_btc))

            self.open_orders.setItem(0, 8, QTableWidgetItem(str(order["orderId"])))

            self.open_orders.setItem(0, 9, QTableWidgetItem("cancel"))

            self.open_orders.item(0, 9).setForeground(QColor(colors.color_yellow))

            if order["side"] == "BUY":
                self.open_orders.item(0, 3).setForeground(QColor(colors.color_green))
            else:
                self.open_orders.item(0, 3).setForeground(QColor(colors.color_pink))


    def remove_from_open_orders(self, order):
        if order["symbol"] == val["pair"]:
            for row in range(self.open_orders.rowCount()):
                try:
                    if str(self.open_orders.item(row, 8).text()) == str(order["orderId"]):

                        self.open_orders.removeRow(row)

                except (AttributeError, TypeError):
                    pass

    def add_to_history(self, order):
        if order["symbol"] == val["pair"]:

            self.history_table.insertRow(0)
            self.history_table.setItem(0, 0, QTableWidgetItem(str(datetime.fromtimestamp(int(str(order["time"])[:-3])).strftime('%d.%m.%y - %H:%M:%S.%f')[:-7])))
            self.history_table.setItem(0, 1, QTableWidgetItem(order["symbol"]))

            self.history_table.setItem(0, 2, QTableWidgetItem(order["side"]))


            price = '{number:.{digits}f}'.format(number=float(order["price"]), digits=val["decimals"])
            self.history_table.setItem(0, 3, QTableWidgetItem(price))

            qty = '{number:.{digits}f}'.format(number=float(order["executedQty"]), digits=val["assetDecimals"]) + " " + val["coin"]
            self.history_table.setItem(0, 4, QTableWidgetItem(qty))


            # total = '{number:.{digits}f}'.format(number=float(order["price"]) * float(order["executedQty"]), digits=8)

            self.history_table.setItem(0, 5, QTableWidgetItem('{number:.{digits}f}'.format(number=float(order["price"]) * float(order["executedQty"]), digits=8) + " BTC"))

            if order["side"] == "BUY":
                self.history_table.item(0, 2).setForeground(QColor(colors.color_green))
            else:
                self.history_table.item(0, 2).setForeground(QColor(colors.color_pink))


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
        for i in range(self.open_orders.rowCount()):
            order_id = self.open_orders.item(i, 8).text()
            if str(order_id) == str(order["orderId"]):
                filled_percent = '{number:.{digits}f}'.format(number=float(order["executedQty"]) / float(order["origQty"]), digits=2) + "%"

                self.open_orders.setItem(0, 6, QTableWidgetItem(filled_percent))


    def orders_received(self, orders):
        """Callback function to draw order history."""
        for _, order in enumerate(orders):
            if order["symbol"] == val["pair"]:
                if order["status"] == "FILLED" or order["status"] == "PARTIALLY_FILLED":
                    self.add_to_history(order)

                # handle open orders
                # Date	Pair	Type	Side	Price	Amount	Filled%	Total	Trigger Conditions
                elif order["status"] == "NEW":

                    self.add_to_open_orders(order)

            # self.history_table.scrollToTop()
            # self.open_orders.scrollToTop()




    # do stuff once api data has arrived
    def t_complete(self):
        # print("We don now")
        self.limit_buy_input.setValue(float(val["bids"][0][0]))
        self.limit_sell_input.setValue(float(val["asks"][0][0]))
        value = percentage_ammount(val["accHoldings"]["BTC"]["free"], self.limit_buy_input.value(), int(self.buy_slider_label.text().strip("%")), val["assetDecimals"])
        print("value: " + str(value))
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
        self.tradeTable.setItem(0, 0, QTableWidgetItem('{number:.{digits}f}'.format(number=float(trade["price"]), digits=val["decimals"])))
        self.tradeTable.setItem(0, 1, QTableWidgetItem('{number:.{digits}f}'.format(number=float(trade["quantity"]), digits=val["assetDecimals"])))
        self.tradeTable.setItem(0, 2, QTableWidgetItem(str(datetime.fromtimestamp(int(str(trade["time"])[:-3])).strftime('%H:%M:%S.%f')[:-7])))
        if trade["maker"] is True:
            self.tradeTable.item(0, 0).setForeground(QColor(colors.color_pink))
        else:
            self.tradeTable.item(0, 0).setForeground(QColor(colors.color_green))

        self.tradeTable.item(0, 2).setForeground(QColor(colors.color_lightgrey))


        self.tradeTable.removeRow(50)
        # # set last price, color and arrow
        #
        try:
            if float(self.tradeTable.item(0, 0).text()) > float(self.tradeTable.item(1, 0).text()):
                arrow = QPixmap("images/assets/2arrow_up.png")
                color = colors.color_green
            elif float(self.tradeTable.item(0, 0).text()) == float(self.tradeTable.item(1, 0).text()):
                arrow = QPixmap("images/assets/2arrow.png")
                color = colors.color_yellow
            else:
                arrow = QPixmap("images/assets/2arrow_down.png")
                color = colors.color_pink

            formatted_price = '{number:.{digits}f}'.format(number=float(val["globalList"][0]["price"]), digits=val["decimals"])
            self.price_arrow.setPixmap(arrow)

            self.last_price.setText("<span style='font-size: 20px; font-family: Arial Black; color:" + color + "'>" + formatted_price + "</span>")

            usd_price = '{number:.{digits}f}'.format(number=float(val["globalList"][0]["price"]) * float(val["tickers"]["BTCUSDT"]["lastPrice"]), digits=2)

            self.usd_value.setText("<span style='font-size: 18px; font-family: Arial Black; color: " + colors.color_yellow + "'>$" + usd_price + "</span>")
        except AttributeError:
            pass


    def progress_asks(self, asks):
        for i, _ in enumerate(asks):
            ask_price = '{number:.{digits}f}'.format(number=float(asks[i][0]), digits=val["decimals"])
            ask_quantity = '{number:.{digits}f}'.format(number=float(asks[i][1]), digits=val["assetDecimals"])
            total_btc_asks = '{number:.{digits}f}'.format(number=float(ask_price) * float(ask_quantity), digits=3)

            self.asks_table.setItem(19 - i, 0, QTableWidgetItem(str(i + 1).zfill(2)))

            self.asks_table.setItem(19 - i, 1, QTableWidgetItem(ask_price))
            self.asks_table.setItem(19 - i, 2, QTableWidgetItem(ask_quantity))

            self.asks_table.setItem(19 - i, 3, QTableWidgetItem(total_btc_asks + " BTC"))
            self.asks_table.item(19 - i, 1).setForeground(QColor(colors.color_pink))

            # self.asks_table.scrollToBottom()

        spread = ((float(val["asks"][0][0]) / float(val["bids"][0][0])) - 1) * 100
        spread_formatted = '{number:.{digits}f}'.format(number=spread, digits=2) + "%"

        self.spread_label.setText("<span style='font-size: 14px; font-family: Arial Black; color:" +
                                  colors.color_lightgrey + "'>" + spread_formatted + "</span>")

    def progress_bids(self, bids):
        for i, _ in enumerate(bids):
            bid_price = '{number:.{digits}f}'.format(number=float(bids[i][0]), digits=val["decimals"])
            bid_quantity = '{number:.{digits}f}'.format(number=float(bids[i][1]), digits=val["assetDecimals"])
            total_btc_bids = '{number:.{digits}f}'.format(number=float(bid_price) * float(bid_quantity), digits=3)

            self.bids_table.setItem(i, 0, QTableWidgetItem(str(i + 1).zfill(2)))

            self.bids_table.setItem(i, 1, QTableWidgetItem(bid_price))
            self.bids_table.setItem(i, 2, QTableWidgetItem(bid_quantity))

            self.bids_table.setItem(i, 3, QTableWidgetItem(total_btc_bids + " BTC"))
            self.bids_table.item(i, 1).setForeground(QColor(colors.color_green))

    # Draw UI changes
    def progress_fn(self, payload):
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
                self.limit_sell_button.setCursor(QCursor(Qt.ForbiddenCursor))
                val["sellAllowed"] = False
            else:
                self.limit_sell_button.setStyleSheet("border: 2px solid transparent;")
                self.limit_sell_button.setCursor(QCursor(Qt.PointingHandCursor))
                val["sellAllowed"] = True

        except ValueError:
            print("val error")
            # pass
        self.calc_total_sell()

    def check_buy_amount(self):
        total = int(((float(self.limit_buy_amount.value()) * float(self.limit_buy_input.value())) / float(val["accHoldings"]["BTC"]["free"])) * 100)
        print("check buy")
        self.calc_total_buy()

        try:
            total = float(self.limit_buy_input.value()) * float(self.limit_buy_amount.text())

            if total > float(val["accHoldings"]["BTC"]["free"]) or total < 0.001:
                self.limit_buy_button.setStyleSheet("border: 2px solid transparent; background: #70a800; color: #f3f3f3;")
                self.limit_buy_button.setCursor(QCursor(Qt.ForbiddenCursor))
                val["buyAllowed"] = False

            else:
                self.limit_buy_button.setCursor(QCursor(Qt.PointingHandCursor))
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

    def create_sell_order(self):
        if val["sellAllowed"] is True:
            pair = val["pair"]
            price = '{number:.{digits}f}'.format(number=self.limit_sell_input.value(), digits=val["decimals"])

            amount = '{number:.{digits}f}'.format(number=self.limit_sell_amount.value(), digits=val["assetDecimals"])

            side = "Sell"

            worker = Worker(partial(api_create_order, side, pair, price, amount))
            # worker.signals.progress.connect(self.create_order_callback)
            self.threadpool.start(worker)





    def check_for_update(self, progress_callback):
        current_height = self.frameGeometry().height()
        while True:
            # print("check")
            try:

                if current_height != self.frameGeometry().height():
                    progress_callback.emit(15)


            except (KeyError, UnboundLocalError):
                pass

            current_height = self.frameGeometry().height()

            progress_callback.emit(1)

            time.sleep(1)



    def start_sockets(self, progress_callback):

        val["bm"] = BinanceSocketManager(client)

        self.websockets()

        # start user websocket separately since it does not need to be restarted
        val["userWebsocket"] = val["bm"].start_user_socket(partial(userCallback, self))

        val["tickerWebsocket"] = val["bm"].start_ticker_socket(partial(tickerCallback, self))


        val["bm"].start()

    def websockets(self):
        val["aggtradeWebsocket"] = val["bm"].start_aggtrade_socket(val["pair"], partial(directCallback, self))

        val["depthWebsocket"] = val["bm"].start_depth_socket(val["pair"], partial(depthCallback, self), depth=20)



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

    def holding_updated(self):
        print("holding updated")
        self.limit_total_btc.setText(str(val["accHoldings"]["BTC"]["free"]) + " BTC")
        self.limit_total_coin.setText(str(val["accHoldings"][val["coin"]]["free"]) + " " + val["coin"])

        bold_font = QFont()
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

                self.holdings_table.setItem(i, 3, QTableWidgetItem("{0:g}".format(float(total))))
                self.holdings_table.setItem(i, 4, QTableWidgetItem("{0:g}".format(float(free))))
                self.holdings_table.setItem(i, 5, QTableWidgetItem("{0:g}".format(float(locked))))
                self.holdings_table.setItem(i, 6, QTableWidgetItem(total_btc_formatted))
                self.holdings_table.item(i, 6).setFont(bold_font)
                self.holdings_table.item(i, 6).setForeground(QColor(colors.color_lightgrey))


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
