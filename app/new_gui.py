# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui


# from PyQt5.QtCore import pyqtSlot
import numpy as np
import pandas as pd

from app.charts import Webpages
from app.gui import logging
from app.helpers import resource_path
from app.elements.gui_periodic import GuiScheduler


class GuiMgr:

    def __init__(self, mw):
        self.mw = mw
        print("Init new gui mgr")
        # super().__init__(mw)
        self.set_tooltips()
        self.set_timer()
        self.timer_count = 0

        self.scheduler = GuiScheduler(mw)
        # self.mw.coin_selector.update()

        # tab stuff
        self.hide_tabs()
        self.setup_tabs()


    def set_timer(self):
        self.timer = QtCore.QTimer(self.mw)
        self.timer.setInterval(250)          # Throw event timeout with an interval of 1000 milliseconds
        self.timer.timeout.connect(self.blink)
        self.timer.start(1000)

    # Refactor:
    # Idea: Ticker websocket triggers this instead of QTimer.
    # This would ensure that functions trigger directly after new ticker data has been received.
    def blink(self):
        """Call all periodic ui updates here."""
        self.scheduler.update()


    # ######## Setup ##########
    def set_tooltips(self):
        print("Setting tooltips")
        # TODO: implement/remove
        # self.mw.limit_buy_input.setStatusTip("BUY TOOLTIP")
        # self.mw.limit_buy_input.setWhatsThis("WHAT TEH FUG")
        # print("INPUT:", self.mw.limit_buy_input.value())
    
    def set_api_dependant(self):
        return
        print("Setting api dependant gui values")
        # TODO: this is currently called too early to have an effect
        # self.mw.coin_selector.update()


############################

    def change_pair(self):
        """Change the active pair and call symbol specific methods."""
        data = self.mw.data
        
        current_pair = data.current.pair
        new_pair = self.mw.coin_selector.currentText()

        print("CHANGE_PAIR: from:", current_pair, "to:", new_pair)
        
        if any(new_pair in s for s in self.mw.data.tickers) and new_pair != current_pair:
            print("change pair to:", new_pair)

            data.set_current_pair(new_pair)

            self.set_charts(new_pair)

            self.mw.websocket_manager.stop_sockets()

            logging.info('Switching to %s' % new_pair)

            print("LIMIT PANE VALUES")
            self.limit_pane_current_values()

            # new 'initial data'
            self.mw.new_api.threaded_pair_update()
            self.mw.websocket_manager.websockets_symbol()
        
            # self.mw.api_manager.api_calls()
            self.update_hide_other_filter()

            # new
            # self.mw.trade_history_view.update()

    # TODO: Call this after loading default pair from config
    def change_to(self, coin):
        print("Change_to:", coin)
        self.mw.coin_selector.update()
        find = self.mw.coin_selector.findText(coin, flags=QtCore.Qt.MatchStartsWith)
        self.mw.coin_selector.setCurrentIndex(find)

        self.change_pair()

    def update_hide_other_filter(self):
        """Set the coinindex_filter QLineEdit to the currently selected pair."""
        if self.mw.hide_pairs.checkState() == 2:
            self.mw.coinindex_filter.setText(self.mw.data.current.coin)

    def set_charts(self, pair):
        try:
            # This is different from the call that sets up the charts; TODO: Unify
            self.mw.chart.setHtml(Webpages.build_chart2(pair, self.mw.cfg_manager.defaultTimeframe))

            url = Webpages.build_cmc(self)
            self.mw.cmc_chart.load(QtCore.QUrl(url))
        except TypeError as e:
            print("DEBUG: chart failed", e)

    def tab_change(self, index):
        """Only show time frame combobox in corner widget when the correct tab
        page is active. (Trade History)."""
        tabname = self.mw.tabsBotLeft.tabText(index)

        if tabname == "Trade History":
            self.mw.cb_history_time.setVisible(True)
        else:
            self.mw.cb_history_time.setVisible(False)

        if tabname == "Open Orders":
            self.mw.btn_cancel_all.setVisible(True)
        else:
            self.mw.btn_cancel_all.setVisible(False)

    def setup_tabs(self):
        """Set tabbed ui elements to default pages."""

        self.mw.ChartTabs.tabBar().setExpanding(False)

        self.mw.ChartTabs.setCurrentIndex(0)
        self.mw.tabsBotLeft.setCurrentIndex(4)
        self.mw.bot_tabs.setCurrentIndex(0)

        self.mw.tabsBotLeft.currentChanged.connect(self.tab_change)
        self.mw.tabsBotLeft.tabBar().setExpanding(False)
        # self.mw.tabsBotLeft.setCornerWidget(self.mw.coin_index_filter)
        # self.mw.ChartTabs.setCornerWidget(self.mw.volume_widget)
        # self.mw.ChartTabs.adjustSize()


    def hide_tabs(self):
        """Hide disable tabs not ready/suitable for the user."""
        self.mw.tabsBotLeft.removeTab(1)
        self.mw.tabsBotLeft.removeTab(0)

        self.mw.ChartTabs.removeTab(8)
        self.mw.ChartTabs.removeTab(7)
        self.mw.ChartTabs.removeTab(4)
        self.mw.ChartTabs.removeTab(3)
        self.mw.ChartTabs.removeTab(1)

        self.mw.bot_tabs.setTabEnabled(1, False)
        self.mw.bot_tabs.setTabEnabled(2, False)
        self.mw.bot_tabs.setTabEnabled(3, False)


    def disable_ui(self):
        """Disable api dependant ui elements."""
        print("DISABLE UI!!")
        # self.mw.bot_tabs.setEnabled(1, False)
        self.mw.limit_pane.setEnabled(False)
        self.mw.websocket_area.setEnabled(False)
        
        self.mw.last_price.setText("")
        self.mw.price_arrow.setText("")
        self.mw.spread_label.setText("")

        self.mw.percent_frame.setVisible(False)
        self.mw.volume_widget.setVisible(False)
        self.mw.volumes_widget.setVisible(False)

        # Fully expand chart
        self.mw.splitter_v.setSizes([0, 0])
        self.mw.splitter_h.setSizes([0, 0])

    # Maybe move this into limit order pane
    def limit_pane_current_values(self):
        """Set pair specific values such as asset names and decimals/single step
        in the limit order pane.
        This is called when the current pair is changed or asset balances change."""

        data = self.mw.data

        coin = data.current.coin
        pair = data.current.pair

        holdings = self.mw.user_data.holdings
        tickers = self.mw.data.pairs

        try:
            self.mw.buy_asset.setText(coin)
            self.mw.sell_asset.setText(coin)

            self.mw.limit_total_btc.setText(str(holdings["BTC"]["free"]) + " BTC")
            self.mw.limit_total_coin.setText(str(holdings[coin]["free"]) + " " + coin)

            self.mw.limit_buy_label.setText("Buy " + coin)
            self.mw.limit_sell_label.setText("Sell " + coin)

            self.mw.limit_buy_input.setDecimals(tickers[pair]["decimals"])
            self.mw.limit_buy_input.setSingleStep(float(tickers[pair]["tickSize"]))

            self.mw.limit_sell_input.setDecimals(tickers[pair]["decimals"])
            self.mw.limit_sell_input.setSingleStep(float(tickers[pair]["tickSize"]))

            self.mw.limit_buy_amount.setDecimals(tickers[pair]["assetDecimals"])
            self.mw.limit_buy_amount.setSingleStep(float(tickers[pair]["minTrade"]))

            self.mw.limit_sell_amount.setDecimals(tickers[pair]["assetDecimals"])
            self.mw.limit_sell_amount.setSingleStep(float(tickers[pair]["minTrade"]))
        except KeyError as e:
            print("livedata values key error", e)

    def setup(self):
        print("NEWEST GUI SETUP")
        # TODO: rename
        """Condensed setup methods required."""
        # call these from api setup or gui
        # self.mw.new_api.api_calls()
        # self.mw.websocket_manager.schedule_websockets()

        # self.mw.gui_manager.schedule_work()

        # move somewhere else as well
        # self.mw.chart.show()

        # setup quote asset box
        icon = QtGui.QIcon(resource_path("images/ico/" + "BTC" + ".svg"))
        self.mw.quote_asset_box.addItem(icon, "BTC")
        self.mw.quote_asset_box.setIconSize(QtCore.QSize(25, 25))