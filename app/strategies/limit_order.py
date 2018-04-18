# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

# import PyQt5.QtGui as QtGui
# import PyQt5.QtWidgets as QtWidgets

from app.init import val
# from app.colors import Colors


# change
# from app.apiFunctions import percentage_amount, round_sell_amount


class LimitOrder():
    """Class containing methods to create limit orders."""

    def __init__(self, gui):
        LimitOrder.gui = gui

    # def test_func(self):
    #     print(self)


    @staticmethod
    def open_orders_cell_clicked(self, row, column):
        """Method to cancel open orders from open orders table."""
        print("open orders click")

        gui = LimitOrder.gui

        if column == 11:
            order_id = str(gui.open_orders.item(row, 10).text())
            pair = str(gui.open_orders.item(row, 2).text())

            # todo: fix
            self.mw.open_orders.cancel_order_byId(order_id, pair)


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
