# from collections import defaultdict
from addict import Dict
import app
import numpy as np
import tulipy as ti
import pandas as pd
import dateparser
from functools import partial
from app.workers import Worker
import time

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
        self.indicators = Dict()
        self.websocket_klines = Dict()
        self.mw = app.mw
        self.threadpool = app.threadpool
    
    def has_data(self, pair, timeframe):
        """Return true if a pair has evaluable data."""
        return len(self.klines[pair][timeframe].items()) > 10

    def get_hist_values(self, pair):
        """Calculate historical values that are not result of an indicator by iterating over 1m candles."""
        klines = self.klines[pair]["1m"]
        last_hour = list(klines.items())[-60:]
        last_hour.reverse()

        # High and low price are lists of lists.
        # The respective highest and lowest price is obtained after the loop.
        high_price = list()
        low_price = list()
        close_price = list()
        volumes = list()

        volume = [0, 0, 0, 0, 0]
        count = [0, 0, 0, 0, 0]


        for i, element in enumerate(last_hour):

            if i == 0:
                volume[0] = float(element[1]["quote_asset_volume"])
                count[0] = int(element[1]["number_of_trades"])

            if i < 5:

                volume[1] += float(element[1]["quote_asset_volume"])
                count[1] += int(element[1]["number_of_trades"])
            if i < 15:

                volume[2] += float(element[1]["quote_asset_volume"])
                count[2] += int(element[1]["number_of_trades"])
            if i < 30:

                volume[3] += float(element[1]["quote_asset_volume"])
                count[3] += int(element[1]["number_of_trades"])

            volume[4] += float(element[1]["quote_asset_volume"])
            count[4] += int(element[1]["number_of_trades"])

            high_price.append(float(element[1]["high_price"]))
            low_price.append(float(element[1]["low_price"]))
            close_price.append(float(element[1]["close_price"]))
            volumes.append(float(element[1]["quote_asset_volume"]))

        mean_volume = list()
        min_price = list()
        max_price = list()
        difference = list()

        intervals = [1, 5, 15, 30, 60]
        for i, interval in enumerate(intervals):
            # print("ASSIGN INTERVALS", i)
            try:
                mean_volume.append((volume[interval]) / len(volumes[:interval]))
            except IndexError:
                mean_volume.append(volumes[0])
            min_price.append(min(low_price[:interval]))
            max_price.append(max(high_price[:interval]))
            difference.append(((close_price[0] / close_price[interval -1]) - 1) * 100)
        
        return {"volume": volume, "count": count, "min": min_price, "max": max_price, "difference": difference, "mean_volume": mean_volume}
        # mean_volume[0] = volumes[:1]
        # mean_volume[1] = sum(volumes[:5]) / len(volumes[:5])
        # mean_volume[2] = sum(volumes[:15]) / len(volumes[:15])
        # mean_volume[3] = sum(volumes[:30]) / len(volumes[:30])
        # mean_volume[4] = sum(volumes) / len(volumes)

        
        # min_price[0] = low_price[:1]
        # min_price[1] = min(low_price[:5])
        # min_price[2] = min(low_price[:15])
        # min_price[3] = min(low_price[:30])
        # min_price[4] = min(low_price)


        # max_price[0] = high_price[:1]
        # max_price[1] = max(high_price[:5])
        # max_price[2] = max(high_price[:15])
        # max_price[3] = max(high_price[:30])
        # max_price[4] = max(high_price)

        # difference[0] = ((close_price[0] / close_price[1]) - 1) * 100
        # difference[1] = ((close_price[0] / close_price[4]) - 1) * 100
        # difference[2] = ((close_price[0] / close_price[14]) - 1) * 100
        # difference[3] = ((close_price[0] / close_price[29]) - 1) * 100
        # difference[4] = ((close_price[0] / close_price[-1]) - 1) * 100

        # values = [volume[0], volume[1], volume[2], volume[3], volume[4], count[0], count[1], count[2], count[3], count[4], max15, max1h, diff15, diff60]
        # return values


    def get_hist_volume(self, pair, minutes):
        # print("GET HIST VOL", pair)
        klines = self.klines[pair]["1m"]
        els = list(klines.items())
        test = els[-minutes:]
        volume = 0
        for ele in test:
            # print("+= ", ele[1]["quote_asset_volume"])
            # print("ELE", ele)
            volume += float(ele[1]["quote_asset_volume"])
        return volume
        # test2 = els[0][1]["volume"]
        # nparray = np.array(klines)
        # res = np.array([list(item.values()) for item in klines.values()])
        # import pdb; pdb.set_trace()
        # print("KLINES", volume)

    def update_kline(self, kline):
        """Update a single kline after a websocket update has occured."""
        pass
    
    def set_klines(self, klines):
        """Receive a list of lists of kline values and store them as dict."""
        pass


    def kline_list_to_dict(self, symbol, timeframe, kline_list):
        """Convert kline values in list form to a better readable dict."""
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

        # if not isinstance(self.klines[symbol][timeframe][kline_list[0]], dict):
        #     self.klines[symbol][timeframe][kline_list[0]] = kline_values
        # else:
        #     print("ALREADY HAS VALUES", self.klines[symbol][timeframe][kline_list[0]])


    def set_websocket_klines(self, klines):
        """Store kline values received from websocket callback."""

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
                    # "B": "WEBSOCKET"
                
                    # "x": "bar_is_final",
                    # "B": "ignore"}
                    }
        pair = klines["s"]
        interval = klines["i"]
        open_time = klines["t"]

        output = dict()

        for k, v in mapping.items():
            output[v] = klines[k]

        # Store kline values in dict with open_time as key
        self.klines[pair][interval][open_time] = output

        if interval == "1m":
            if self.has_data(pair, "1m"):
                 self.indicators[pair] = self.get_hist_values(pair)



        # if not isinstance(self.klines[pair][interval][open_time], dict):
        #     self.klines[pair][interval] = output
        # else:
        #     print("KLINE DICT NOT YET PRESENT")

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
        # bbandsdf.to_csv("bbands.csv")
        return bbandsdf
       
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

    ###################################################
    # indicators loop
    ###################################################

    def kline_api_loop(self, dr, progress_callback):
        """Loop over all pairs and fetch 1m kline values."""

        print("STARTING INDICATOR LOOP")

        thread_count = self.threadpool.maxThreadCount()
        desired_count = thread_count - 2

        pairs = list(self.mw.data.tickers.keys())
        print("PAIRS", pairs)
        start_length = len(pairs)
        progress_callback.emit({"start": len(pairs)})
        while pairs:
            while self.threadpool.activeThreadCount() < desired_count:
                pair = pairs.pop(0)
                print("PROCESSING", pair, "rest len:", len(pairs))
                # self.mw.api_manager.api_klines(pair, dr)
                worker = Worker(partial(self.mw.api_manager.api_klines, [pair, dr]))
                # worker.signals.progress.connect(self.loop_callback)
                self.threadpool.start(worker)
                progress_callback.emit(start_length - len(pairs))

                # time.sleep(0.1)

        print("INDICATOR LOOP DONE")
    
    # def loop_callback(self, msg):
    #     print("LOOP CALLBACK", msg)
    #     for k, v in msg.items():
    #         print("KV", k, v)
    
    def calculate_indicators(self, progress_callback):
        """Loop over all pairs and calculate indicator values if enough data is present."""
        pairs = list(self.mw.data.tickers.keys())
        while True:
            print("BEGINNGING INDICATOR LOOP")
            for pair in pairs:
                if self.has_data(pair, "1m"):
                    print("PAIR", pair, "has data!")
                    self.pair_indicators(self.klines[pair]["1m"])
            
            print("SLEEPING")
            time.sleep(1)


    def pad_left(self, x, n, pad=np.nan):
        return np.pad(x, (n - x.size, 0), 'constant', constant_values=(pad,))


    def pair_indicators(self, dataf):
        print("CALCULATING PAIR INDICATORS")
        simple = dict()
        closel = list()
        timel = list()
        for k, v in dataf.items():
            simple[k] = v["close_price"]
            closel.append(float(v["close_price"]))
            timel.append(int(k))


        time = np.array(timel)
        close = np.array(closel)

        bbands = ti.bbands(close, period=20, stddev=2)
        macd = ti.macd(close, 12, 26, 9)

        ohlc = dict()
        ohlc["close"] = close
        ohlc["time"] = time
        ohlc["bbandsl"] = self.pad_left(bbands[0], ohlc["time"].size)
        ohlc["bbandsm"] = self.pad_left(bbands[1], ohlc["time"].size)
        ohlc["bbandsh"] = self.pad_left(bbands[2], ohlc["time"].size)
        ohlc["macd1"] = self.pad_left(macd[0], ohlc["time"].size)
        ohlc["macd2"] = self.pad_left(macd[1], ohlc["time"].size)
        ohlc["macd3"] = self.pad_left(macd[2], ohlc["time"].size)

        # if pair == self.mw.data.current.pair:
        #     result = {"interval": interval, "pair": pair, "time": ohlc["time"][-1], "close": ohlc["close"][-1], "bbandsl": ohlc["bbandsl"][-1], "bbandsm": ohlc["bbandsm"][-1], 
        #     "bbandsh": ohlc["bbandsh"][-1]}
        #     progress_callback.emit(result)


    def progressbar_callback(self, progress):
        """Set max/ advance progress bar callback.""" 
        if isinstance(progress, dict):
            self.mw.pb_klines.setMaximum(progress["start"])
        else:
            self.mw.pb_klines.setValue(progress)

            # Get progress percent
            # percent = (self.mw.pb_klines.value() - self.mw.pb_klines.minimum()) / self.mw.pb_klines.maximum() - self.mw.pb_klines.minimum()
            # print("PERCENT", percent)
            # if percent >= 0.4:
            #     self.mw.pb_klines.setStyleSheet("color: 'black';")
            if self.mw.pb_klines.value() == self.mw.pb_klines.maximum():
                self.mw.pb_klines.hide()
            
