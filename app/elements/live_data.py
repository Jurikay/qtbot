# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import app
from datetime import datetime
from app.init import val
# from app.table_items import CoinDelegate
from app.colors import Colors


class LiveData(QtWidgets.QWidget):
    """Widget containing other widgets to display live websocket data."""
    def __init__(self, parent=None):
        super(LiveData, self).__init__(parent)
        self.mw = app.mw
        self.history_progressed = False
        self.ob_progressed = False


    # live data
    def progress_history(self, trade):
        """Callback function to add trades to the trade history table."""
        self.mw.tradeTable.insertRow(0)
        
        price_item = QtWidgets.QTableWidgetItem('{number:.{digits}f}'.format(number=float(trade["price"]), digits=val["decimals"]))
        qty_item = QtWidgets.QTableWidgetItem('{number:.{digits}f}'.format(number=float(trade["quantity"]), digits=val["assetDecimals"]))
        time_item = QtWidgets.QTableWidgetItem(str(datetime.fromtimestamp(int(str(trade["time"])[:-3])).strftime('%H:%M:%S.%f')[:-7]))

        price_item.setTextAlignment(QtCore.Qt.AlignRight)
        qty_item.setTextAlignment(QtCore.Qt.AlignRight)
        time_item.setTextAlignment(QtCore.Qt.AlignHCenter)

        self.mw.tradeTable.setItem(0, 0, price_item)
        self.mw.tradeTable.setItem(0, 1, qty_item)
        self.mw.tradeTable.setItem(0, 2, time_item)

        if trade["maker"] is True:
            self.mw.tradeTable.item(0, 0).setForeground(QtGui.QColor(Colors.color_pink))

            val["volDirection"] -= float(trade["price"]) * float(trade["quantity"])
        else:
            self.mw.tradeTable.item(0, 0).setForeground(QtGui.QColor(Colors.color_green))
            val["volDirection"] += float(trade["price"]) * float(trade["quantity"])

        self.mw.tradeTable.item(0, 2).setForeground(QtGui.QColor(Colors.color_lightgrey))


        if self.history_progressed is True and self.ob_progressed is True:
            # self.mw.tradeTable.update()
            self.set_last_price()
            self.set_spread()



    def set_last_price(self):

        history = self.mw.trade_history[:]

        # set color and arrow based on the last two trades
        if float(history[0]["price"]) > float(history[1]["price"]):
            arrow = QtGui.QPixmap("images/assets/2arrow_up.png")
            color = Colors.color_green
        elif float(history[0]["price"]) == float(history[1]["price"]):
            arrow = QtGui.QPixmap("images/assets/2arrow.png")
            color = Colors.color_yellow
        else:
            arrow = QtGui.QPixmap("images/assets/2arrow_down.png")
            color = Colors.color_pink


        formatted_price = '{number:.{digits}f}'.format(number=float(history[0]["price"]), digits=val["decimals"])
        self.mw.price_arrow.setPixmap(arrow)

        self.mw.last_price.setText("<span style='font-size: 20px; font-family: Arial Black; color:" + color + "'>" + formatted_price + "</span>")

        usd_price = '{number:.{digits}f}'.format(number=float(history[0]["price"]) * float(val["tickers"]["BTCUSDT"]["lastPrice"]), digits=2)

        self.mw.usd_value.setText("<span style='font-size: 18px; font-family: Arial Black; color: " + Colors.color_yellow + "'>$" + usd_price + "</span>")

        if self.mw.tradeTable.rowCount() >= 50:
            self.mw.tradeTable.removeRow(50)



    def progress_orderbook(self, order_data):
        order = order_data[0]
        order_type = order_data[1]

        for i, _ in enumerate(order):
            if order_type == "asks":
                start_index = 19
                text_color = QtGui.QColor(Colors.color_pink)
                table = self.mw.asks_table
                
            elif order_type == "bids":
                start_index = i * 2
                text_color = QtGui.QColor(Colors.color_green)
                table = self.mw.bids_table

            ask_price = '{number:.{digits}f}'.format(number=float(order[i][0]), digits=val["decimals"])
            ask_quantity = '{number:.{digits}f}'.format(number=float(order[i][1]), digits=val["assetDecimals"])
            total_btc_asks = '{number:.{digits}f}'.format(number=float(ask_price) * float(ask_quantity), digits=3)
            
            count_item = QtWidgets.QTableWidgetItem(str(i + 1).zfill(2))
            price_item = QtWidgets.QTableWidgetItem(ask_price)
            qty_item = QtWidgets.QTableWidgetItem(ask_quantity)
            total_item = QtWidgets.QTableWidgetItem(total_btc_asks + " BTC ")

            count_item.setTextAlignment(QtCore.Qt.AlignRight)
            price_item.setTextAlignment(QtCore.Qt.AlignRight)
            qty_item.setTextAlignment(QtCore.Qt.AlignRight)
            total_item.setTextAlignment(QtCore.Qt.AlignRight)

            table.setItem(start_index - i, 0, count_item)
            table.setItem(start_index - i, 1, price_item)
            table.setItem(start_index - i, 2, qty_item)
            table.setItem(start_index - i, 3, total_item)
            table.item(start_index - i, 1).setForeground(text_color)


    # live data
    def set_spread(self):
        if len(val["bids"]) > 1 and len(val["asks"]) > 1:
            spread = ((float(val["asks"][0][0]) / float(val["bids"][0][0])) - 1) * 100
            spread_formatted = '{number:.{digits}f}'.format(number=spread, digits=2) + "%"

            self.mw.spread_label.setText("<span style='font-size: 18px; font-family: Arial Black; color:" + Colors.color_lightgrey + "'>" + spread_formatted + "</span>")


    # Draw UI changes (bids, asks, history)
    def batch_orderbook(self, payload):
        # logging.info("progress FN")
        self.ob_progressed = False
        asks = payload.get("asks", "")
        bids = payload.get("bids", "")

        if len(asks) == 20:
            for _ in enumerate(asks):
                self.progress_orderbook([asks, "asks"])

        if len(bids) == 20:
            for _ in enumerate(bids):
                self.progress_orderbook([bids, "bids"])

        self.ob_progressed = True
        # self.set_spread()


    def batch_history(self, payload):
        self.mw.trade_history = []
        self.history_progressed = False
        history = payload.get("history", "")
        # if len(list(history)) > 10:
        for trade in enumerate(history):
            self.progress_history(trade[1])
            self.mw.trade_history.append(trade[1])

        self.history_progressed = True
        self.mw.tradeTable.update()
        self.set_last_price()
