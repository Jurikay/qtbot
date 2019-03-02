# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import pandas as pd
from addict import Dict


class DataManager():
    """Stores and transforms data received from api calls and websockets

    Uses addict dictionary data structure.
    https://github.com/mewwts/addict
    """
    def __init__(self):
        self.current = Dict()

    @staticmethod
    def set_depth(depth):
        """Receive depth data either from api call or from websocket."""
        pass
    
    @staticmethod
    def set_tickers(tickers):
        pass
    
    @staticmethod
    def set_trades(trades):
        pass