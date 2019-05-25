# from app.workers import Worker
import os
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

from app.colors import Colors
from datetime import timedelta
import time
from app.gui import logging
from app.workers import Worker
from app.charts import Webpages

from app.helpers import resource_path

class ExamplePopup(QtWidgets.QDialog):
    
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name
        self.label = QtWidgets.QLabel(self.name, self)

class GuiManager:

    """Methods concerning the global UI."""

    def __init__(self, mw, tp):
        self.mw = mw
        self.update_count = 0
        self.no_updates = 0
        self.threadpool = tp
        mw.popup_btn.clicked.connect(self.show_notification)

        self.last_btc_price = 0
        self.runtime = 0
        self.buildExamplePopup("name")
        
    def buildExamplePopup(self, name):
        self.exPopup = ExamplePopup(name, self.mw)
        self.exPopup.setGeometry(100, 200, 100, 100)
        self.exPopup.show()

    def show_tooltip(self):
        point = QtCore.QPoint(100, 100)
        QtWidgets.QToolTip.showText(point, "LELLO SCHMELLO", self.mw.top_groupBox)

    # Refactor
    def initialize(self):
        self.initial_last_price()
        # self.initial_values()
        
        self.api_init()

        # self.mw.coin_selector.setup()

    # Refactor
    def initial_last_price(self):
        return
        # init last_price
        arrow = QtGui.QPixmap("images/assets/2arrow.png")
        formatted_price = '{number:.{digits}f}'.format(number=float(self.mw.tickers[self.mw.cfg_manager.pair]["lastPrice"]), digits=self.mw.tickers[self.mw.cfg_manager.pair]["decimals"])
        self.mw.price_arrow.setPixmap(arrow)
        self.mw.last_price.setText("<span style='font-size: 20px; font-family: Arial Black; color:" + Colors.color_yellow + "'>" + formatted_price + "</span>")
        usd_price = '{number:.{digits}f}'.format(number=float(self.mw.tickers[self.mw.cfg_manager.pair]["lastPrice"]) * float(self.mw.tickers["BTCUSDT"]["lastPrice"]), digits=2)
        self.mw.usd_value.setText("<span style='font-size: 18px; font-family: Arial Black; color: " + Colors.color_yellow + "'>$" + usd_price + "</span>")

    # gui init
    def api_init(self):
        """One-time gui initialization."""
        self.mw.api_manager.api_calls()
        self.mw.websocket_manager.schedule_websockets()
        self.mw.gui_manager.schedule_work()

        # CMC Chart:
        # TODO: Reenable
        # self.set_charts(self.mw.cfg_manager.pair)
        self.mw.chart.show()

        icon = QtGui.QIcon(resource_path("images/ico/" + "BTC" + ".svg"))
        self.mw.quote_asset_box.addItem(icon, "BTC")
        self.mw.quote_asset_box.setIconSize(QtCore.QSize(25, 25))

        # delayed stuff; TODO: Refactor
        self.mw.timer = QtCore.QTimer()
        self.mw.timer.setInterval(200)
        self.mw.timer.timeout.connect(self.mw.delayed_stuff)
        self.mw.timer.start()

    # refactor
    # global ui
    def check_for_update(self, progress_callback):
        """Check if main window height has changed. If so,
        scroll asks to bottom."""
        current_height = self.mw.frameGeometry().height()
        while True:
            if current_height != self.mw.frameGeometry().height():
                progress_callback.emit(15)

            current_height = self.mw.frameGeometry().height()
            progress_callback.emit(1)

            # self.mw.fishbot_table.check_fish_bot()
            time.sleep(1)

    # refactor
    def tick(self, payload):
        if payload == 1:
            self.one_second_update()

        elif payload == 15:
            print("scroll to bottom")
            # self.mw.asks_table.scrollToBottom()
            self.mw.new_asks.scrollToTop()
            self.mw.new_asks.scrollToBottom()

    # TODO refactor
    # global ui
    def one_second_update(self):

        """Update some values every second."""

        self.runtime += 1

        # self.mw.index_view.websocket_update()

        # test
        # self.mw.tabsBotLeft.adjustSize()
        # self.mw.coin_index_filter.adjustSize()

        total_btc_value = self.calc_total_btc()
        self.mw.total_btc_label.setText("<span style='font-size: 14px; color: #f3ba2e; font-family: Arial Black;'>" + total_btc_value + "</span>")

        total_usd_value = '{number:,.{digits}f}'.format(number=float(total_btc_value.replace(" BTC", "")) * float(self.mw.tickers["BTCUSDT"]["lastPrice"]), digits=2) + "$"
        self.mw.total_usd_label.setText("<span style='font-size: 14px; color: white; font-family: Arial Black;'>" + total_usd_value + "</span>")

        last_btc_price = float(self.mw.tickers["BTCUSDT"]["lastPrice"])
        last_btc_price_formatted = '{number:,.{digits}f}'.format(number=last_btc_price, digits=2) + "$"

        if last_btc_price > self.last_btc_price:
            last_color = Colors.color_green
        elif last_btc_price == self.last_btc_price:
            last_color = Colors.color_lightgrey
        else:
            last_color = Colors.color_pink

        self.mw.btc_price_label.setText("<span style='color: " + last_color + "'>" + last_btc_price_formatted + "</span>")
        self.last_btc_price = last_btc_price

        operator = ""
        percent_change = float(self.mw.tickers["BTCUSDT"]["priceChangePercent"])
        if percent_change > 0:
            operator = "+"
            percent_color = Colors.color_green
        else:
            percent_color = Colors.color_pink

        btc_percent = operator + '{number:,.{digits}f}'.format(number=percent_change, digits=2) + "%"
        self.mw.btc_percent_label.setText("<span style='color: " + percent_color + "'>" + btc_percent + "</span>")

        high = float(self.mw.tickers["BTCUSDT"]["highPrice"])
        low = float(self.mw.tickers["BTCUSDT"]["lowPrice"])
        vol = float(self.mw.tickers["BTCUSDT"]["volume"])

        high_formatted = '{number:,.{digits}f}'.format(number=high, digits=2) + "$"
        low_formatted = '{number:,.{digits}f}'.format(number=low, digits=2) + "$"
        vol_formatted = '{number:,.{digits}f}'.format(number=vol, digits=2) + " BTC"

        self.mw.btc_high_label.setText("<span style='color: " + Colors.color_green + "'>" + high_formatted + "</span>")
        self.mw.btc_low_label.setText("<span style='color: " + Colors.color_pink + "'>" + low_formatted + "</span>")
        self.mw.btc_vol_label.setText("<span style='color: " + Colors.color_lightgrey + "'>" + vol_formatted + "</span>")

        self.percent_changes()
        self.check_websocket()
        self.update_stats()

    def update_stats(self):
        session_time = str(timedelta(seconds=self.runtime))
        # total_time = str(timedelta(seconds=self.runtime + int(val["stats"]["timeRunning"])))

        self.mw.session_running.setText(session_time)
        # self.mw.total_running.setText(total_time)

        self.mw.current_time.setText(str(time.strftime('%a, %d %b %Y %H:%M:%S')))

        # self.mw.explicit_api_calls_label.setText(str(val["apiCalls"]))
        self.mw.explicit_api_updates.setText(str(self.mw.websocket_manager.api_updates))

    # global ui / logic REFACTOR
    def check_websocket(self):
        """Check if websocket updates stop occuring."""
        if self.update_count == int(self.mw.websocket_manager.api_updates):
            self.no_updates += 1
        else:
            self.no_updates = 0

        self.update_count = int(self.mw.websocket_manager.api_updates)

        if self.no_updates >= 2 and self.no_updates < 10:
            self.mw.status_label.setText("<span style='color:" + Colors.color_yellow + "'>waiting</span>")
        elif self.no_updates >= 10:
            self.mw.status_label.setText("<span style='color:" + Colors.color_pink + "'>disconnected!</span>")
        else:
            self.mw.status_label.setText("<span style='color:" + Colors.color_green + "'>connected</span>")

    # global ui # todo: refactor
    def percent_changes(self):

        """Calculate and display price change values."""

        # close_t = float(val["klines"]["1m"].get(self.mw.cfg_manager.pair, {})[-5][4])
        klines_data = self.mw.klines.get("1m")
        coin_data = klines_data.get(self.mw.cfg_manager.pair)

        if isinstance(coin_data, list):
            close_5m = float(self.mw.klines["1m"][self.mw.cfg_manager.pair][-5][4])
            close_15m = float(self.mw.klines["1m"][self.mw.cfg_manager.pair][-15][4])
            # close_30m = float(self.mw.klines["1m"][self.mw.cfg_manager.pair][-30][4])
            close_1h = float(self.mw.klines["1m"][self.mw.cfg_manager.pair][-60][4])
            close_4h = float(self.mw.klines["1m"][self.mw.cfg_manager.pair][-240][4])

            change_5m_value = ((float(self.mw.tickers[self.mw.cfg_manager.pair]["lastPrice"]) / float(close_5m)) - 1) * 100
            change_15m_value = ((float(self.mw.tickers[self.mw.cfg_manager.pair]["lastPrice"]) / float(close_15m)) - 1) * 100
            # change_30m_value = ((float(self.mw.tickers[self.mw.cfg_manager.pair]["lastPrice"]) / float(close_30m)) - 1) * 100
            change_1h_value = ((float(self.mw.tickers[self.mw.cfg_manager.pair]["lastPrice"]) / float(close_1h)) - 1) * 100
            change_4h_value = ((float(self.mw.tickers[self.mw.cfg_manager.pair]["lastPrice"]) / float(close_4h)) - 1) * 100

            change_1d_value = float(self.mw.tickers[self.mw.cfg_manager.pair]["priceChangePercent"])

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

    # Modified; New data
    def calc_total_btc(self):
        """Multiply holdings by their current price to get
        the total account value."""
        total_btc_val = 0
        for holding in self.mw.user_data.holdings:
            free = self.mw.user_data.holdings[holding]["free"]
            locked = self.mw.user_data.holdings[holding]["locked"]
            total = float(free) + float(locked)

            if holding + "BTC" in self.mw.data.tickers:
                if holding != "BTC" and total * float(self.mw.data.tickers[holding + "BTC"]["lastPrice"]) > 0.001:

                    coin_total = total * float(self.mw.data.tickers[holding + "BTC"]["lastPrice"])
                    total_btc_val += coin_total

            elif holding == "BTC":
                total_btc_val += total

        total_formatted = '{number:.{digits}f}'.format(number=float(total_btc_val), digits=8) + " BTC"
        # print("total: " + total_formatted)
        return total_formatted

    # global ui
    def schedule_work(self):

        # Pass the function to execute
        worker = Worker(self.check_for_update)

        # Any other args, kwargs are passed to the run function
        # worker.signals.result.connect(self.print_output)
        worker.signals.progress.connect(self.tick)

        # start thread
        self.threadpool.start(worker)

    def show_notification(self):
        print("SHOW NOTIF")
        icon = QtGui.QIcon("images/assets/icon.png")
        menu = QtWidgets.QMenu()
        self.tray = QtWidgets.QSystemTrayIcon()
        self.tray.setIcon(icon)
        self.tray.setContextMenu(menu)
        self.tray.show()
        self.tray.setToolTip("Beeser Binance Bot")
        self.tray.showMessage("hoge", "moge")
        self.tray.showMessage("fuga", "moge")
