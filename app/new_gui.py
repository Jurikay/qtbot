# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
import PyQt5.QtCore as QtCore
from PyQt5.QtCore import pyqtSlot
import numpy as np

class GuiMgr:

    def __init__(self, mw):
        self.mw = mw
        print("Init new gui mgr")
        # super().__init__(mw)
        self.set_tooltips()
        self.set_timer()
        self.timer_count = 0


    def set_timer(self):
        self.timer= QtCore.QTimer(self.mw)
        self.timer.setInterval(250)          # Throw event timeout with an interval of 1000 milliseconds
        self.timer.timeout.connect(self.blink)
        self.timer.start()

    def blink(self):
        # try:
        self.timer_count += 1
        df1 = self.mw.tradeTable.df
        df2 = self.mw.data.current.history_df
        if not np.allclose(df1,df2):
            self.mw.tradeTable.update()
            self.mw.live_data.new_last_price()
        
        if self.timer_count >= 4:
            ticker_df = self.mw.data.ticker_df()
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