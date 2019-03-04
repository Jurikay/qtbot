import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from functools import partial
import logging
import app

from app.workers import Worker

# TODO: Refactor; replace val references


class LimitOrderPane(QtWidgets.QWidget):
    def __init__(self):
        super(LimitOrderPane, self).__init__()
        self.mw = app.mw
        # self.initialize()

    def set_holding_values(self):
        """Update values based on updated holdings."""
        coin = self.mw.cfg_manager.coin
        btc_qty = self.mw.user_data.holdings["BTC"]["free"]
        coin_qty = self.mw.user_data.holdings[coin]["free"]
        self.mw.limit_total_btc.setText(str(btc_qty) + " BTC")
        self.mw.limit_total_coin.setText(str(coin_qty) + " " + coin)

        self.mw.limit_pane.check_buy_amount()
        self.mw.limit_pane.check_sell_amount()



    def buy_slider_move(self):
        buy_percent_val = str(self.mw.limit_buy_slider.value())
        self.mw.buy_slider_label.setText(buy_percent_val + "%")

        buy_value = self.percentage_amount(self.mw.user_data.holdings["BTC"]["free"], self.mw.limit_buy_input.value(), int(buy_percent_val), self.mw.tickers[self.mw.cfg_manager.pair]["assetDecimals"])
        self.mw.limit_buy_amount.setValue(float(buy_value))
        order_cost = float(buy_value) * float(self.mw.limit_buy_input.value())
        self.mw.limit_buy_total.setText('{number:.{digits}f}'.format(number=order_cost, digits=8) + " BTC ")
        btc_usd = float(self.mw.tickers["BTCUSDT"]["lastPrice"])
        self.mw.limit_buy_total_usd.setText(' {number:,.{digits}f}'.format(number=order_cost * btc_usd, digits=0) + " $")

    def sell_slider_move(self):
        # Text to value
        print("ich slide")
        # print(self.mw.user_data.holdings[val["coin"]]["free"])
        sell_percent = str(self.mw.limit_sell_slider.value())

        sell_size = self.round_sell_amount(sell_percent)

        self.mw.limit_sell_amount.setValue(sell_size)


        self.mw.sell_slider_label.setText(sell_percent + "%")



    def limit_percentage(self):
        button_number = int(self.mw.sender().objectName()[-1:])


        # print("acch: " + str(self.mw.user_data.holdings["BTC"]["free"]))
        # print("buy input: " + str(self.mw.limit_buy_input.value()))
        # print("btn nmber: " + str(self.mw.cfg_manager.buttonPercentage[button_number]))
        # print("asset dec" + str(self.mw.tickers[self.mw.cfg_manager.pair]["assetDecimals"]))
        value = self.percentage_amount(self.mw.user_data.holdings["BTC"]["free"], self.mw.limit_buy_input.value(), int(self.mw.cfg_manager.buttonPercentage[button_number]), self.mw.tickers[self.mw.cfg_manager.pair]["assetDecimals"])

        self.mw.limit_buy_amount.setValue(float(value))

        self.mw.limit_buy_slider.setValue(int(self.mw.cfg_manager.buttonPercentage[button_number]))


    def limit_percentage_sell(self):
        button_number = int(self.mw.sender().objectName()[-1:])
        coin = self.mw.cfg_manager.coin
        value = float(self.mw.user_data.holdings[coin]["free"]) * (float(self.mw.cfg_manager.buttonPercentage[button_number]) / 100)
        print("sell btn", value, self.mw.cfg_manager.buttonPercentage[button_number])
        # print(self.mw.user_data.holdings[val["coin"]]["free"])
        self.mw.limit_sell_amount.setValue(float(value))
        self.mw.limit_sell_slider.setValue(int(self.mw.cfg_manager.buttonPercentage[button_number]))


    def calc_total_buy(self):
        try:
            total = float(self.mw.limit_buy_input.value()) * float(self.mw.limit_buy_amount.text())
            total_formatted = '{number:.{digits}f}'.format(number=total, digits=8)

            self.mw.limit_buy_total.setText(str(total_formatted) + " BTC ")
            btc_usd = float(self.mw.tickers["BTCUSDT"]["lastPrice"])
            self.mw.limit_buy_total_usd.setText(' {number:,.{digits}f}'.format(number=total * btc_usd, digits=0) + " $")

        except ValueError as e:
            print("calc total buy value error: " + str(e))


    def calc_total_sell(self):
        try:
            total = float(self.mw.limit_sell_input.value()) * float(self.mw.limit_sell_amount.text())
            total_formatted = '{number:.{digits}f}'.format(number=total, digits=8)
            self.mw.limit_sell_total.setText(str(total_formatted) + " BTC ")
            btc_usd = float(self.mw.tickers["BTCUSDT"]["lastPrice"])
            self.mw.limit_sell_total_usd.setText(' {number:,.{digits}f}'.format(number=total * btc_usd, digits=0) + " $")

        except ValueError:
            print("calc total sell ERROR")


    def initialize(self):


        self.mw.limit_buy_slider.valueChanged.connect(self.buy_slider_move)
        self.mw.limit_sell_slider.valueChanged.connect(self.sell_slider_move)

        self.mw.limit_buy_input.valueChanged.connect(self.calc_total_buy)
        self.mw.limit_sell_input.valueChanged.connect(self.calc_total_sell)


        self.mw.limit_sell_amount.valueChanged.connect(self.check_sell_amount)
        self.mw.limit_buy_amount.valueChanged.connect(self.check_buy_amount)

        self.mw.limit_sell_input.valueChanged.connect(self.check_sell_amount)
        self.mw.limit_buy_input.valueChanged.connect(self.check_buy_amount)

        # self.mw.tradeTable.cellClicked.connect(self.cell_was_clicked)

        # self.mw.bids_table.cellClicked.connect(self.bids_cell_clicked)

        # self.mw.asks_table.cellClicked.connect(self.asks_cell_clicked)

        self.init_buttons()


    def init_buttons(self):
        self.mw.limit_button0.clicked.connect(self.limit_percentage)
        self.mw.limit_button1.clicked.connect(self.limit_percentage)
        self.mw.limit_button2.clicked.connect(self.limit_percentage)
        self.mw.limit_button3.clicked.connect(self.limit_percentage)
        self.mw.limit_button4.clicked.connect(self.limit_percentage)

        self.mw.limit_sbutton0.clicked.connect(self.limit_percentage_sell)
        self.mw.limit_sbutton1.clicked.connect(self.limit_percentage_sell)
        self.mw.limit_sbutton2.clicked.connect(self.limit_percentage_sell)
        self.mw.limit_sbutton3.clicked.connect(self.limit_percentage_sell)
        self.mw.limit_sbutton4.clicked.connect(self.limit_percentage_sell)

        self.mw.limit_outbid.clicked.connect(self.overbid_undercut)
        self.mw.limit_undercut.clicked.connect(self.overbid_undercut)
        self.mw.limit_high.clicked.connect(self.overbid_undercut)
        self.mw.limit_low.clicked.connect(self.overbid_undercut)

        self.mw.limit_buy_button.clicked.connect(self.create_buy_order)
        self.mw.limit_sell_button.clicked.connect(self.create_sell_order)



    def round_sell_amount(self, percent_val):
        holding = float(self.mw.user_data.holdings[self.mw.cfg_manager.coin]["free"]) * (float(percent_val) / 100)
        if self.mw.tickers[self.mw.cfg_manager.pair]["minTrade"] == 1:
            sizeRounded = int(holding)
        else:
            sizeRounded = int(holding * 10**self.mw.tickers[self.mw.cfg_manager.pair]["assetDecimals"]) / 10.0**self.mw.tickers[self.mw.cfg_manager.pair]["assetDecimals"]
        return sizeRounded


    def overbid_undercut(self):
        try:
            print("NAME:", str(self.mw.sender))
            if self.mw.sender().text() == "outbid":
                self.mw.limit_buy_input.setValue(float(val["bids"][0][0]) + float(self.mw.tickers[self.mw.cfg_manager.pair]["tickSize"]))
            elif self.mw.sender().text() == "undercut":
                self.mw.limit_sell_input.setValue(float(val["asks"][0][0]) - float(self.mw.tickers[self.mw.cfg_manager.pair]["tickSize"]))
            elif self.mw.sender().text() == "daily low":
                self.mw.limit_buy_input.setValue(float(self.mw.tickers[self.mw.cfg_manager.pair]["lowPrice"]))
            elif self.mw.sender().text() == "daily high":
                self.mw.limit_sell_input.setValue(float(self.mw.tickers[self.mw.cfg_manager.pair]["highPrice"]))
        except KeyError as e:
            print("overbid undercut error", e)
####################################
    #           VALIDATATION
    ####################################

    def check_sell_amount(self):
        # total = float(self.limit_sell_amount.text()) *

        try:
            sell_amount = float(self.mw.limit_sell_amount.text())
            free_amount = float(self.mw.user_data.holdings[self.mw.cfg_manager.coin]["free"])
            sell_price = float(self.mw.limit_sell_input.text())

            if sell_amount > free_amount or sell_amount * sell_price < 0.001:
                self.mw.limit_sell_button.setStyleSheet("border: 2px solid transparent; background: #ff077a; color: #f3f3f3;")
                self.mw.limit_sell_button.setCursor(QtGui.QCursor(QtCore.Qt.ForbiddenCursor))
                val["sellAllowed"] = False
            else:
                self.mw.limit_sell_button.setStyleSheet("border: 2px solid transparent;")
                self.mw.limit_sell_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                val["sellAllowed"] = True

        except ValueError:
            print("val error")
            # pass
        self.calc_total_sell()


    def check_buy_amount(self):
        if float(self.mw.user_data.holdings["BTC"]["free"]) != 0:
            total = int(((float(self.mw.limit_buy_amount.value()) * float(self.mw.limit_buy_input.value())) / float(self.mw.user_data.holdings["BTC"]["free"])) * 100)
        else:
            total = 0
        # print("check buy")
        self.calc_total_buy()

        try:
            total = float(self.mw.limit_buy_input.value()) * float(self.mw.limit_buy_amount.text())

            if total > float(self.mw.user_data.holdings["BTC"]["free"]) or total < 0.001:
                self.mw.limit_buy_button.setStyleSheet("border: 2px solid transparent; background: #70a800; color: #f3f3f3;")
                self.mw.limit_buy_button.setCursor(QtGui.QCursor(QtCore.Qt.ForbiddenCursor))
                # val["buyAllowed"] = False

            else:
                self.mw.limit_buy_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                self.mw.limit_buy_button.setStyleSheet("border: 2px solid transparent;")
                # val["buyAllowed"] = True

        except ValueError as error:
            print(str(error))

#################################
# table cells clicked

    def cell_was_clicked(self, row, column):
        try:


            self.mw.limit_buy_input.setValue(float(self.mw.trade_history[row]["price"]))
            self.mw.limit_sell_input.setValue(float(self.mw.trade_history[row]["price"]))

        except IndexError as e:
            print(str(e))


    def bids_cell_clicked(self, row, column):
        self.mw.limit_buy_input.setValue(float(val["bids"][row][0]))
        self.mw.limit_sell_input.setValue(float(val["bids"][row][0]))


    def asks_cell_clicked(self, row, column):
        self.mw.limit_buy_input.setValue(float(val["asks"][19 - row][0]))
        self.mw.limit_sell_input.setValue(float(val["asks"][19 - row][0]))


    def create_buy_order(self):
        if val["buyAllowed"] is True:
            pair = self.mw.cfg_manager.pair
            price = '{number:.{digits}f}'.format(number=self.mw.limit_buy_input.value(), digits=self.mw.tickers[self.mw.cfg_manager.pair]["decimals"])

            amount = '{number:.{digits}f}'.format(number=self.mw.limit_buy_amount.value(), digits=self.mw.tickers[self.mw.cfg_manager.pair]["assetDecimals"])
            side = "Buy"

            worker = Worker(partial(self.mw.api_manager.api_create_order, side, pair, price, amount))
            # worker.signals.progress.connect(self.create_order_callback)
            self.mw.threadpool.start(worker)
            logging.info('[ + ] BUY ORDER CREATED! %s' % str(pair) + " " + str(amount) + " at " + str(price))


    def create_sell_order(self):
        if val["sellAllowed"] is True:
            pair = self.mw.cfg_manager.pair
            price = '{number:.{digits}f}'.format(number=self.mw.limit_sell_input.value(), digits=self.mw.tickers[self.mw.cfg_manager.pair]["decimals"])

            amount = '{number:.{digits}f}'.format(number=self.mw.limit_sell_amount.value(), digits=self.mw.tickers[self.mw.cfg_manager.pair]["assetDecimals"])

            side = "Sell"

            worker = Worker(partial(self.mw.api_manager.api_create_order, side, pair, price, amount))
            # worker.signals.progress.connect(self.create_order_callback)
            self.mw.threadpool.start(worker)
            logging.info('[ - ] SELL ORDER CREATED! %s' % str(pair) + " " + str(amount) + " at " + str(price))


    # do stuff once api data has arrived

    def t_complete(self):
        # print("We don now")
        self.mw.limit_buy_input.setValue(float(val["bids"][0][0]))
        self.mw.limit_sell_input.setValue(float(val["asks"][0][0]))
        value = self.percentage_amount(self.mw.user_data.holdings["BTC"]["free"], self.mw.limit_buy_input.value(), int(self.mw.buy_slider_label.text().strip("%")), self.mw.tickers[self.mw.cfg_manager.pair]["assetDecimals"])
        self.mw.limit_buy_amount.setValue(value)

        # print(self.mw.user_data.holdings[val["coin"]]["free"])
        sell_percent = str(self.mw.limit_sell_slider.value())

        sell_size = self.mw.limit_pane.round_sell_amount(sell_percent)

        self.mw.limit_sell_amount.setValue(sell_size)


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

    def init_tables(self):
        # Handle table initialization 
        pass



        # for _ in range(20):
        #     self.mw.bids_table.insertRow(0)
        #     self.mw.asks_table.insertRow(0)
        # self.mw.new_table.insertRow(0)

        # for _ in range(50):
        #     self.mw.tradeTable.insertRow(0)

        # self.mw.asks_table.setColumnWidth(0, 22)
        # self.mw.bids_table.setColumnWidth(0, 22)
        # self.mw.asks_table.setColumnWidth(1, 80)
        # self.mw.bids_table.setColumnWidth(1, 80)
        # self.mw.asks_table.setColumnWidth(2, 40)
        # self.mw.bids_table.setColumnWidth(2, 40)
        # self.mw.asks_table.setColumnWidth(3, 80)
        # self.mw.bids_table.setColumnWidth(3, 80)

        # self.mw.asks_table.setColumnWidth(4, 1)

        # self.mw.tradeTable.setColumnWidth(0, 80)
        # self.mw.tradeTable.setColumnWidth(1, 80)
