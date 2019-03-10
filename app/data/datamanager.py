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
        print("Init new datamanager")
        self.current = Dict()
        self.tickers = dict()
        self.pairs = dict()

        # Hardcoded default
        self.current.symbol = "ETHBTC"
        self.current.tickers = dict()

    def set_thread(self, callback):
        print("CALLBACK:", callback)

    def set_depth(self, depth):
        """Receives current bids and asks of selected pair."""
        self.current["orderbook"] = Dict(depth)
        self.depth_df("bids")
        self.depth_df("asks")
        
    
    def set_tickers(self, ticker):
        # Iterate over list of tickers
        for info in ticker:
            # Filter only BTC pairs; TODO: Evaluate other currency pairs too
            if info["symbol"][-3:] == "BTC":
                # coin = info["symbol"][:-3]
                pair = info["symbol"]

                # Store tickers by pair
                # temp_tickers[pair] = info
                self.tickers[pair] = info
    
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
            self.current["history"] = list(reversed(history))
        
        self.history_df()

    def set_info(self, info, products):
    
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
        self.pairs = pair_info

    # ############### DATAFRAMES ######################
    def depth_df(self, side):
        """(Re)creates two pandas dataframes: One for asks and one for bids."""
        # print(self.current.orderbook[side])
        # for side in sides:
        df = pd.DataFrame(self.current.orderbook[side])
        df.columns = ["Price", "Amount", "Total"]

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
        df = pd.DataFrame(self.tickers)
        # df = df[["price", "quantity", "time"]]
        df = df.transpose()
        df = df[["symbol", "bidPrice", "priceChangePercent", "quoteVolume"]]
        # print(df)
        df = df.apply(pd.to_numeric, errors="ignore")
        df = df.rename(columns={"symbol": "Pair", "bidPrice": "Price", "priceChangePercent": "Chnage", "quoteVolume": "Volume"})
        self.current.ticker_df = df
        # print(df)
        return df