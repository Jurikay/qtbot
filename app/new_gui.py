# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


class GuiMgr:

    def __init__(self, mw):
        self.mw = mw
        print("Init new gui mgr")
        # super().__init__(mw)
        self.set_tooltips()


    # ######## Setup ##########
    def set_tooltips(self):
        print("Setting tooltips")
        self.mw.limit_buy_input.setToolTip = "BUY TOOLTIP" 