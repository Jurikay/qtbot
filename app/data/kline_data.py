# from collections import defaultdict
from addict import Dict
import app
import numpy as np
import tulipy as ti
import pandas as pd


import PyQt5.QtCore as QtCore

class HistoricalData(QtCore.QObject):
    def __init__(self, parent=None):
        """Klines are stored and are accessible in the following fashion:

        klimes = {
            "BNBBTC": {
                "1m": {
                    15512312312: {
                        "open": "0.0034531",
                        "low": "0.0031123",
                        "volume": "123434",
                    }
                }
            }
        }
        """

        super().__init__(parent=parent)
        self.klines = Dict()
        self.websocket_klines = Dict()
        self.mw = app.mw
    
    def has_data(self, pair, timeframe):
        """Return true if a pair has evaluable data."""
        return len(self.klines[pair][timeframe].items()) > 10

    def update_kline(self, kline):
        """Update a single kline after a websocket update has occured."""
        pass
    
    def set_klines(self, klines):
        """Receive a list of lists of kline values and store them as dict."""
        pass


    def kline_list_to_dict(self, symbol, timeframe, kline_list):
        """Convert kline values in list form to a more readable dict."""
        kline_values = {"open_time": kline_list[0],
                        "open_price": kline_list[1],
                        "high_price": kline_list[2],
                        "low_price": kline_list[3],
                        "close_price": kline_list[4],
                        "volume": kline_list[5],
                        "close_time": kline_list[6],
                        "quote_asset_volume": kline_list[7],
                        "number_of_trades": kline_list[8],
                        "taker_buy_asset_volume": kline_list[9],
                        "taker_buy_quote_asset_volume": kline_list[10],}

        # print("ADDING KLINE DATA TO DICT")
        self.klines[symbol][timeframe][kline_list[0]] = kline_values


    def set_websocket_klines(self, klines):
        """Store kline values received from api call."""
        # print("WEBSOCKET KLINES", klines)

        # Map shortended websocket dict keys to full words
        mapping = {"t": "open_time",
                   "T": "close_time",
                   "o": "open_price",
                #    "s": "symbol",
                #    "i": "interval",
                #    "f": "first_trade_id",
                #    "L": "last_trade_id",
                   "c": "close_price",
                   "h": "high_price",
                   "l": "low_price",
                   "v": "volume",
                   "n": "number_of_trades",
                   "q": "quote_asset_volume",
                   "V": "taker_buy_asset_volume",
                   "Q": "taker_buy_quote_asset_volume",
                #    "B": "WEBSOCKET"
                   }
                #    "x": "bar_is_final",
                #    "B": "ignore"}

        pair = klines["s"]
        interval = klines["i"]
        open_time = klines["t"]

        output = dict()

        for k, v in mapping.items():
            output[v] = klines[k]

        # for key, value in klines.items():
        #     output[mapping[key]] = value

        self.klines[pair][interval][open_time] = output

    def klines_to_csv(self):
        """Store kline values in csv file."""
        pass



    ############ TULIPY #############
    @staticmethod
    def print_info(indicator):
        print("Type:", indicator.type)
        print("Full Name:", indicator.full_name)
        print("Inputs:", indicator.inputs)
        print("Options:", indicator.options)
        print("Outputs:", indicator.outputs)

    def debug_tulipy(self):
        print("DEBUG TULIPY")
        self.print_info(ti.bbands)


    def test_indicators(self):
        nano_close_1m = self.mw.historical_data.klines["NANOBTC"]["1m"]
        # df = pd.DataFrame(nano_close_1m)
        df = pd.DataFrame.from_dict(nano_close_1m)
        df = df.apply(pd.to_numeric, errors='coerce')
        df = df.transpose()

        # better
        close = df.close_price.values.flatten()
        bbands = ti.bbands(close, period=5, stddev=2)
        print("bbands", bbands)
        bbandsdf = pd.DataFrame(bbands)
        bbandsdf = bbandsdf.transpose()
        bbandsdf.columns = ["lower band", "middle band", "upper band"]
        bbandsdf.to_csv("bbands.csv")
        # somewhat working
        # print("DF!!!!", df)
        # df = df.apply(pd.to_numeric, errors='coerce')

        # df = df.transpose()
        # df = df["close_price"]
        # df2 = df.values.flatten()
        # df2 = df2.copy(order='close_price')
        # bbands = ti.bbands(df2, period=5, stddev=2)
        # bbdf = pd.DataFrame(bbands)
        # concat = pd.concat([df, bbdf])
        # print("CONCAT", concat)
        # concat.to_csv("bbands.csv")


    def set_value(self, coin, tf, time, key, value):
        self.klines[coin][tf][time] = {key: value}
# multiplex socket:
# conn_key = bm.start_multiplex_socket(['bnbbtc@kline', 'neobtc@kline'], process_m_message)
