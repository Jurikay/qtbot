import logging
# from app.workers import Worker
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from app.init import val
from app.charts import Webpages
from app.colors import Colors
# from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage


class InitManager:

    def __init__(self, mw):
        self.mw = mw
        self.counter = 0


    def initialize(self):
        """Initial initialization :^)"""
        self.initial_values()
        self.set_modes()
        self.main_init()


    def initial_values(self):
        """Set various values needed for further tasks. Gets called when the pair
        is changed."""
        self.mw.limit_total_btc.setText(str(val["accHoldings"]["BTC"]["free"]) + " BTC")
        self.mw.limit_total_coin.setText(str(val["accHoldings"][val["coin"]]["free"]) + " " + val["coin"])

        self.mw.limit_buy_label.setText("<span style='font-weight: bold; font-size: 12px;'>Buy " + val["coin"] + "</span>")
        self.mw.limit_sell_label.setText("<span style='font-weight: bold; font-size: 12px;'>Sell " + val["coin"] + "</span>")

        # self.mw.limit_coin_label_buy.setText("<span style='font-weight: bold; color: white;'>" + val["coin"] + "</span>")
        # self.mw.limit_coin_label_sell.setText("<span style='font-weight: bold; color: white;'>" + val["coin"] + "</span>")

        # self.mw.limit_buy_input.setText("kernoschmaus")
        self.mw.limit_buy_input.setDecimals(val["decimals"])
        self.mw.limit_buy_input.setSingleStep(float(val["coins"][val["pair"]]["tickSize"]))

        self.mw.limit_sell_input.setDecimals(val["decimals"])
        self.mw.limit_sell_input.setSingleStep(float(val["coins"][val["pair"]]["tickSize"]))

        self.mw.limit_buy_amount.setDecimals(val["assetDecimals"])
        self.mw.limit_buy_amount.setSingleStep(float(val["coins"][val["pair"]]["minTrade"]))

        self.mw.limit_sell_amount.setDecimals(val["assetDecimals"])
        self.mw.limit_sell_amount.setSingleStep(float(val["coins"][val["pair"]]["minTrade"]))

        self.mw.buy_asset.setText(val["coin"])
        self.mw.sell_asset.setText(val["coin"])

        self.mw.chart.setHtml(Webpages.build_chart2(val["pair"], val["defaultTimeframe"]))
        # self.mw.chart.backgroundColor(QtGui.QColor("#000000"))
        self.mw.chart.show()

        url = Webpages.build_cmc()
        self.mw.cmc_chart.load(QtCore.QUrl(url))

        bids_header = self.mw.bids_table.horizontalHeader()
        asks_header = self.mw.asks_table.horizontalHeader()
        bids_header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        bids_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        bids_header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        asks_header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        asks_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        asks_header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        trades_header = self.mw.tradeTable.horizontalHeader()
        trades_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        trades_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)


    # gui init
    def set_modes(self):
        if val["debug"] is False:
            # self.tabsBotLeft.setTabEnabled(0, False)
            self.mw.tabsBotLeft.removeTab(0)
            self.mw.ChartTabs.removeTab(5)
            self.mw.ChartTabs.removeTab(4)
            self.mw.ChartTabs.removeTab(3)
            self.mw.ChartTabs.setTabEnabled(1, False)

            self.mw.tabsBotLeft.setCurrentIndex(0)
            self.mw.ChartTabs.setCurrentIndex(0)
            self.mw.bot_tabs.setCurrentIndex(0)
        else:
            logging.info("DEBUG mode enabled")


    def main_init(self):
        """One time gui initialization."""
        # set default locale
        QtCore.QLocale.setDefault(QtCore.QLocale(QtCore.QLocale.C))

        logging.info('Initializing GUI')

        self.mw.setWindowTitle("Juris beeser Bot")

        self.mw.setWindowIcon(QtGui.QIcon('images/assets/256.png'))

        self.mw.restart_warning.setStyleSheet("color: transparent;")
        # self.mw.spread_area.setStyleSheet("background: #2e363d;")

        self.mw.holdings_table.setStyleSheet("alternate-background-color: #2e363d;")

        self.mw.counter = 0
        # self.mw.counter2 = 0

        # self.mw.update_count = 0
        # self.mw.no_updates = 0


    # gui init
    def api_init(self):
        """One-time gui initialization."""
        self.mw.api_manager.api_calls()

        self.initial_last_price()

        for coin in val["coins"]:

            icon = QtGui.QIcon("images/ico/" + coin[:-3] + ".svg")
            self.mw.coin_selector.addItem(icon, coin[:-3])

        self.mw.coin_selector.model().sort(0)
        self.mw.coin_selector.setIconSize(QtCore.QSize(25, 25))

        coinIndex = self.mw.coin_selector.findText(val["coin"])
        self.mw.coin_selector.setCurrentIndex(coinIndex)

        icon = QtGui.QIcon("images/ico/" + "BTC" + ".svg")
        self.mw.quote_asset_box.addItem(icon, "BTC")
        self.mw.quote_asset_box.setIconSize(QtCore.QSize(25, 25))
        self.mw.quote_asset_box.setIconSize(QtCore.QSize(25, 25))


        self.mw.websocket_manager.schedule_websockets()
        self.mw.gui_manager.schedule_work()

        self.mw.holdings_table.initialize()

        self.mw.coin_index.build_coinindex()


        # self.sound_1 = QSound('sounds/Tink.wav')
        self.mw.btc_chart.setHtml(Webpages.build_chart_btc("BTCUSD", val["defaultTimeframe"], "COINBASE"))
        self.mw.btc_chart.show()

        self.mw.ChartTabs.setCornerWidget(self.mw.volume_widget)

        self.mw.timer = QtCore.QTimer()
        self.mw.timer.setInterval(200)
        self.mw.timer.timeout.connect(self.mw.delayed_stuff)
        self.mw.timer.start()

    def initial_last_price(self):
        # init last_price
        arrow = QtGui.QPixmap("images/assets/2arrow.png")
        formatted_price = '{number:.{digits}f}'.format(number=float(val["tickers"][val["pair"]]["lastPrice"]), digits=val["decimals"])
        self.mw.price_arrow.setPixmap(arrow)
        self.mw.last_price.setText("<span style='font-size: 20px; font-family: Arial Black; color:" + Colors.color_yellow + "'>" + formatted_price + "</span>")
        usd_price = '{number:.{digits}f}'.format(number=float(val["tickers"][val["pair"]]["lastPrice"]) * float(val["tickers"]["BTCUSDT"]["lastPrice"]), digits=2)
        self.mw.usd_value.setText("<span style='font-size: 18px; font-family: Arial Black; color: " + Colors.color_yellow + "'>$" + usd_price + "</span>")
