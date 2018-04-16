# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

# import PyQt5.QtGui as QtGui
# import PyQt5.QtWidgets as QtWidgets

from app.init import val
from app.colors import Colors


# change
# from app.apiFunctions import percentage_amount, round_sell_amount


class LimitOrder():
    """Class containing methods to create limit orders."""

    def __init__(self, gui):
        LimitOrder.gui = gui

    # def test_func(self):
    #     print(self)


    @staticmethod
    def open_orders_cell_clicked(row, column):
        """Method to cancel open orders from open orders table."""
        print("open orders click")

        gui = LimitOrder.gui

        if column == 11:
            order_id = str(gui.open_orders.item(row, 10).text())
            pair = str(gui.open_orders.item(row, 2).text())

            gui.cancel_order_byId(order_id, pair)


    @staticmethod
    def cell_was_clicked(row, column):
        try:
            reversed_list = val["tradeHistory"]

            LimitOrder.gui.limit_buy_input.setValue(float(reversed_list[row]["price"]))
            LimitOrder.gui.limit_sell_input.setValue(float(reversed_list[row]["price"]))

        except IndexError as e:
            print(str(e))


    @staticmethod
    def bids_cell_clicked(row, column):
        LimitOrder.gui.limit_buy_input.setValue(float(val["bids"][row][0]))
        LimitOrder.gui.limit_sell_input.setValue(float(val["bids"][row][0]))


    @staticmethod
    def asks_cell_clicked(row, column):
        LimitOrder.gui.limit_buy_input.setValue(float(val["asks"][19 - row][0]))
        LimitOrder.gui.limit_sell_input.setValue(float(val["asks"][19 - row][0]))


    @staticmethod
    def overbid_undercut():
        try:
            if LimitOrder.gui.sender().text() == "outbid":
                LimitOrder.gui.limit_buy_input.setValue(float(val["bids"][0][0]) + float(val["coins"][val["pair"]]["tickSize"]))
            elif LimitOrder.gui.sender().text() == "undercut":
                LimitOrder.gui.limit_sell_input.setValue(float(val["asks"][0][0]) - float(val["coins"][val["pair"]]["tickSize"]))
            elif LimitOrder.gui.sender().text() == "daily low":
                LimitOrder.gui.limit_buy_input.setValue(float(val["coins"][val["pair"]]["low"]))
            elif LimitOrder.gui.sender().text() == "daily high":
                LimitOrder.gui.limit_sell_input.setValue(float(val["coins"][val["pair"]]["high"]))
        except KeyError:
            pass

# INPUTS

    # def limit_percentage(self):
    #     button_number = int(self.sender().objectName()[-1:])

    #     value = percentage_amount(val["accHoldings"]["BTC"]["free"], self.limit_buy_input.value(), int(val["buttonPercentage"][button_number]), val["assetDecimals"])

    #     self.limit_buy_amount.setValue(float(value))

    #     self.limit_buy_slider.setValue(int(val["buttonPercentage"][button_number]))

    # def limit_percentage_sell(self):
    #     button_number = int(self.sender().objectName()[-1:])
    #     # value = float(val["accHoldings"][val["coin"]]["free"]) * (float(val["buttonPercentage"][button_number]) / 100)

    #     # print(val["accHoldings"][val["coin"]]["free"])
    #     # self.limit_sell_amount.setValue(value)

    #     self.limit_sell_slider.setValue(int(val["buttonPercentage"][button_number]))


    # def calc_total_buy(self):
    #     try:
    #         total = float(self.limit_buy_input.value()) * float(self.limit_buy_amount.text())
    #         total_formatted = '{number:.{digits}f}'.format(number=total, digits=8)

    #         self.limit_buy_total.setText(str(total_formatted) + " BTC")
    #     except ValueError:
    #         pass


    # def calc_total_sell(self):
    #     try:
    #         total = float(self.limit_sell_input.value()) * float(self.limit_sell_amount.text())
    #         total_formatted = '{number:.{digits}f}'.format(number=total, digits=8)
    #         self.limit_sell_total.setText(str(total_formatted) + " BTC")
    #     except ValueError:
    #         pass


    # def buy_slider(self):
    #     buy_percent_val = str(self.limit_buy_slider.value())
    #     self.buy_slider_label.setText(buy_percent_val + "%")

    #     buy_value = percentage_amount(val["accHoldings"]["BTC"]["free"], self.limit_buy_input.value(), int(buy_percent_val), val["assetDecimals"])
    #     self.limit_buy_amount.setValue(float(buy_value))
    #     order_cost = float(buy_value) * float(self.limit_buy_input.value())
    #     self.limit_buy_total.setText('{number:.{digits}f}'.format(number=order_cost, digits=8) + " BTC")

    #     # if order_cost < 0.002:
    #     #     self.limit_buy_button.setStyleSheet("border: 2px solid #bf4a3d;")
    #     # else:
    #     #     self.limit_buy_button.setStyleSheet("border: 2px solid #151a1e;")

    # def sell_slider(self):
    #     # Text to value
    #     print("ich slide")
    #     # print(val["accHoldings"][val["coin"]]["free"])
    #     sell_percent = str(self.limit_sell_slider.value())

    #     sell_size = round_sell_amount(sell_percent)

    #     self.limit_sell_amount.setValue(sell_size)


    #     self.sell_slider_label.setText(sell_percent + "%")

