import logging
# from app.workers import Worker
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from app.init import val
from app.charts import Webpages
# from app.colors import Colors
# from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage


class InitManager:

    """ UI initialization that happens before API data arrives."""

    def __init__(self, mw):
        self.mw = mw
        self.counter = 0


    def initialize(self):
        """Initial initialization :^)"""
        self.set_modes()
        self.main_init()
        self.table_setup()


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

        self.mw.btc_chart.setHtml(Webpages.build_chart_btc("BTCUSD", self.mw.cfg_manager.btcTimeframe, self.mw.cfg_manager.btcExchange))
        self.mw.btc_chart.show()
        self.mw.chart.show()


    # maybe move this into limit_pane
    def table_setup(self):

        coin = self.mw.cfg_manager.coin

        


        bids_header = self.mw.bids_table.horizontalHeader()
        asks_header = self.mw.asks_table.horizontalHeader()
        
        bids_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        bids_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        bids_header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        bids_header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)

        asks_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        asks_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        asks_header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        asks_header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        # asks_header.setSectionResizeMode(4, QtWidgets.QHeaderView.Fixed)

        trades_header = self.mw.tradeTable.horizontalHeader()
        trades_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        trades_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)

        # self.mw.bids_table.setCellW


    def show_error_page(self):
        self.mw.chart.setHtml(Webpages.welcome_page())
        self.mw.chart.show()
        self.mw.bot_tabs.setCurrentIndex(4)

        self.mw.api_key_label.setStyleSheet("border: 2px solid #f3ba2e;")
        self.mw.api_secret_label.setStyleSheet("border: 2px solid #f3ba2e;")
