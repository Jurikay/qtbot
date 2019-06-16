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

        self.mw = app.mw

        self.current = Dict()
        self.user = Dict()
        self.stats = Dict()

        self.klines = Dict()

        self.user.start_btc = 0

        self.tickers = dict()
        self.pairs = dict()

        self.btc_price = dict()
        # Hardcoded default
        cfg = app.mw.data
        self.set_current_pair(app.mw.cfg_manager.pair)

        self.current.tickers = dict()
        # todo: load from cfg

        # debug
        self.index_list = list()


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

                # if info["symbol"]set_tickers IFNO == "BNBBTC":
                #     print("", info)

                # Store tickers by pair
                self.tickers[pair] = info
            elif info["symbol"] == "BTCUSDT":
                self.btc_price = info


        # self.ticker_df()

    @staticmethod
    def set_trades(trades):
        pass

    def set_hist(self, history):
        """Receives either a list of recent trades (dicts) or the most recent trade."""
        # TODO: Verify
        # Websocket: Receive single history entry
        if isinstance(history, dict):
            if not isinstance(self.current["history"], list):
                self.current["history"] = list()
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
        """side can be either bids or asks."""
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
        if self.current["history"]:
            df = pd.DataFrame(self.current["history"])
            df.columns = ["maker", "price", "quantity", "time"]
            df = df[["price", "quantity", "time"]]
            # df = df.rename(columns={"price": "Price", "quantity": "Quantity", "time": "Time"})
            df = df.apply(pd.to_numeric, errors="coerce")
            self.current.history_df = df
            return df
    


    def new_index_df(self, progress_callback=None):
        if self.tickers:
            index_data = dict()
            for pair, ticker_data in self.tickers.items():
                if app.mw.historical_data.has_data(pair, "1m"):
                    indicators = app.mw.historical_data.indicators.get(pair, None)
                    if indicators is not None:
                        index_data[pair] = {"symbol": str(ticker_data["symbol"]),
                                            "lastPrice": float(ticker_data["lastPrice"]),
                                            "count": int(ticker_data["count"]),
                                            "1m count": int(indicators["count"][0]),
                                            "5m count": int(indicators["count"][1]),
                                            "15m count": int(indicators["count"][2]),
                                            "30m count": int(indicators["count"][3]),
                                            "1h count": int(indicators["count"][4]),

                                            "1m volume": int(indicators["volume"][0]),
                                            "5m volume": int(indicators["volume"][1]),
                                            "15m volume": int(indicators["volume"][2]),
                                            "30m volume": int(indicators["volume"][3]),
                                            "1h volume": int(indicators["volume"][4])
                                            
                                            }
            self.index_dict = index_data

            df = pd.DataFrame.from_dict(self.mw.data.index_dict)
            df = df.transpose()
            df = df.apply(pd.to_numeric, errors='ignore')
            self.current.new_index_df = df
            return df


    def index_df(self, progress_callback=None):
        """Prepare data for index dataframe. This is not done in the main thread."""
        print("INDEX DF")
        if self.tickers:
            index_list = list()

            for k, v in self.tickers.items():
                indicators = None
                if app.mw.historical_data.has_data(k, "1m"):
                    indicators = app.mw.historical_data.indicators.get(k, None)
                if indicators is None:
                    ind = [0,0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0]
                else:
                    ind = list(indicators.values())
                pair_data_list = list()
                pair_data_list.extend([str(v["symbol"]), float(v["lastPrice"]), int(v["count"]), ind[0], ind[1], ind[2], ind[3], ind[4], ind[5], ind[6], ind[7], ind[8], ind[9], ind[10], ind[11], ind[12], ind[13]])
                index_list.append(pair_data_list)




            self.index_list = index_list
            # df = pd.DataFrame(index_list, columns=["Coin", "last Price", "Count", "5m volume", "15m volume", "30m volume", "1h volume", "5m count", "15m count", "30m count", "1h count"])

            # return df
                # self.current.index_df = df


    def ticker_df(self):
        if self.tickers:
            df = pd.DataFrame(self.tickers)
            # df2 = pd.DataFrame.from_dict(self.tickers)
            # df2 = df2.transpose()
            # df = df[["price", "quantity", "time"]]
            df = df.transpose()
            # df = df[["symbol", "bidPrice", "priceChangePercent", "quoteVolume"]]
            df.to_csv("tickers.csv")

            # df = df[["bidPrice", "priceChangePercent", "quoteVolume"]]
            df = df.reset_index()
            df = df.rename(columns={"index": "Coin", "bidPrice": "Price", "priceChangePercent": "Change", "quoteVolume": "Volume"})
            # df.index.name = "index"
            df = df.apply(pd.to_numeric, errors="ignore")

            # Drop symbol column since it is used as index already
            df = df.drop(['symbol'], axis=1)
            # print(df)
            # df = df.apply(pd.to_numeric, errors="ignore")
            # df = df.rename(columns={"symbol": "Coin", "bidPrice": "Price", "priceChangePercent": "Change", "quoteVolume": "Volume"})
            
            # df = df.reset_index(drop=True)
            
            # print(df)
            # Add a numerical index
            self.current.ticker_df = df

            
            # print(df)
            # df.to_csv("tickers.csv")
            return df