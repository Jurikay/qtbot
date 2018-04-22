# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import PyQt5.QtWidgets as QtWidgets
# import PyQt5.QtCore as QtCore
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


    # live data
    def progress_history(self, trade):
        self.mw.tradeTable.insertRow(0)
        price_item = QtWidgets.QTableWidgetItem('{number:.{digits}f}'.format(number=float(trade["price"]), digits=val["decimals"]))
        # price_item.setTextAlignment(QtCore.Qt.AlignHCenter)

        self.mw.tradeTable.setItem(0, 0, price_item)

        qty_item = QtWidgets.QTableWidgetItem('{number:.{digits}f}'.format(number=float(trade["quantity"]), digits=val["assetDecimals"]))
        # qty_item.setTextAlignment(QtCore.Qt.AlignHCenter)
        self.mw.tradeTable.setItem(0, 1, qty_item)

        time_item = QtWidgets.QTableWidgetItem(str(datetime.fromtimestamp(int(str(trade["time"])[:-3])).strftime('%H:%M:%S.%f')[:-7]))
        # time_item.setTextAlignment(QtCore.Qt.AlignHCenter)
        self.mw.tradeTable.setItem(0, 2, time_item)

        if trade["maker"] is True:
            self.mw.tradeTable.item(0, 0).setForeground(QtGui.QColor(Colors.color_pink))

            val["volDirection"] -= float(trade["price"]) * float(trade["quantity"])
        else:
            self.mw.tradeTable.item(0, 0).setForeground(QtGui.QColor(Colors.color_green))
            val["volDirection"] += float(trade["price"]) * float(trade["quantity"])

        self.mw.tradeTable.item(0, 2).setForeground(QtGui.QColor(Colors.color_lightgrey))


        # # set last price, color and arrow
        #
        if self.history_progressed is True:
            if float(self.mw.tradeTable.item(0, 0).text()) > float(self.mw.tradeTable.item(1, 0).text()):
                arrow = QtGui.QPixmap("images/assets/2arrow_up.png")
                color = Colors.color_green
            elif float(self.mw.tradeTable.item(0, 0).text()) == float(self.mw.tradeTable.item(1, 0).text()):
                arrow = QtGui.QPixmap("images/assets/2arrow.png")
                color = Colors.color_yellow
            else:
                arrow = QtGui.QPixmap("images/assets/2arrow_down.png")
                color = Colors.color_pink

            formatted_price = '{number:.{digits}f}'.format(number=float(self.mw.trade_history[0]["price"]), digits=val["decimals"])
            self.mw.price_arrow.setPixmap(arrow)

            self.mw.last_price.setText("<span style='font-size: 20px; font-family: Arial Black; color:" + color + "'>" + formatted_price + "</span>")

            usd_price = '{number:.{digits}f}'.format(number=float(self.mw.trade_history[0]["price"]) * float(val["tickers"]["BTCUSDT"]["lastPrice"]), digits=2)

            self.mw.usd_value.setText("<span style='font-size: 18px; font-family: Arial Black; color: " + Colors.color_yellow + "'>$" + usd_price + "</span>")


        if self.mw.tradeTable.rowCount() >= 50:
            self.mw.tradeTable.removeRow(50)


    def progress_asks(self, asks):
        for i, _ in enumerate(asks):
            ask_price = '{number:.{digits}f}'.format(number=float(asks[i][0]), digits=val["decimals"])
            ask_quantity = '{number:.{digits}f}'.format(number=float(asks[i][1]), digits=val["assetDecimals"])
            total_btc_asks = '{number:.{digits}f}'.format(number=float(ask_price) * float(ask_quantity), digits=3)

            self.mw.asks_table.setItem(19 - i, 0, QtWidgets.QTableWidgetItem(str(i + 1).zfill(2)))

            self.mw.asks_table.setItem(19 - i, 1, QtWidgets.QTableWidgetItem(ask_price))
            self.mw.asks_table.setItem(19 - i, 2, QtWidgets.QTableWidgetItem(ask_quantity))

            self.mw.asks_table.setItem(19 - i, 3, QtWidgets.QTableWidgetItem(total_btc_asks + " BTC"))
            self.mw.asks_table.item(19 - i, 1).setForeground(QtGui.QColor(Colors.color_pink))
            self.set_spread()

            # self.mw.asks_table.scrollToBottom()

    def progress_bids(self, bids):
        for i, _ in enumerate(bids):
            bid_price = '{number:.{digits}f}'.format(number=float(bids[i][0]), digits=val["decimals"])
            bid_quantity = '{number:.{digits}f}'.format(number=float(bids[i][1]), digits=val["assetDecimals"])
            total_btc_bids = '{number:.{digits}f}'.format(number=float(bid_price) * float(bid_quantity), digits=3)

            self.mw.bids_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(i + 1).zfill(2)))

            self.mw.bids_table.setItem(i, 1, QtWidgets.QTableWidgetItem(bid_price))
            self.mw.bids_table.setItem(i, 2, QtWidgets.QTableWidgetItem(bid_quantity))

            self.mw.bids_table.setItem(i, 3, QtWidgets.QTableWidgetItem(total_btc_bids + " BTC"))
            self.mw.bids_table.item(i, 1).setForeground(QtGui.QColor(Colors.color_green))
            self.set_spread()

    # live data
    def set_spread(self):
        spread = ((float(val["asks"][0][0]) / float(val["bids"][0][0])) - 1) * 100
        spread_formatted = '{number:.{digits}f}'.format(number=spread, digits=2) + "%"

        self.mw.spread_label.setText("<span style='font-size: 18px; font-family: Arial Black; color:" + Colors.color_lightgrey + "'>" + spread_formatted + "</span>")


    # Draw UI changes (bids, asks, history)
    def batch_orderbook(self, payload):
        # logging.info("progress FN")
            asks = payload.get("asks", "")
            bids = payload.get("bids", "")

            if len(asks) == 20:
                for _ in enumerate(asks):
                    self.progress_asks(asks)

            if len(bids) == 20:
                for _ in enumerate(bids):
                    self.progress_bids(bids)


    def batch_history(self, payload):
        history = payload.get("history", "")
        # if len(list(history)) > 10:
        for trade in enumerate(history):
            self.progress_history(trade[1])
        self.history_progressed = True
