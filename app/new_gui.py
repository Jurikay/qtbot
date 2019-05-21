# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
import PyQt5.QtCore as QtCore
# from PyQt5.QtCore import pyqtSlot
import numpy as np
import pandas as pd

from app.charts import Webpages
from app.gui import logging


class GuiMgr:

    def __init__(self, mw):
        self.mw = mw
        print("Init new gui mgr")
        # super().__init__(mw)
        self.set_tooltips()
        self.set_timer()
        self.timer_count = 0

        self.mw.coin_selector.update()
        self.set_default_tabs()

    def set_timer(self):
        self.timer= QtCore.QTimer(self.mw)
        self.timer.setInterval(250)          # Throw event timeout with an interval of 1000 milliseconds
        self.timer.timeout.connect(self.blink)
        self.timer.start()

    # Refactor
    def blink(self):
        # try:
        self.timer_count += 1
        df1 = self.mw.tradeTable.df
        df2 = self.mw.data.current.history_df
        if isinstance(df1, pd.DataFrame) and isinstance(df2, pd.DataFrame):
            if not np.allclose(df1, df2):
                self.mw.tradeTable.update()
                self.mw.live_data.new_last_price()
        
        if self.timer_count >= 4:
            if self.mw.is_connected:
                self.mw.data.ticker_df()
                self.mw.coin_selector.update()
            self.timer_count = 0
            # if df1 != df2:
            #     print("UNEQ DF")
            # else:
            #     print("EQ DF")
        # except Exception as e:
        #     print("ERROR:", e)


    # ######## Setup ##########
    def set_tooltips(self):
        print("Setting tooltips")
        # self.mw.limit_buy_input.setStatusTip("BUY TOOLTIP")
        # self.mw.limit_buy_input.setWhatsThis("WHAT TEH FUG")
        print("INPUT:", self.mw.limit_buy_input.value())
    
    def set_api_dependant(self):
        print("Setting api dependant gui values")
        self.mw.coin_selector.update()


############################

    def change_pair(self):
        """Change the active pair and call symbol specific methods."""
        data = self.mw.data
        
        current_pair = data.current.pair
        new_pair = self.mw.coin_selector.currentText()

        if any(new_pair in s for s in self.mw.tickers) and new_pair != current_pair:
            print("inside if", new_pair)

            data.set_current_pair(new_pair)

            self.set_charts(new_pair)

            self.mw.websocket_manager.stop_sockets()

            logging.info('Switching to %s' % new_pair)

            self.limit_pane_current_values()

            # new 'initial data'
            self.mw.new_api.threaded_pair_update()
            self.mw.websocket_manager.websockets_symbol()
            
            # self.mw.api_manager.api_calls()


            # new
            self.mw.trade_history_view.update()

    # TODO: Call this after loading default pair from config
    def change_to(self, coin):
        print("Change_to:", coin)

        find = self.mw.coin_selector.findText(coin, flags=QtCore.Qt.MatchStartsWith)
        self.mw.coin_selector.setCurrentIndex(find)

        self.change_pair()

    def set_charts(self, pair):
        # This is different from the call that sets up the charts; TODO: Unify
        self.mw.chart.setHtml(Webpages.build_chart2(pair, self.mw.cfg_manager.defaultTimeframe))

        url = Webpages.build_cmc(self)
        self.mw.cmc_chart.load(QtCore.QUrl(url))


    def set_default_tabs(self):
        """Set tabbed ui elements to default pages."""

        self.mw.ChartTabs.setCurrentIndex(0)
        self.mw.tabsBotLeft.setCurrentIndex(4)
        self.mw.bot_tabs.setCurrentIndex(0)

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

        self.mw.limit_sell_amount.setDecimals(tickers[pair]["assetDecimals"]+1)
        self.mw.limit_sell_amount.setSingleStep(float(tickers[pair]["minTrade"])/100)
