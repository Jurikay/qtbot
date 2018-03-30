import sys
import traceback
import time
import configparser
from functools import partial
from datetime import datetime
from PyQt5.QtCore import pyqtSlot, QThreadPool, QTimer, QObject, QRunnable, pyqtSignal, QSize, Qt
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QMainWindow, QListWidgetItem, QScrollBar, QTableWidgetItem, QStyleFactory, QHeaderView, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QColor, QPalette, QIcon, QStandardItem, QPixmap, QFont, QFontDatabase, QCursor
from PyQt5.uic import loadUi

from init import val
from initApi import *
from charts import build_chart, build_chart2, welcome_page

color_pink = "#ff007a"
color_yellow = "#f3ba2e"
color_green = "#94c940"
color_lightgrey = "#cdcdcd"
color_grey = "#999"


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(object)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handle worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class beeserBot(QMainWindow):

    """Main ui class."""

    def __init__(self):
        """Init method."""
        super(beeserBot, self).__init__()
        loadUi("ui/BeeserBotFull.ui", self)


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
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())



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
        self.limit_buy_amount.valueChanged.connect(self.check_buy_ammount)


        self.limit_buy_button.clicked.connect(self.create_buy_order)
        self.limit_sell_button.clicked.connect(self.create_sell_order)


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

            self.default_timeframe.setText(str(val["defaultTimeframe"]))

        except (TypeError, KeyError):
            pass





        # check if coin is an empty dict. If yes, api calls have not been answered.
        if val["coin"] != dict():
            print("authenticated!")

            self.inizialize()

        # api credentials not valid; display welcome page
        else:
            self.chart.setHtml(welcome_page())
            self.chart.show()
            self.bot_tabs.setCurrentIndex(4)

            self.api_key.setStyleSheet("border: 2px solid #f3ba2e;")
            self.api_secret.setStyleSheet("border: 2px solid #f3ba2e;")


        for i in range(20):
            self.bids_table.insertRow(0)
            self.asks_table.insertRow(0)
            self.new_table.insertRow(0)


        for i in range(50):
            self.tradeTable.insertRow(0)
    def inizialize(self):


        self.api_calls()

        for coin in val["coins"]:

            icon = QIcon("ico/" + coin[:-3] + ".svg")

            self.coin_selector.addItem(icon, coin[:-3])

        self.coin_selector.model().sort(0)
        self.coin_selector.setIconSize(QSize(25, 25))




        coinIndex = self.coin_selector.findText(val["coin"])


        self.coin_selector.setCurrentIndex(coinIndex)


        initial_values(self)


        self.schedule_websockets()
        self.schedule_work()

        build_holdings(self)


        self.timer = QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.delayed_stuff)
        self.timer.start()

    def delayed_stuff(self):
        self.asks_table.scrollToBottom()
        print("delayed")

        self.asks_table.setColumnWidth(1, 75)
        self.bids_table.setColumnWidth(1, 75)
        self.tradeTable.setColumnWidth(1, 75)

        self.open_orders.setColumnWidth(0, 150)
        self.open_orders.setColumnWidth(7, 120)
        self.history_table.setColumnWidth(0, 150)
        self.history_table.setColumnWidth(5, 120)
        self.holdings_table.setColumnWidth(0, 150)

        self.holdings_table.setColumnWidth(1, 75)
        self.holdings_table.setColumnWidth(7, 120)

        total_btc_value = self.total_btc()

        self.total_btc_label.setText("<span style='font-size: 14px; color: #f3ba2e; font-family: Arial Black;'>" + total_btc_value + "</span>")

        total_usd_value = '{number:,.{digits}f}'.format(number=float(total_btc_value.replace(" BTC", "")) * float(val["tether"]["lastPrice"]), digits=2) + "$"




        self.total_usd_label.setText(total_usd_value)

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


            self.api_calls()




    def open_orders_cell_clicked(self, row, column):
        if column == 9:

            id = str(self.open_orders.item(row, 8).text())
            pair = str(self.open_orders.item(row, 1).text())

            # cancel = (cancel_order(client, id, pair))

            self.cancel_order_byId(id, pair)

            # if str(cancel["orderId"]) == str(id):
            #     self.open_orders.removeRow(row)


    def cell_was_clicked(self, row, column):

        try:
            self.limit_buy_input.setValue(float(val["globalList"][row]["price"]))
            self.limit_sell_input.setValue(float(val["globalList"][row]["price"]))
            value = percentage_ammount(val["accHoldings"]["BTC"]["free"], self.limit_buy_input.value(), int(self.buy_slider_label.text().strip("%")), val["assetDecimals"])
            # self.limit_buy_amount.setValue(value)
        except IndexError:
            pass

    def bids_cell_clicked(self, row, column):
        self.limit_buy_input.setValue(float(val["bids"][row][0]))
        self.limit_sell_input.setValue(float(val["bids"][row][0]))
        value = percentage_ammount(val["accHoldings"]["BTC"]["free"], self.limit_buy_input.value(), int(self.buy_slider_label.text().strip("%")), val["assetDecimals"])
        # self.limit_buy_amount.setValue(value)



    def asks_cell_clicked(self, row, column):
        self.limit_buy_input.setValue(float(val["asks"][19-row][0]))
        self.limit_sell_input.setValue(float(val["asks"][19-row][0]))
        value = percentage_ammount(val["accHoldings"]["BTC"]["free"], self.limit_buy_input.value(), int(self.buy_slider_label.text().strip("%")), val["assetDecimals"])
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



    def print_output(self, s):
        # print(s["lastPrice"])
        print(s)


    # callback function to draw order history
    def orders_finished(self, payload):


        for i, order in enumerate(payload["orders"]):
            # print(order)
            if order["symbol"] == val["pair"]:
                if order["status"] == "FILLED":
                    color = color_grey


                    self.history_table.insertRow(0)
                    self.history_table.setItem(0, 0, QTableWidgetItem(str(datetime.fromtimestamp(int(str(order["time"])[:-3])).strftime('%d.%m.%y - %H:%M:%S.%f')[:-7])))
                    self.history_table.setItem(0, 1, QTableWidgetItem(order["symbol"]))

                    self.history_table.setItem(0, 2, QTableWidgetItem(order["side"]))


                    price = '{number:.{digits}f}'.format(number=float(order["price"]), digits=val["decimals"])
                    self.history_table.setItem(0, 3, QTableWidgetItem(price))

                    qty = '{number:.{digits}f}'.format(number=float(order["executedQty"]), digits=val["assetDecimals"]) + " " + val["coin"]
                    self.history_table.setItem(0, 4, QTableWidgetItem(qty))


                    total = '{number:.{digits}f}'.format(number=float(order["price"]) * float(order["executedQty"]), digits=8)

                    self.history_table.setItem(0, 5, QTableWidgetItem('{number:.{digits}f}'.format(number=float(order["price"]) * float(order["executedQty"]), digits=8) + " BTC"))

                    if order["side"] == "BUY":
                        self.history_table.item(0, 2).setForeground(QColor(color_green))
                    else:
                        self.history_table.item(0, 2).setForeground(QColor(color_pink))

                # handle open orders
                # Date	Pair	Type	Side	Price	Amount	Filled%	Total	Trigger Conditions
                elif order["status"] == "NEW":
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

                    self.open_orders.item(0, 9).setForeground(QColor(color_yellow))

                    if order["side"] == "BUY":
                        self.open_orders.item(0, 3).setForeground(QColor(color_green))
                    else:
                        self.open_orders.item(0, 3).setForeground(QColor(color_pink))


            self.history_table.scrollToTop()
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

        sell_size = self.round_sell_amount(sell_percent)

        self.limit_sell_amount.setValue(sell_size)



    def round_sell_amount(self, percent_val):
        holding = float(val["accHoldings"][val["coin"]]["free"]) * (float(percent_val) / 100)
        if val["coins"][val["pair"]]["minTrade"] == 1:
                sizeRounded = int(holding)
        else:
            sizeRounded = int(holding * 10**val["assetDecimals"]) / 10.0**val["assetDecimals"]
        return sizeRounded

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
            self.tradeTable.item(0, 0).setForeground(QColor(color_pink))
        else:
            self.tradeTable.item(0, 0).setForeground(QColor(color_green))

        self.tradeTable.item(0, 2).setForeground(QColor(color_lightgrey))


        self.tradeTable.removeRow(50)
        # # set last price, color and arrow
        #
        if float(self.tradeTable.item(0, 0).text()) > float(self.tradeTable.item(1, 0).text()):
            arrow = QPixmap("img/2arrow_up.png")
            color = color_green
        elif float(self.tradeTable.item(0, 0).text()) == float(self.tradeTable.item(1, 0).text()):
            arrow = QPixmap("img/2arrow.png")
            color = color_yellow
        else:
            arrow = QPixmap("img/2arrow_down.png")
            color = color_pink

        formatted_price = '{number:.{digits}f}'.format(number=float(val["globalList"][0]["price"]), digits=val["decimals"])
        self.price_arrow.setPixmap(arrow)

        self.last_price.setText("<span style='font-size: 20px; font-family: Arial Black; color:" + color + "'>" + formatted_price + "</span>")

        usd_price = '{number:.{digits}f}'.format(number=float(val["globalList"][0]["price"]) * float(val["tether"]["lastPrice"]), digits=2)

        self.usd_value.setText("<span style='font-size: 18px; font-family: Arial Black; color: " + color_yellow + "'>$" + usd_price + "</span>")


    def progress_asks(self, asks):
        for i, value in enumerate(asks):
            ask_price = '{number:.{digits}f}'.format(number=float(asks[i][0]), digits=val["decimals"])
            ask_quantity = '{number:.{digits}f}'.format(number=float(asks[i][1]), digits=val["assetDecimals"])
            total_btc_asks = '{number:.{digits}f}'.format(number=float(ask_price) * float(ask_quantity), digits=3)

            self.asks_table.setItem(19-i, 0, QTableWidgetItem(str(i+1).zfill(2)))

            self.asks_table.setItem(19-i, 1, QTableWidgetItem(ask_price))
            self.asks_table.setItem(19-i, 2, QTableWidgetItem(ask_quantity))

            self.asks_table.setItem(19-i, 3, QTableWidgetItem(total_btc_asks + " BTC"))
            self.asks_table.item(19-i, 1).setForeground(QColor(color_pink))

            # self.asks_table.scrollToBottom()

        spread = ((float(val["asks"][0][0]) / float(val["bids"][0][0])) - 1) * 100
        spread_formatted = '{number:.{digits}f}'.format(number=spread, digits=2) + "%"

        self.spread_label.setText("<span style='font-size: 14px; font-family: Arial Black; color:" + color_lightgrey + "'>" + spread_formatted + "</span>")

    def progress_bids(self, bids):
        for i, value in enumerate(bids):
            bid_price = '{number:.{digits}f}'.format(number=float(bids[i][0]), digits=val["decimals"])
            bid_quantity = '{number:.{digits}f}'.format(number=float(bids[i][1]), digits=val["assetDecimals"])
            total_btc_bids = '{number:.{digits}f}'.format(number=float(bid_price) * float(bid_quantity), digits=3)

            self.bids_table.setItem(i, 0, QTableWidgetItem(str(i+1).zfill(2)))

            self.bids_table.setItem(i, 1, QTableWidgetItem(bid_price))
            self.bids_table.setItem(i, 2, QTableWidgetItem(bid_quantity))

            self.bids_table.setItem(i, 3, QTableWidgetItem(total_btc_bids + " BTC"))
            self.bids_table.item(i, 1).setForeground(QColor(color_green))

    # Draw UI changes
    def progress_fn(self, payload):
        try:
            asks = payload["asks"]
            if len(asks) == 20:
                for i, value in enumerate(asks):
                    ask_price = '{number:.{digits}f}'.format(number=float(asks[i][0]), digits=val["decimals"])
                    ask_quantity = '{number:.{digits}f}'.format(number=float(asks[i][1]), digits=val["assetDecimals"])
                    total_btc_asks = '{number:.{digits}f}'.format(number=float(ask_price) * float(ask_quantity), digits=3)

                    self.asks_table.setItem(19-i, 0, QTableWidgetItem(str(i+1).zfill(2)))

                    self.asks_table.setItem(19-i, 1, QTableWidgetItem(ask_price))
                    self.asks_table.setItem(19-i, 2, QTableWidgetItem(ask_quantity))

                    self.asks_table.setItem(19-i, 3, QTableWidgetItem(total_btc_asks + " BTC"))
                    self.asks_table.item(19-i, 1).setForeground(QColor(color_pink))

                    # self.asks_table.scrollToBottom()

            spread = ((float(val["asks"][0][0]) / float(val["bids"][0][0])) - 1) * 100
            spread_formatted = '{number:.{digits}f}'.format(number=spread, digits=2) + "%"

            self.spread_label.setText("<span style='font-size: 14px; font-family: Arial Black; color:" + color_lightgrey + "'>" + spread_formatted + "</span>")
        except (TypeError, KeyError):
            pass


        try:
            bids = payload["bids"]
            if len(bids) == 20:
                for i, value in enumerate(bids):
                    bid_price = '{number:.{digits}f}'.format(number=float(bids[i][0]), digits=val["decimals"])
                    bid_quantity = '{number:.{digits}f}'.format(number=float(bids[i][1]), digits=val["assetDecimals"])
                    total_btc_bids = '{number:.{digits}f}'.format(number=float(bid_price) * float(bid_quantity), digits=3)

                    self.bids_table.setItem(i, 0, QTableWidgetItem(str(i+1).zfill(2)))

                    self.bids_table.setItem(i, 1, QTableWidgetItem(bid_price))
                    self.bids_table.setItem(i, 2, QTableWidgetItem(bid_quantity))

                    self.bids_table.setItem(i, 3, QTableWidgetItem(total_btc_bids + " BTC"))
                    self.bids_table.item(i, 1).setForeground(QColor(color_green))


        except (TypeError, KeyError):
            pass

        try:
            history = payload["history"]
            for index, trade in enumerate(history):
                self.tradeTable.setItem(index, 0, QTableWidgetItem('{number:.{digits}f}'.format(number=float(trade["price"]), digits=val["decimals"])))
                self.tradeTable.setItem(index, 1, QTableWidgetItem('{number:.{digits}f}'.format(number=float(trade["quantity"]), digits=val["assetDecimals"])))



                self.tradeTable.setItem(index, 2, QTableWidgetItem(str(datetime.fromtimestamp(int(str(trade["time"])[:-3])).strftime('%H:%M:%S.%f')[:-7])))

                if trade["maker"] is True:
                    self.tradeTable.item(index, 0).setForeground(QColor(color_pink))
                else:
                    self.tradeTable.item(index, 0).setForeground(QColor(color_green))

                self.tradeTable.item(index, 2).setForeground(QColor(color_lightgrey))

            # set last price, color and arrow

            if history[0]["price"] > history[1]["price"]:
                arrow = QPixmap("img/2arrow_up.png")
                color = color_green
            elif history[0]["price"] == history[1]["price"]:
                arrow = QPixmap("img/2arrow.png")
                color = color_yellow
            else:
                arrow = QPixmap("img/2arrow_down.png")
                color = color_pink

            formatted_price = '{number:.{digits}f}'.format(number=float(val["globalList"][0]["price"]), digits=val["decimals"])
            self.price_arrow.setPixmap(arrow)

            self.last_price.setText("<span style='font-size: 20px; font-family: Arial Black; color:" + color + "'>" + formatted_price + "</span>")

            usd_price = '{number:.{digits}f}'.format(number=float(val["globalList"][0]["price"]) * float(val["tether"]["lastPrice"]), digits=2)

            self.usd_value.setText("<span style='font-size: 18px; font-family: Arial Black; color: " + color_yellow + "'>$" + usd_price + "</span>")

        except (TypeError, KeyError, ValueError):
            pass

    def limit_percentage(self):
        button_number = int(self.sender().objectName()[-1:])

        value = percentage_ammount(val["accHoldings"]["BTC"]["free"], self.limit_buy_input.value(), int(val["buttonPercentage"][button_number]), val["assetDecimals"])

        self.limit_buy_amount.setValue(float(value))

        self.limit_buy_slider.setValue(int(val["buttonPercentage"][button_number]))

    def limit_percentage_sell(self):
        button_number = int(self.sender().objectName()[-1:])
        value = float(val["accHoldings"][val["coin"]]["free"]) * (float(val["buttonPercentage"][button_number]) / 100)

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
        print(val["accHoldings"][val["coin"]]["free"])
        sell_percent = str(self.limit_sell_slider.value())

        sell_size = self.round_sell_amount(sell_percent)

        self.limit_sell_amount.setValue(sell_size)


        self.sell_slider_label.setText(sell_percent + "%")

        value = percentage_ammount(val["accHoldings"]["BTC"]["free"], self.limit_buy_input.value(), int(sell_percent), val["assetDecimals"])

        order_cost = float(value) * float(self.limit_sell_input.value())
        self.limit_sell_total.setText('{number:.{digits}f}'.format(number=order_cost, digits=8) + " BTC")

        # if order_cost < 0.002:
        #     self.limit_sell_button.setStyleSheet("border: 2px solid orange;")
        # else:
        #     self.limit_sell_button.setStyleSheet("border: 2px solid #151a1e;")


    ####################################
    ########## VALIDATATION
    ####################################

    def check_sell_ammount(self):
        # total = float(self.limit_sell_amount.text()) *

        try:
            if float(self.limit_sell_amount.text()) > float(val["accHoldings"][val["coin"]]["free"]):
                self.limit_sell_button.setStyleSheet("border: 2px solid red;")
            else:
                self.limit_sell_button.setStyleSheet("border: 2px solid #151a1e;")
        except ValueError:
            pass
        self.calc_total_sell()

    def check_buy_ammount(self):

        total = int(((float(self.limit_buy_amount.value()) * float(self.limit_buy_input.value())) / float(val["accHoldings"]["BTC"]["free"])) * 100)

        self.calc_total_buy()

        try:
            min_trade = val["coins"][val["pair"]]["minTrade"]

            total = float(self.limit_buy_input.value()) * float(self.limit_buy_amount.text())

            print("total: " + str(total))
            print(type(total))

            if total != 0.0:
                if total > float(val["accHoldings"]["BTC"]["free"]) or total < 0.001:
                    self.limit_buy_button.setStyleSheet("border: 2px solid transparent; background: #678034; color: #666;")
                    self.limit_buy_button.setCursor(QCursor(Qt.ForbiddenCursor))
                    val["buyEnabled"] = False

                else:
                    self.limit_buy_button.setCursor(QCursor(Qt.PointingHandCursor))
                    self.limit_buy_button.setStyleSheet("border: 2px solid transparent;")
                    val["buyEnabled"] = True

            else:
                self.limit_buy_button.setStyleSheet("border: 2px solid transparent;")
                val["buyEnabled"] = False
                self.limit_buy_button.setCursor(QCursor(Qt.ForbiddenCursor))
        except ValueError:
            pass



    def schedule_work(self):
        # Pass the function to execute

        worker = Worker(self.check_for_update)
        # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.print_output)
        # worker.signals.finished.connect(self.t_complete)

        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.threadpool.start(worker)


    def schedule_websockets(self):
            # Pass the function to execute
            worker = Worker(self.start_sockets)
            # Any other args, kwargs are passed to the run function
            worker.signals.result.connect(self.print_output)
            # worker.signals.finished.connect(self.t_complete)
            worker.signals.progress.connect(self.progress_fn)

            # Execute
            self.threadpool.start(worker)


    def api_calls(self):
        worker = Worker(self.api_history)
        worker.signals.progress.connect(self.progress_fn)
        self.threadpool.start(worker)

        worker = Worker(self.api_depth)
        worker.signals.progress.connect(self.progress_fn)
        worker.signals.finished.connect(self.t_complete)
        self.threadpool.start(worker)

        worker = Worker(self.api_order_history)
        worker.signals.progress.connect(self.orders_finished)
        self.threadpool.start(worker)

    def api_history(self, progress_callback):
        val["globalList"] = getTradehistory(client, val["pair"])
        progress_callback.emit({"history": val["globalList"]})

    def api_depth(self, progress_callback):
        depth = getDepth(client, val["pair"])
        val["asks"] = depth["asks"]
        progress_callback.emit({"asks": val["asks"]})
        val["bids"] = depth["bids"]
        progress_callback.emit({"bids": val["bids"]})

    def api_order_history(self, progress_callback):
        orders = getOrders(client, val["pair"])
        progress_callback.emit({"orders": orders})


    # threaded orders

    # cancel an order from a separate thread
    def cancel_order_byId(self, id, symbol):

        worker = Worker(partial(self.api_cancel_order, id, symbol))
        worker.signals.progress.connect(self.cancel_callback)
        self.threadpool.start(worker)

    # cancel the order and call the callback when done
    def api_cancel_order(self, id, symbol, progress_callback):
        print("cancel order " + str(symbol) + " " + str(id))
        try:
            client.cancel_order(symbol=symbol, orderId=id)
        except BinanceAPIException:
            print("cancel failed")

        # not needed since user socket handles this
        # progress_callback.emit(result)

    # remove canceled order from open orders table
    def cancel_callback(self, payload):

        for row in range(self.open_orders.rowCount()):
            try:
                if str(self.open_orders.item(row, 8).text()) == str(payload["orderId"]):

                    self.open_orders.removeRow(row)

            except AttributeError:
                pass





    def create_buy_order(self):
        if val["buyEnabled"] is True:
            pair = val["pair"]
            price = '{number:.{digits}f}'.format(number=self.limit_buy_input.value(), digits=val["decimals"])

            amount = '{number:.{digits}f}'.format(number=self.limit_buy_amount.value(), digits=val["assetDecimals"])
            side = "Buy"

            worker = Worker(partial(self.api_create_order, side, pair, price, amount))
            worker.signals.progress.connect(self.create_order_callback)
            self.threadpool.start(worker)

    def create_sell_order(self):
        pair = val["pair"]
        price = '{number:.{digits}f}'.format(number=self.limit_sell_input.value(), digits=val["decimals"])

        amount = '{number:.{digits}f}'.format(number=self.limit_sell_amount.value(), digits=val["assetDecimals"])

        side = "Sell"

        worker = Worker(partial(self.api_create_order, side, pair, price, amount))
        worker.signals.progress.connect(self.create_order_callback)
        self.threadpool.start(worker)


    def api_create_order(self, side, pair, price, amount, progress_callback):
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
        except BinanceAPIException:
            print("create order failed")


    def create_order_callback(self, payload):
        print("order created!")
        print(payload)


    def check_for_update(self, progress_callback):

        while 2<1:
            # print("check")
            try:
                # print("check hist")
                if current_history != val["tradeHistory"]:
                    progress_callback.emit({"history": val["tradeHistory"][:]})


                if current_bids != val["bids"]:
                    progress_callback.emit({"bids": val["bids"][:]})


                if current_asks != val["asks"]:
                    progress_callback.emit({"asks": val["asks"][:]})

                if current_height != self.frameGeometry().height():
                    self.asks_table.scrollToBottom()


            except (KeyError, UnboundLocalError):
                pass

            current_bids = val["bids"]
            current_asks = val["asks"]
            current_history = val["tradeHistory"]
            current_height = self.frameGeometry().height()

            time.sleep(0.05)



    def start_sockets(self, progress_callback):

        val["bm"] = BinanceSocketManager(client)

        self.websockets()

        # start user websocket separately since it does not need to be restarted
        val["userWebsocket"] = val["bm"].start_user_socket(partial(userCallback, self))


        val["bm"].start()

    def websockets(self):
        val["aggtradeWebsocket"] = val["bm"].start_aggtrade_socket(val["pair"], partial(directCallback, self))

        val["depthWebsocket"] = val["bm"].start_depth_socket(val["pair"], partial(depthCallback, self), depth=20)



    def write_config(self):
        key = self.api_key.text()
        secret = self.api_secret.text()
        defaultPair = self.default_pair.text()
        defaultTimeframe = self.default_timeframe.text()

        copy_price = self.copy_price_box.isChecked()
        copy_qty = self.copy_qty_box.isChecked()
        print("checkbox state:" + str(copy_price) + " " + str(copy_qty))
        # percent_1 = self.percent_1.text()
        # percent_2 = self.percent_2.text()
        # percent_3 = self.percent_3.text()
        # percent_4 = self.percent_4.text()
        # percent_5 = self.percent_5.text()

        percent_texts = [self.percent_1, self.percent_2, self.percent_3, self.percent_4, self.percent_5]
        percent = val["buttonPercentage"]

        for i, value in enumerate(percent):

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
                            'DefaultTimeframe': defaultTimeframe,
                            'CopyPrice': copy_price,
                            'CopyQuantity': copy_qty,
                            }
        config["API"] = {"Key": key, "Secret": secret}

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        read_config()
        self.set_button_text()

    def socket_history(self, history, progress_callback):
        progress_callback.emit(history)

    def socket_orderbook(self, depth, progress_callback):
        progress_callback.emit(depth)

    def add_open_order(self, order, progress_callback):
        progress_callback.emit({"orders": order})

    def update_holdings(self, progress_callback):
        progress_callback.emit("update")


    def holding_updated(self):

        self.limit_total_btc.setText(str(val["accHoldings"]["BTC"]["free"]) + " BTC")
        self.limit_total_coin.setText(str(val["accHoldings"][val["coin"]]["free"]) + " " + val["coin"])

        print("Porcc")
        for i in range(self.holdings_table.rowCount()):
            coin = self.holdings_table.item(i, 1).text()
            free = val["accHoldings"][coin]["free"]
            locked = val["accHoldings"][coin]["locked"]
            total = float(free) + float(locked)
            # self.holdings_table.setItem(i, 3, QTableWidgetItem(total))
            # self.holdings_table.setItem(i, 4, QTableWidgetItem(free))
            # self.holdings_table.setItem(i, 5, QTableWidgetItem(locked))

            self.holdings_table.item(i, 3).setText(str(total))
            self.holdings_table.item(i, 4).setText(str(free))
            self.holdings_table.item(i, 5).setText(str(locked))



    def total_btc(self):
        total_btc = 0
        for holding in val["accHoldings"]:
            free = val["accHoldings"][holding]["free"]
            locked = val["accHoldings"][holding]["locked"]
            total = float(free) + float(locked)
            try:
                if holding != "BTC" and total * float(val["coins"][holding+"BTC"]["close"]) > 0.002:

                    coin_total = total * float(val["coins"][holding+"BTC"]["close"])
                    total_btc += coin_total


                elif holding == "BTC":
                    total_btc += total
            except KeyError:
                pass
        total_formatted = '{number:.{digits}f}'.format(number=float(total_btc), digits=8) + " BTC"

        return total_formatted

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

def initial_values(self):
    self.limit_total_btc.setText(str(val["accHoldings"]["BTC"]["free"]) + " BTC")
    self.limit_total_coin.setText(str(val["accHoldings"][val["coin"]]["free"]) + " " + val["coin"])

    self.limit_buy_label.setText("<span style='font-weight: bold;'>Buy " + val["coin"] + "</span>")
    self.limit_sell_label.setText("<span style='font-weight: bold;'>Sell " + val["coin"] + "</span>")

    # self.limit_buy_input.setText("kernoschmaus")
    self.limit_buy_input.setDecimals(val["decimals"])
    self.limit_buy_input.setSingleStep(float(val["coins"][val["pair"]]["tickSize"]))

    self.limit_sell_input.setDecimals(val["decimals"])
    self.limit_sell_input.setSingleStep(float(val["coins"][val["pair"]]["tickSize"]))

    self.limit_buy_amount.setDecimals(val["assetDecimals"])
    self.limit_buy_amount.setSingleStep(float(val["coins"][val["pair"]]["minTrade"]))

    self.limit_sell_amount.setDecimals(val["assetDecimals"])
    self.limit_sell_amount.setSingleStep(float(val["coins"][val["pair"]]["minTrade"]))

    self.buy_asset.setText(val["coin"])
    self.sell_asset.setText(val["coin"])


    self.chart.setHtml(build_chart2(val["pair"]))
    self.chart.show()

    bids_header = self.bids_table.horizontalHeader()
    asks_header = self.asks_table.horizontalHeader()
    bids_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
    bids_header.setSectionResizeMode(1, QHeaderView.Fixed)
    bids_header.setSectionResizeMode(2, QHeaderView.Fixed)

    asks_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
    asks_header.setSectionResizeMode(1, QHeaderView.Fixed)
    asks_header.setSectionResizeMode(2, QHeaderView.Fixed)





def build_holdings(self, *args):
    for holding in val["accHoldings"]:

        try:
            name = val["coins"][holding + "BTC"]["baseAssetName"]
        except KeyError:
            name = "Bitcoin"
        free = val["accHoldings"][holding]["free"]
        locked = val["accHoldings"][holding]["locked"]
        total = float(free) + float(locked)
        total_formatted = '{number:.{digits}f}'.format(number=total, digits=8)

        bold_font = QFont()
        bold_font.setBold(True)

        try:
            if holding == "BTC":
                icon = QIcon("ico/" + str(holding) + ".svg")

                icon_item = QTableWidgetItem()
                icon_item.setIcon(icon)
                self.holdings_table.insertRow(0)
                self.holdings_table.setItem(0, 0, icon_item)

                self.holdings_table.setItem(0, 1, QTableWidgetItem(holding))
                self.holdings_table.setItem(0, 2, QTableWidgetItem(name))
                self.holdings_table.setItem(0, 3, QTableWidgetItem(total_formatted))
                self.holdings_table.setItem(0, 4, QTableWidgetItem(free))
                self.holdings_table.setItem(0, 5, QTableWidgetItem(locked))
                self.holdings_table.setItem(0, 6, QTableWidgetItem(total_formatted))

                self.holdings_table.item(0, 6).setFont(bold_font)
                self.holdings_table.item(0, 6).setForeground(QColor(color_lightgrey))

                self.btn_sell = QPushButton('Trade' + " BTC")
                self.btn_sell.setEnabled(False)
                self.btn_sell.setStyleSheet("color: #666;")
                self.btn_sell.clicked.connect(self.gotoTradeButtonClicked)
                self.holdings_table.setCellWidget(0,7,self.btn_sell)


            elif float(total) * float(val["coins"][holding + "BTC"]["close"]) >= 0.002:
                icon = QIcon("ico/" + str(holding) + ".svg")

                icon_item = QTableWidgetItem()
                icon_item.setIcon(icon)

                total_btc = total * float(val["coins"][holding + "BTC"]["close"])
                total_btc_formatted = '{number:.{digits}f}'.format(number=total_btc, digits=8)


                self.holdings_table.insertRow(1)
                self.holdings_table.setItem(1, 0, icon_item)

                self.holdings_table.setItem(1, 1, QTableWidgetItem(holding))
                self.holdings_table.setItem(1, 2, QTableWidgetItem(name))
                self.holdings_table.setItem(1, 3, QTableWidgetItem(total_formatted))
                self.holdings_table.setItem(1, 4, QTableWidgetItem(free))
                self.holdings_table.setItem(1, 5, QTableWidgetItem(locked))
                self.holdings_table.setItem(1, 6, QTableWidgetItem(total_btc_formatted))

                self.holdings_table.item(1, 6).setFont(bold_font)
                self.holdings_table.item(1, 6).setForeground(QColor(color_lightgrey))

                self.btn_sell = QPushButton('Trade ' + str(holding))
                self.btn_sell.clicked.connect(self.gotoTradeButtonClicked)
                self.holdings_table.setCellWidget(1,7,self.btn_sell)

        except KeyError:
            pass

        header = self.holdings_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        self.holdings_table.setIconSize(QSize(25, 25))




def directCallback(self, msg):
    val["globalList"].insert(0, {"price": msg["p"], "quantity": msg["q"], "maker": bool(msg["m"]), "time": msg["T"]})

    if len(val["globalList"]) > 50:
        val["globalList"].pop()

    # make a copy to track changes later
    val["tradeHistory"] = val["globalList"][:]


    history = {"price": msg["p"], "quantity": msg["q"], "maker": bool(msg["m"]), "time": msg["T"]}
    worker = Worker(partial(self.socket_history, history))
    worker.signals.progress.connect(self.progress_history)
    # worker.signals.finished.connect(self.t_complete)
    self.threadpool.start(worker)


def depthCallback(self, msg):
    old_bids = val["bids"]
    old_asks = val["asks"]

    val["bids"] = msg["bids"]
    val["asks"] = msg["asks"]

    if old_bids != val["bids"]:
        worker = Worker(partial(self.socket_orderbook, msg["bids"]))
        worker.signals.progress.connect(self.progress_bids)
        # worker.signals.finished.connect(self.t_complete)
        self.threadpool.start(worker)
    if old_asks != val["asks"]:
        worker = Worker(partial(self.socket_orderbook, msg["asks"]))
        worker.signals.progress.connect(self.progress_asks)
        # worker.signals.finished.connect(self.t_complete)
        self.threadpool.start(worker)



def userCallback(self, msg):
    # print("user callback")
    # print("####################")
    # print(str(self))
    # print(msg)


    for key, value in msg.items():
        userMsg[key] = value

    if userMsg["e"] == "outboundAccountInfo":
        for i in range(len(userMsg["B"])):

            # put account info in accHoldings dictionary. Access free and locked holdings like so: accHoldings["BTC"]["free"]
            val["accHoldings"][userMsg["B"][i]["a"]] = {"free": userMsg["B"][i]["f"], "locked": userMsg["B"][i]["l"]}


        # update holdings table in a separate thread
        worker = Worker(self.update_holdings)
        worker.signals.progress.connect(self.holding_updated)
        self.threadpool.start(worker)

    elif userMsg["e"] == "executionReport":
            order = dict()
            order = [{"symbol": userMsg["s"], "price": userMsg["p"], "origQty": userMsg["q"], "side": userMsg["S"], "orderId": userMsg["i"], "status": userMsg["X"], "time": userMsg["T"], "type": userMsg["o"], "executedQty": userMsg["z"]}]

            print("user msg procc")


            if userMsg["X"] == "NEW":





                worker = Worker(partial(self.add_open_order, order))
                worker.signals.progress.connect(self.orders_finished)
                self.threadpool.start(worker)

            elif userMsg["X"] == "CANCELED":
                self.cancel_callback(order[0])

            elif userMsg["X"] == "FILLED":
                self.cancel_callback(order[0])
                print("filled order!")
                print(order)
                worker = Worker(partial(self.add_open_order, order))
                worker.signals.progress.connect(self.orders_finished)
                self.threadpool.start(worker)






if __name__ == "__main__":
    app = QApplication(sys.argv)

    # QFontDatabase.addApplicationFont('static/Roboto-Bold.ttf')
    #

    app.setStyle(QStyleFactory.create('Fusion'))

    widget = beeserBot()
    widget.show()

    sys.exit(app.exec_())
