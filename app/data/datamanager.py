# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import pandas as pd
from addict import Dict
import app

class DataManager():
    """Stores and transforms general api data received from api calls and websockets

    Uses addict dictionary data structure.
    https://github.com/mewwts/addict
    """
    def __init__(self):
        print("Init new datamanager")
        self.current = Dict()
        self.user = Dict()
        self.stats = Dict()
        
        self.tickers = dict()
        self.pairs = dict()

        self.btc_price = dict()
        # Hardcoded default
        cfg = app.mw.data
        self.set_current_pair(app.mw.cfg_manager.pair)

        self.current.tickers = dict()
        # todo: load from cfg


    def set_depth(self, depth, progress_callback=None):
        """Receives current bids and asks of selected pair."""
        self.current["orderbook"] = Dict(depth)
        self.depth_df("bids")
        self.depth_df("asks")
        
    
    def set_tickers(self, ticker):
        # Iterate over list of tickers
        for info in ticker:
            # Filter only BTC pairs; TODO: Evaluate other currency pairs too
            if info["symbol"][-3:] == "BTC" and float(info["lastPrice"]) > 0.00000000 and not info["askPrice"] == "0.00000000":
                # coin = info["symbol"][:-3]
                pair = info["symbol"]

                if info["symbol"] == "PHXBTC":
                    print(info)
                # Store tickers by pair
                # temp_tickers[pair] = info
                self.tickers[pair] = info
            elif info["symbol"] == "BTCUSDT":
                self.btc_price = info
        self.ticker_df()

    @staticmethod
    def set_trades(trades):
        pass

    def set_hist(self, history):
        """Receives either a list of recent trades (dicts) or the most recent trade."""
        # TODO: Verify
        # Websocket: Receive single history entry
        if isinstance(history, dict):
            self.current["history"].insert(0, {"price": history["p"], "quantity": history["q"], "maker": bool(history["m"]), "time": history["T"]})

            # Keep history size consistent
            if len(self.current["history"]) > 50:
                self.current["history"].pop()

        # Api call: Receive complete list of history entries; Store reversed list
        elif isinstance(history, list):
            print("STORE LIST HISTORY")
            self.current["history"] = list(reversed(history))
        
        self.history_df()

    def set_info(self, products, info):
    
        pair_info = Dict()

        # Iterate over products dict
        for key, value in products.items():

            # TODO: Replace hardcoded BTC; Make other pairs available
            # Filter active pairs of desired asset
            if value["quoteAsset"] == "BTC" and float(value["volume"]) > 0 and value["status"] == "TRADING":
                pair_info[key] = value

                # Iterate over info dict and add calculated filter information.
                for sfilter, filterval in info[key].items():
                    pair_info[key][sfilter] = filterval

        # Store 'static' info in self.pairs
        print("SETTING PAIR INFO")
        self.pairs = pair_info

    def set_current_pair(self, pair):
        print("DATA: SETTING CURERNT PAIR", pair)
        self.current.pair = pair
        self.current.coin = pair[:-3]

    # ############### DATAFRAMES ######################
    def depth_df(self, side):
        """(Re)creates two pandas dataframes: One for asks and one for bids."""
        # print(self.current.orderbook[side])
        # for side in sides:
        df = pd.DataFrame(self.current.orderbook[side])
        
        df.columns = ["Price", "Amount"]

        # Convert to numerical values
        df = df.apply(pd.to_numeric, errors='coerce')

        # Calculate total
        total = df.Price * df.Amount
        df["Total"] = total
        
        df['#'] = df.index + 1
        df = df[["#", "Price", "Amount", "Total"]]

        # Reverse asks
        if side == "asks":
            df = df.reindex(index=df.index[::-1])
        
        self.current.depth_df[side] = df
        return df

    def history_df(self):
        df = pd.DataFrame(self.current["history"])
        df.columns = ["maker", "price", "quantity", "time"]
        df = df[["price", "quantity", "time"]]
        # df = df.rename(columns={"price": "Price", "quantity": "Quantity", "time": "Time"})
        df = df.apply(pd.to_numeric, errors="coerce")
        self.current.history_df = df
        return df
    
    def ticker_df(self):
        if self.tickers:
            df = pd.DataFrame(self.tickers)
            # df = df[["price", "quantity", "time"]]
            df = df.transpose()
            # df = df[["symbol", "bidPrice", "priceChangePercent", "quoteVolume"]]
            
            df = df[["bidPrice", "priceChangePercent", "quoteVolume"]]
            df = df.reset_index()
            df = df.rename(columns={"index": "Coin", "bidPrice": "Price", "priceChangePercent": "Change", "quoteVolume": "Volume"})
            df.index.name = "index"
            df = df.apply(pd.to_numeric, errors="ignore")

            # print(df)
            # df = df.apply(pd.to_numeric, errors="ignore")
            # df = df.rename(columns={"symbol": "Coin", "bidPrice": "Price", "priceChangePercent": "Change", "quoteVolume": "Volume"})
            
            df = df.reset_index(drop=True)
            
            # print(df)
            # Add a numerical index
            self.current.ticker_df = df
            # print(df)
            return df