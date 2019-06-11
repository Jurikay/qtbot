# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

import logging
# from PyQt5.QtCore import pyqtSlot
import numpy as np
import pandas as pd

from app.charts import Webpages
from app.helpers import resource_path
from app.elements.gui_scheduler import GuiScheduler
import time

class GuiMgr:

    def __init__(self, mw, tp):
        self.mw = mw
        print("Init new gui mgr")
        self.set_tooltips()
        self.set_timer()
        self.timer_count = 0

        self.scheduler = GuiScheduler(mw, tp)

        # tab stuff
        self.hide_tabs()
        self.setup_tabs()

        self.ticks = 0


    def scheduler_loop(self, progress_callback):
        while True:
            print("SCHEDULER LOOP")
            # do stuff
            self.scheduler.test_indicators()
            time.sleep(1)

    def set_timer(self):
        self.timer = QtCore.QTimer(self.mw)
        self.timer.setInterval(1000)          # Throw event timeout with an interval of 1000 milliseconds
        self.timer.timeout.connect(self.blink)
        self.timer.start()

    # Refactor:
    # Idea: Ticker websocket triggers this instead of QTimer.
    # This would ensure that functions trigger directly after new ticker data has been received.
    def blink(self):
        """Call all periodic ui updates here."""
        try:
            self.scheduler.update()
        except AttributeError as e:
            print("blink error", e)
        # if self.ticks >= 4:
        #     self.scheduler.less_regular_update()
        #     self.ticks = 0
            
        # self.ticks += 1


    # ######## Setup ##########
    def set_tooltips(self):
        print("Setting tooltips")
        self.mw.pb_klines.setToolTip("<span style='color: #f3ba2e'>Historical price data</span> is still being loaded.\nIndicators for all pairs will only be available when done.")

        # TODO: implement/remove
        # self.mw.limit_buy_input.setStatusTip("BUY TOOLTIP")
        # self.mw.limit_buy_input.setWhatsThis("WHAT TEH FUG")
        # print("INPUT:", self.mw.limit_buy_input.value())
    
    def set_api_independant(self):
        """Gui setup that does not rely on any api data."""
        self.hide_placeholders()
        self.mw.version_label.setText("Version: " + "<span style='color: #f3f3f3'>" + self.mw.version + "</span>")
        self.mw.btc_timeframe_selector.currentIndexChanged.connect(self.update_btc_chart)
        self.mw.cfg_remember.stateChanged.connect(self.disable_default_pair_selector)
        self.setup_config_ui()
        self.store_ui_config_values()
        self.set_ui_stat_values()

        self.mw.limit_buy_warning.setVisible(False)
        self.mw.limit_sell_warning.setVisible(False)




    def hide_placeholders(self):
        """Hide ui text elements until their data arrives."""
        self.mw.last_price.setText("")
        self.mw.price_arrow.setText("")
        self.mw.spread_label.setText("")

        self.mw.btc_vol_label.setText("")
        self.mw.btc_low_label.setText("")
        self.mw.btc_high_label.setText("")
        self.mw.btc_price_label.setText("")
        self.mw.btc_percent_label.setText("")

        self.mw.btn_cancel_all.setVisible(False)
        self.mw.cb_history_time.setVisible(False)
        
############################

    def change_pair(self):
        """Change the active pair and call symbol specific methods."""
        print("Change pair")
        data = self.mw.data
        
        current_pair = data.current.pair
        new_pair = self.mw.coin_selector.currentText()

        print("CHANGE_PAIR: from:", current_pair, "to:", new_pair)
        
        if any(new_pair in s for s in self.mw.data.tickers) and new_pair != current_pair:
            print("change pair to:", new_pair)

            data.set_current_pair(new_pair)

            self.set_charts(new_pair)

            self.mw.websocket_manager.stop_sockets()

            if self.mw.cfg_remember.isChecked():
                self.mw.default_pair_label.setText(new_pair)

            logging.info('Change active pair to %s' % new_pair)

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
        print("SET_CHARTS")
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

        self.mw.tabsBotLeft.currentChanged.connect(self.tab_change)
        self.mw.tabsBotLeft.tabBar().setExpanding(False)

        self.mw.ChartTabs.setCurrentIndex(0)
        self.mw.tabsBotLeft.setCurrentIndex(2)
        self.mw.bot_tabs.setCurrentIndex(0)
        # self.mw.tabsBotLeft.setCornerWidget(self.mw.coin_index_filter)
        # self.mw.ChartTabs.setCornerWidget(self.mw.volume_widget)
        # self.mw.ChartTabs.adjustSize()


    def hide_tabs(self):
        """Hide disable tabs not ready/suitable for the user."""
        # self.mw.tabsBotLeft.removeTab(1)
        self.mw.tabsBotLeft.removeTab(0)

        self.mw.ChartTabs.removeTab(8)
        self.mw.ChartTabs.removeTab(7)
        self.mw.ChartTabs.removeTab(4)
        self.mw.ChartTabs.removeTab(3)
        self.mw.ChartTabs.removeTab(1)

        self.mw.bot_tabs.setTabEnabled(1, False)
        self.mw.bot_tabs.setTabEnabled(2, False)
        self.mw.bot_tabs.setTabEnabled(3, False)

    def first_time_setup(self):
        print("FIRST TIME SETUP")
        # self.mw.splitter_h.setSizes([120, 124])
        self.mw.splitter_h.setStretchFactor(1, 1)
        self.mw.api_key_label.setStyleSheet("border: 2px solid #f3ba2e;")
        self.mw.api_secret_label.setStyleSheet("border: 2px solid #f3ba2e;")
        self.mw.bot_tabs.setCurrentIndex(4)
        

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


    def enable_ui(self):
        self.mw.limit_pane.setEnabled(True)
        self.mw.websocket_area.setEnabled(True)
        self.mw.percent_frame.setVisible(True)
        self.mw.volume_widget.setVisible(True)
        self.mw.volumes_widget.setVisible(True)
        # Fully expand chart
        # self.mw.splitter_v.setSizes([0, 0])
        # self.mw.splitter_h.setSizes([0, 0])
        
        # self.first_time_setup()

    def current_pair_ui_values(self):
        """Set corner widget volume values and change values of current pair."""
        pair = self.mw.data.current.pair
        indicators = self.mw.historical_data.indicators[pair]

        indicator_list = list()
        indicator_list.append(indicators.get("1m volume", 0))
        indicator_list.append(indicators.get("5m volume", 0))
        indicator_list.append(indicators.get("15m volume", 0))
        # indicator_list.append(indicators.get("30m volume", 0))
        indicator_list.append(indicators.get("1h volume", 0))

        ui_elements = [self.mw.volume_1m, self.mw.volume_5m, self.mw.volume_15m, self.mw.volume_1h]

    
        for i, ele in enumerate(ui_elements):
            if indicator_list[3] == 0:
                ele.setText("<span style='color: #999;'>" + str(round(indicator_list[i], 4))+ " BTC</span>")
            else:
                ele.setText(str(round(indicator_list[i], 4))+ " BTC")


        # print("current_pair_ui_values:", indicator_list)
        # self.mw.volume_1m.setText(str(round(indicator_list[0], 4))+ " BTC")
        # self.mw.volume_5m.setText(str(round(indicator_list[1], 4))+ " BTC")
        # self.mw.volume_15m.setText(str(round(indicator_list[2], 4))+ " BTC")
        # self.mw.volume_1h.setText(str(round(indicator_list[4], 4))+ " BTC")
        
        # self.mw.volume_1m.text = self.mw.histoircal_data.

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

            # Reset values
            self.mw.limit_buy_input.setValue(0)
            self.mw.limit_sell_input.setValue(0)
            self.mw.limit_buy_amount.setValue(0)
            self.mw.limit_sell_amount.setValue(0)

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
        print("setup config ui")
        
    
    ###################################
    # CONFIG
    ###################################
    def update_btc_chart(self):
        self.mw.btc_chart.setHtml(Webpages.build_chart_btc(self, "BTCUSD", self.mw.cfg_manager.btcTimeframe, self.mw.btc_exchange_selector.currentText()))


    def setup_config_ui(self):
        self.mw.save_config.clicked.connect(self.save_config)
    

    def save_config(self):
        print("save_config")
        config_dict = self.read_ui_config_values()
        print("SAVE CONFIG DICT", config_dict)
        self.mw.cfg_manager.store_config(config_dict)

        if not self.mw.is_connected:
            print("TRY TO CONNECT")
            self.mw.api_manager.init_authentication()
            self.mw.check_connection()

    def save_stats(self):
        """Main public stats method.
        Read current stats from ui and safe to file."""
        stats = self.read_ui_stats_values()
        # self.mw.cfg_manager.stats = stats
        self.mw.cfg_manager.store_stats(stats)
        self.mw.cfg_manager.write_stats()
        # self.write_config()
        # config = configparser.ConfigParser()
        # if os.path.isfile("config.ini"):
        #     config.read('config.ini')

        # self.read_config(config)
        # if not self.mw.is_connected:
        #     print("trying to authenticate")
        #     self.mw.api_manager.in

    def read_ui_stats_values(self):
        """Read values from stats pane ui elements."""
        running = self.scheduler.runtime
        old_total = self.mw.cfg_manager.stats["Stats"]["timerunning"]
        print("RUNNING", running)
        session_time = self.mw.session_running.text()
        total_time = int(running) + int(old_total)

        session_trades = self.mw.session_trades.text()
        total_trades = self.mw.total_trades.text()

        session_bot_trades = self.mw.session_bot_trades.text()
        total_bot_trades = self.mw.total_bot_trades.text()

        session_api_updates = self.mw.session_api_updates.text()
        total_api_updates = self.mw.total_api_updates.text()

        session_explicit_updates = self.mw.session_explicit.text()
        total_explicit_updates = self.mw.total_api_calls.text()
        return {"Stats": {"timerunning": total_time, "exectrades": total_trades, "execbottrades": total_bot_trades, "apiupdates": total_api_updates, "apicalls": total_explicit_updates}}

    def set_ui_stat_values(self):
        """Apply stats values to ui elements."""
        stats = self.mw.cfg_manager.stats["Stats"]
        self.mw.total_running.setText(stats["timerunning"])
        self.mw.total_trades.setText(stats["exectrades"])
        self.mw.total_bot_trades.setText(stats["execbottrades"])
        self.mw.total_api_updates.setText(stats["apiupdates"])
        self.mw.total_api_calls.setText(stats["apicalls"])


    def read_ui_config_values(self):
        """Read values from config pane ui elements.
        Returns a dict in the format configparser expects."""
        print("reading ui config values")
        api_key = self.mw.api_key_label.text()
        api_secret = self.mw.api_secret_label.text()

        remember_pair = self.mw.cfg_remember.isChecked()
        defaultpair = self.mw.default_pair_label.text()
        # copy_price = self.mw.copy_price_box.isChecked()
        # copy_qty = self.mw.copy_qty_box.isChecked()
        percent_texts = self.mw.percent_1.text() + ", " + self.mw.percent_2.text() + ", " + self.mw.percent_3.text() + ", " + self.mw.percent_4.text() + ", " + self.mw.percent_5.text()
        # percent = self.mw.buttonPercentage
        default_timeframe_index = self.mw.default_timeframe_selector.currentIndex()
        btctimeframe_index = self.mw.btc_timeframe_selector.currentIndex()
        timeframes = self.mw.cfg_manager.timeframes
        default_timeframe = timeframes[default_timeframe_index]
        btctimeframe = timeframes[btctimeframe_index]
        uiscale = self.mw.sb_uiscale.value()


        btcexchange = self.mw.btc_exchange_selector.currentText()
        return {"CONFIG": {"defaultpair": defaultpair, "rememberdefault": remember_pair, "buttonpercentages": percent_texts, 
                "defaulttimeframe": default_timeframe, "btctimeframe": btctimeframe, "btcexchange": btcexchange,
                "copyprice": True, "copyquantity": False, "uiupdates": 1, "uiscale": uiscale},
                "API": {"key": api_key, "secret": api_secret}}  # remove these

    def store_ui_config_values(self):
        """Reflect loaded configuration values in the ui."""
        config = self.mw.cfg_manager.config["CONFIG"]
        api = self.mw.cfg_manager.config["API"]

        check_state = {"True": 2, "False": 0}

        self.mw.api_key_label.setText(api["key"])
        self.mw.api_secret_label.setText(api["secret"])

        self.mw.default_pair_label.setText(config["defaultpair"])
        self.mw.cfg_remember.setCheckState(check_state[config["rememberdefault"]])

        raw_timeframes = self.mw.cfg_manager.timeframes
        for i, tf in enumerate(raw_timeframes):
            if tf == int(config["defaulttimeframe"]):
                self.mw.default_timeframe_selector.setCurrentIndex(i)
            if tf == int(config["btctimeframe"]):
                self.mw.btc_timeframe_selector.setCurrentIndex(i)


        btn_texts = config["buttonpercentages"].split(", ")
        percent_buttons = [self.mw.percent_1, self.mw.percent_2, self.mw.percent_3, self.mw.percent_4, self.mw.percent_5]
        for i, btn in enumerate(percent_buttons):
            btn.setText(btn_texts[i])

    def disable_default_pair_selector(self, state):
        if state == 2:
            self.mw.default_pair_label.setEnabled(False)
            self.mw.default_pair_label.setStyleSheet("color: #999;")
            self.mw.default_pair_label.setText(self.mw.data.current.pair)
        else:
            self.mw.default_pair_label.setEnabled(True)
            self.mw.default_pair_label.setStyleSheet("color: #f3f3f3;")

    