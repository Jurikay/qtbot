# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import PyQt5.QtWidgets as QtWidgets
# import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import app
# from app.init import val
# from app.table_items import CoinDelegate
from app.colors import Colors


class LiveData(QtWidgets.QWidget):
    """Widget containing other widgets to display live websocket data."""
    def __init__(self, parent=None):
        super(LiveData, self).__init__(parent)
        self.mw = app.mw
        self.history_progressed = False
        self.ob_progressed = False


    def set_history_values(self):
        self.set_last_price()
        self.mw.tradeTable.update()


    def set_last_price(self):

        history = self.mw.trade_history

        if history:
            # set color and arrow based on the last two trades
            if float(history[0][0]) > float(history[1][0]):
                arrow = QtGui.QPixmap("images/assets/2arrow_up.png")
                color = Colors.color_green
            elif float(history[0][0]) == float(history[1][0]):
                arrow = QtGui.QPixmap("images/assets/2arrow.png")
                color = Colors.color_yellow
            else:
                arrow = QtGui.QPixmap("images/assets/2arrow_down.png")
                color = Colors.color_pink


            formatted_price = '{number:.{digits}f}'.format(number=float(history[0][0]), digits=self.mw.tickers[self.mw.cfg_manager.pair]["decimals"])
            self.mw.price_arrow.setPixmap(arrow)
            self.mw.last_price.setText("<span style='font-size: 20px; font-family: Arial Black; color:" + color + "'>" + formatted_price + "</span>")
            usd_price = '{number:.{digits}f}'.format(number=float(history[0][0]) * float(self.mw.tickers["BTCUSDT"]["lastPrice"]), digits=2)
            self.mw.usd_value.setText("<span style='font-size: 18px; font-family: Arial Black; color: " + Colors.color_yellow + "'>$" + usd_price + "</span>")



    # TODO refactor
    # live data
    def set_spread(self):
        """Calclulate and set the percentual difference between the best bid and ask."""
        if self.mw.orderbook:
            spread = ((float(self.mw.orderbook["asks"][0][0]) / float(self.mw.orderbook["bids"][0][0])) - 1) * 100
            spread_formatted = '{number:.{digits}f}'.format(number=spread, digits=2) + "%"
            self.mw.spread_label.setText("<span style='font-size: 18px; font-family: Arial Black; color:" + Colors.color_lightgrey + "'>" + spread_formatted + "</span>")




    def batch_history(self, payload):
        """Initially setup trade histroy table."""
        self.mw.trade_history = []
        self.history_progressed = False
        history = payload.get("history", "")
        for trade in enumerate(history):
            self.mw.trade_history.append([trade[1]["price"], trade[1]["quantity"], bool(trade[1]["maker"]), trade[1]["time"]])

        self.history_progressed = True
        self.set_last_price()

        self.mw.tradeTable.setup()
