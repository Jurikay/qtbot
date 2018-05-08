# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


def goto_pair(self, pair):
    if "BTC" in pair:
        coin = pair.replace("BTC", "")
    else:
        coin = pair

    self.mw.gui_manager.change_to(coin)
