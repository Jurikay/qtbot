import math
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
        self.buy_allowed = False
        self.sell_allowed = False
        

    # restructure
    def new_pair(self):
        """Called when the pair is changed. This triggers the change
        of all pair dependant values."""
        new_pair = self.mw.data.current.pair


    def set_holding_values(self):
        """Update values based on updated holdings."""
        coin = self.mw.data.current.coin
        btc_qty = self.mw.user_data.holdings["BTC"]["free"]
        coin_qty = self.mw.user_data.holdings[coin]["free"]
        self.mw.limit_total_btc.setText(str(btc_qty) + " BTC")
        self.mw.limit_total_coin.setText(str(coin_qty) + " " + coin)

        self.mw.limit_pane.check_buy_amount()
        self.mw.limit_pane.check_sell_amount()



    def buy_slider_move(self):
        self.mw.sound_manager.ps2()

        buy_percent_val = str(self.mw.limit_buy_slider.value())
        self.mw.buy_slider_label.setText(buy_percent_val + "%")

        buy_value = self.percentage_amount(self.mw.user_data.holdings["BTC"]["free"], self.mw.limit_buy_input.value(), int(buy_percent_val), self.mw.data.pairs[self.mw.data.current.pair]["assetDecimals"])
        self.mw.limit_buy_amount.setValue(float(buy_value))
        order_cost = float(buy_value) * float(self.mw.limit_buy_input.value())
        self.mw.limit_buy_total.setText('{number:.{digits}f}'.format(number=order_cost, digits=8) + " BTC ")
        btc_usd = float(self.mw.data.btc_price["lastPrice"])
        self.mw.limit_buy_total_usd.setText('${number:,.{digits}f}'.format(number=order_cost * btc_usd, digits=2))

    def sell_slider_move(self):
        """Called when the sell slider is moved. Sets sell valued based on percentage."""
        self.mw.sound_manager.ps2()

        sell_percent = str(self.mw.limit_sell_slider.value())
        sell_size = self.round_sell_amount(sell_percent)
        self.mw.limit_sell_amount.setValue(sell_size)
        self.mw.sell_slider_label.setText(sell_percent + "%")



    def limit_percentage(self):
        self.mw.sound_manager.ps2()
        button_number = int(self.mw.sender().objectName()[-1:])
        value = self.percentage_amount(self.mw.user_data.holdings["BTC"]["free"], self.mw.limit_buy_input.value(), int(self.mw.cfg_manager.buttonPercentage[button_number]), self.mw.data.pairs[self.mw.data.current.pair]["assetDecimals"])

        self.mw.limit_buy_amount.setValue(float(value))
        self.mw.limit_buy_slider.setValue(int(self.mw.cfg_manager.buttonPercentage[button_number]))


    def limit_percentage_sell(self):
        button_number = int(self.mw.sender().objectName()[-1:])
        coin = self.mw.data.current.coin
        value = float(self.mw.user_data.holdings[coin]["free"]) * (float(self.mw.cfg_manager.buttonPercentage[button_number]) / 100)
        print("sell btn", value, self.mw.cfg_manager.buttonPercentage[button_number])
        # print(self.mw.user_data.holdings[val["coin"]]["free"])
        self.mw.limit_sell_slider.setValue(int(self.mw.cfg_manager.buttonPercentage[button_number]))
        # self.mw.limit_sell_amount.setValue(float(value))

    def calc_total_buy(self):
        try:
            total = float(self.mw.limit_buy_input.value()) * float(self.mw.limit_buy_amount.text())
            total_formatted = '{number:.{digits}f}'.format(number=total, digits=8)

            self.mw.limit_buy_total.setText(str(total_formatted) + " BTC ")
            btc_usd = float(self.mw.data.btc_price["lastPrice"])
            self.mw.limit_buy_total_usd.setText('${number:,.{digits}f}'.format(number=total * btc_usd, digits=2))

        except ValueError as e:
            print("calc total buy value error: " + str(e))


    def calc_total_sell(self):
        try:
            total = float(self.mw.limit_sell_input.value()) * float(self.mw.limit_sell_amount.text())
            total_formatted = '{number:.{digits}f}'.format(number=total, digits=8)
            self.mw.limit_sell_total.setText(str(total_formatted) + " BTC ")
            btc_usd = float(self.mw.data.btc_price["lastPrice"])
            self.mw.limit_sell_total_usd.setText('${number:,.{digits}f}'.format(number=total * btc_usd, digits=2))

        except ValueError:
            print("calc total sell ERROR")


    def round_sell_amount(self, percent_val):
        holding = float(self.mw.user_data.holdings[self.mw.data.current.coin]["free"]) * float(percent_val) / 100
        if self.mw.data.pairs[self.mw.data.current.pair]["minTrade"] == 1:
            sizeRounded = int(holding)
        else:
            assetDecimals = int(self.mw.data.pairs[self.mw.data.current.pair]["assetDecimals"])

            integer_part = str(holding).split(".", 1)[0]
            decimal_part = str(holding).split(".", 1)[1]

            # Strip unneded decimals from string. This is done to avoid rounding errors.
            round_decimals = decimal_part[:assetDecimals]

            final_str = integer_part + "." + round_decimals
            sizeRounded = float(final_str)

        return sizeRounded


    def overbid_undercut(self):
        try:
            print("NAME:", str(self.mw.sender))
            if self.mw.sender().text() == "outbid":
                self.mw.limit_buy_input.setValue(float(self.mw.data.current.orderbook["bids"][0][0]) + float(self.mw.data.pairs[self.mw.data.current.pair]["tickSize"]))
            elif self.mw.sender().text() == "undercut":
                self.mw.limit_sell_input.setValue(float(self.mw.data.current.orderbook["asks"][0][0]) - float(self.mw.data.pairs[self.mw.data.current.pair]["tickSize"]))
            elif self.mw.sender().text() == "daily low":
                self.mw.limit_buy_input.setValue(float(self.mw.data.tickers[self.mw.data.current.pair]["lowPrice"]))
            elif self.mw.sender().text() == "daily high":
                self.mw.limit_sell_input.setValue(float(self.mw.data.tickers[self.mw.data.current.pair]["highPrice"]))
        except (KeyError, TypeError) as e:
            print("overbid undercut error", e)
####################################
    #           VALIDATATION
    ####################################

    def check_sell_amount(self):
        # total = float(self.limit_sell_amount.text()) *

        try:
            sell_amount = float(self.mw.limit_sell_amount.text())
            free_amount = float(self.mw.user_data.holdings[self.mw.data.current.coin]["free"])
            sell_price = float(self.mw.limit_sell_input.text())

            if sell_amount > free_amount or sell_amount * sell_price < 0.001:
                self.mw.limit_sell_button.setStyleSheet("border: 2px solid transparent; background: #ff077a; color: #f3f3f3;")
                self.mw.limit_sell_button.setCursor(QtGui.QCursor(QtCore.Qt.ForbiddenCursor))
                self.sell_allowed = False
            else:
                self.mw.limit_sell_button.setStyleSheet("border: 2px solid transparent;")
                self.mw.limit_sell_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                self.sell_allowed = True

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
                self.buy_allowed = False

            else:
                self.mw.limit_buy_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                self.mw.limit_buy_button.setStyleSheet("border: 2px solid transparent;")
                self.buy_allowed = True

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


    # def bids_cell_clicked(self, row, column):
    #     self.mw.limit_buy_input.setValue(float(val["bids"][row][0]))
    #     self.mw.limit_sell_input.setValue(float(val["bids"][row][0]))


    # def asks_cell_clicked(self, row, column):
    #     self.mw.limit_buy_input.setValue(float(val["asks"][19 - row][0]))
    #     self.mw.limit_sell_input.setValue(float(val["asks"][19 - row][0]))


    def create_buy_order(self):
        if self.buy_allowed is True:
            pair = self.mw.data.current.pair
            price = '{number:.{digits}f}'.format(number=self.mw.limit_buy_input.value(), digits=self.mw.data.pairs[self.mw.data.current.pair]["decimals"])

            amount = '{number:.{digits}f}'.format(number=self.mw.limit_buy_amount.value(), digits=self.mw.data.pairs[self.mw.data.current.pair]["assetDecimals"])
            side = "Buy"

            worker = Worker(partial(self.mw.api_manager.api_create_order, side, pair, price, amount))
            # worker.signals.progress.connect(self.create_order_callback)
            self.mw.threadpool.start(worker)
            logging.info('[ + ] BUY ORDER CREATED! %s' % str(pair) + " " + str(amount) + " at " + str(price))


    def create_sell_order(self):
        if self.sell_allowed is True:
            pair = self.mw.data.current.pair
            price = '{number:.{digits}f}'.format(number=self.mw.limit_sell_input.value(), digits=self.mw.data.pairs[self.mw.data.current.pair]["decimals"])

            amount = '{number:.{digits}f}'.format(number=self.mw.limit_sell_amount.value(), digits=self.mw.data.pairs[self.mw.data.current.pair]["assetDecimals"])

            side = "Sell"

            worker = Worker(partial(self.mw.api_manager.api_create_order, side, pair, price, amount))
            # worker.signals.progress.connect(self.create_order_callback)
            self.mw.threadpool.start(worker)
            logging.info('[ - ] SELL ORDER CREATED! %s' % str(pair) + " " + str(amount) + " at " + str(price))


    # do stuff once api data has arrived

    # def t_complete(self):
    #     # print("We don now")
    #     self.mw.limit_buy_input.setValue(float(val["bids"][0][0]))
    #     self.mw.limit_sell_input.setValue(float(val["asks"][0][0]))
    #     value = self.percentage_amount(self.mw.user_data.holdings["BTC"]["free"], self.mw.limit_buy_input.value(), int(self.mw.buy_slider_label.text().strip("%")), self.mw.data.pairs[self.mw.data.current.pair]["assetDecimals"])
    #     self.mw.limit_buy_amount.setValue(value)

    #     # print(self.mw.user_data.holdings[val["coin"]]["free"])
    #     sell_percent = str(self.mw.limit_sell_slider.value())

    #     sell_size = self.mw.limit_pane.round_sell_amount(sell_percent)

    #     self.mw.limit_sell_amount.setValue(sell_size)


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

    def connect_elements(self):
        """One-time ui setup."""
        self.mw.limit_buy_slider.valueChanged.connect(self.buy_slider_move)
        self.mw.limit_sell_slider.valueChanged.connect(self.sell_slider_move)
        self.mw.limit_buy_input.valueChanged.connect(self.calc_total_buy)
        self.mw.limit_sell_input.valueChanged.connect(self.calc_total_sell)
        self.mw.limit_sell_amount.valueChanged.connect(self.check_sell_amount)
        self.mw.limit_buy_amount.valueChanged.connect(self.check_buy_amount)
        self.mw.limit_sell_input.valueChanged.connect(self.check_sell_amount)
        self.mw.limit_buy_input.valueChanged.connect(self.check_buy_amount)

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

        self.set_button_text()
    
    def set_button_text(self):
        """Called when button config values are changed."""
        buttonPercentage = self.mw.cfg_manager.config["CONFIG"]["buttonpercentages"].split(", ")
        self.mw.limit_button0.setText(str(buttonPercentage[0]) + "%")
        self.mw.limit_button1.setText(str(buttonPercentage[1]) + "%")
        self.mw.limit_button2.setText(str(buttonPercentage[2]) + "%")
        self.mw.limit_button3.setText(str(buttonPercentage[3]) + "%")
        self.mw.limit_button4.setText(str(buttonPercentage[4]) + "%")

        self.mw.limit_sbutton0.setText(str(buttonPercentage[0]) + "%")
        self.mw.limit_sbutton1.setText(str(buttonPercentage[1]) + "%")
        self.mw.limit_sbutton2.setText(str(buttonPercentage[2]) + "%")
        self.mw.limit_sbutton3.setText(str(buttonPercentage[3]) + "%")
        self.mw.limit_sbutton4.setText(str(buttonPercentage[4]) + "%")
