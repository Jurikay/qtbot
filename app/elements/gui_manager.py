# from app.workers import Worker
# import PyQt5.QtWidgets as QtWidgets
# import PyQt5.QtGui as QtGui
# import PyQt5.QtCore as QtCore
from app.init import val
from app.colors import Colors
from datetime import timedelta
import time
from app.gui import logging


class GuiManager:

    def __init__(self, mw):
        self.mw = mw
        self.update_count = 0
        self.no_updates = 0


    def initialize(self):
        pass

    # global ui
    def check_for_update(self, progress_callback):
        """Check if main window height has changed. If so,
        scroll asks to bottom."""
        current_height = self.mw.frameGeometry().height()
        while True:
            if current_height > self.mw.frameGeometry().height():
                progress_callback.emit(15)

            current_height = self.mw.frameGeometry().height()
            progress_callback.emit(1)
            time.sleep(1)

    # main gui
    def change_pair(self):
        """Change the active pair and call symbol specific functions."""
        newcoin = self.mw.coin_selector.currentText()

        if any(newcoin + "BTC" in s for s in val["coins"]) and newcoin != val["coin"]:
            val["pair"] = newcoin + "BTC"
            val["bm"].stop_socket(val["aggtradeWebsocket"])
            val["bm"].stop_socket(val["depthWebsocket"])
            val["bm"].stop_socket(val["klineWebsocket"])
            logging.info('Switching to %s' % newcoin + " / BTC")

            self.mw.api_manager.set_pair_values()

            self.mw.init_manager.initial_values()

            self.mw.websockets_symbol()

            self.mw.history_table.setRowCount(0)

            self.mw.api_manager.api_calls()

            self.mw.init_filter()


    # refactor
    def tick(self, payload):
        if payload == 1:
            self.one_second_update()

        elif payload == 15:
            print("scroll to bottom")
            self.mw.asks_table.scrollToBottom()


    # global ui
    def one_second_update(self):
        """Update some values every second."""
        self.mw.session_running.setText(str(timedelta(seconds=val["timeRunning"])))
        val["timeRunning"] += 1

        self.mw.current_time.setText(str(time.strftime('%a, %d %b %Y %H:%M:%S')))

        self.mw.explicit_api_calls_label.setText(str(val["apiCalls"]))
        self.mw.explicit_api_updates.setText(str(val["apiUpdates"]))

        total_btc_value = self.calc_total_btc()
        self.mw.total_btc_label.setText("<span style='font-size: 14px; color: #f3ba2e; font-family: Arial Black;'>" + total_btc_value + "</span>")

        total_usd_value = '{number:,.{digits}f}'.format(number=float(total_btc_value.replace(" BTC", "")) * float(val["tickers"]["BTCUSDT"]["lastPrice"]), digits=2) + "$"

        self.mw.total_usd_label.setText("<span style='font-size: 14px; color: white; font-family: Arial Black;'>" + total_usd_value + "</span>")

        self.mw.btc_price_label.setText('{number:,.{digits}f}'.format(number=float(val["tickers"]["BTCUSDT"]["lastPrice"]), digits=2) + "$")

        operator = ""
        percent_change = float(val["tickers"]["BTCUSDT"]["priceChangePercent"])
        if percent_change > 0:
            operator = "+"

        btc_percent = operator + '{number:,.{digits}f}'.format(number=percent_change, digits=2) + "%"

        self.mw.btc_percent_label.setText(btc_percent)

        self.mw.debug.setText(str(val["volDirection"]))

        self.mw.debug.setText('{number:.{digits}f}'.format(number=float(val["volDirection"]), digits=4) + "BTC")

        self.percent_changes()

        self.check_websocket()

        # only update the currently active table
        tab_index_botLeft = self.mw.tabsBotLeft.currentIndex()

        if tab_index_botLeft == 3:
            self.mw.holdings_table.update_holding_prices()
            val["indexTabOpen"] = False
        elif tab_index_botLeft == 0:
            self.mw.coin_index.update_coin_index_prices()

            # decouple eventually
            self.mw.coin_index.start_kline_iterator()
            val["indexTabOpen"] = True
            # self.start_kline_iterator()
        else:
            val["indexTabOpen"] = False


    # global ui / logic
    def check_websocket(self):
        """Check if websocket updates stop occuring."""
        if self.update_count == int(val["apiUpdates"]):
            self.no_updates += 1
        else:
            self.no_updates = 0

        self.update_count = int(val["apiUpdates"])

        if self.no_updates >= 2 and self.no_updates < 10:
            self.mw.status.setText("<span style='color:" + Colors.color_yellow + "'>warning</span>")
        elif self.no_updates >= 10:
            self.mw.status.setText("<span style='color:" + Colors.color_pink + "'>disconnected</span>")
        else:
            self.mw.status.setText("<span style='color:" + Colors.color_green + "'>connected</span>")

    # global ui
    def percent_changes(self):
        """Calculate and display price change values."""
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


                changes = [self.mw.change_5m, self.mw.change_15m, self.mw.change_1h, self.mw.change_4h, self.mw.change_1d]
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


    @staticmethod
    def calc_total_btc():
        """Multiply holdings by their current price to get
        the total account value."""
        total_btc_val = 0
        for holding in val["accHoldings"]:
            free = val["accHoldings"][holding]["free"]
            locked = val["accHoldings"][holding]["locked"]
            total = float(free) + float(locked)

            if holding + "BTC" in val["coins"]:
                if holding != "BTC" and total * float(val["tickers"][holding + "BTC"]["lastPrice"]) > 0.001:

                    coin_total = total * float(val["tickers"][holding + "BTC"]["lastPrice"])
                    total_btc_val += coin_total

            elif holding == "BTC":
                total_btc_val += total

        total_formatted = '{number:.{digits}f}'.format(number=float(total_btc_val), digits=8) + " BTC"
        # print("total: " + total_formatted)
        return total_formatted
