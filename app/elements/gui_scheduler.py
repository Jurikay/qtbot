# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
import time
from datetime import timedelta
from PyQt5 import QtCore
import app
from app.colors import Colors
import logging
import dateparser
import pandas as pd

from app.workers import Worker
import tulipy as ti
import pdb
import timeit
from functools import partial
import numpy as np
"""Collection of methods that are called periodically
to update gui values."""


class GuiScheduler:

    def __init__(self, mw, tp):
        self.mw = mw
        # self.threadpool = tp

        self.runtime = 0
        self.timer_count = 0
        self.last_btc_price = 0
        self.update_count = 0
        self.no_updates = 0
        self.threadpool = tp

        self.klines_started = False
    

    def less_regular_update(self):
        """This is not called every second but every 5 seconds."""
        print("LESS REGULAR UPDATE")
        worker_indicators = Worker(self.mw.historical_data.calculate_indicators)
        self.threadpool.start(worker_indicators)


    def update(self):
        """Main public method; Is called periodically;
        Calls all other methods."""
        self.runtime += 1
        self.mw.data.stats.runtime = self.runtime
        self.update_stats()

        # debug
        print("current thread count:", self.mw.threadpool.activeThreadCount())

        if self.mw.is_connected:
            # debug
            
            self.one_second_update()

            self.percent_changes()
            self.check_websocket()
            
            self.new_gui_blink()

            self.mw.gui_mgr.current_pair_ui_values()
            # self.periodic_thread()
            # worker = Worker(self.test_indicators)
            # self.threadpool.start(worker)

            # df = pd.DataFrame(self.mw.historical_data.klines["NANOBTC"]["1m"])
            # df = df.transpose()
            if self.mw.threadpool.activeThreadCount() == 0 and not self.klines_started:
                # self.mw.historical_data.indicator_loop()
                self.klines_started = True
                dr = dateparser.parse("2 days, ago UTC")
                worker_i = Worker(partial(self.mw.historical_data.kline_api_loop, dr))
                worker_i.signals.progress.connect(self.mw.historical_data.progressbar_callback)
                self.threadpool.start(worker_i)

                # too heavy
                # worker_indicators = Worker(self.mw.historical_data.calculate_indicators)
                # self.threadpool.start(worker_indicators)

            # TEST
            worker = Worker(self.mw.data.new_index_df)
            # print("CURRENT INDEX",  self.mw.tabsBotLeft.currentIndex())
            if self.mw.tabsBotLeft.currentIndex() == 0:

                worker.signals.finished.connect(self.mw.index_view.update)
            self.threadpool.start(worker)

                
            # if self.mw.threadpool.activeThreadCount() == 0 and not self.klines_started:
            #     print("STARTING SCHEDULER")
            #     self.klines_started = True
            #     self.mw.new_api.start_kline_procedure()

            # if self.mw.threadpool.activeThreadCount() <= 6:
            #     worker0 = Worker(self.test_indicators)
            #     worker0.signals.progress.connect(self.calc_callback)
            #     self.threadpool.start(worker0)
          
          
            # try:
            #     df.to_csv("klines.csv")
            # except PermissionError as e:
            #     print("cannot write csv :(", e)

    def periodic_thread(self):
        """Call methods periodically in a separate thread."""
        worker = Worker(self.test_indicators)
        worker.signals.finished.connect(self.calc_callback)
        self.threadpool.start(worker)

    def calculations(self, progress_callback):
        """This is not executed in the main thread."""
        print("CALCULATIONS")
        time.sleep(1)
        nano_1m = self.mw.historical_data.has_data("NANOBTC", "1m")
        # wabi_1m = self.mw.historical_data.has_data("WABIBTC", "1m")

        if nano_1m:
            bbandsdf = self.test_indicators()
            progress_callback.emit(bbandsdf)



    def pad_left(self, x, n, pad=np.nan):
        return np.pad(x, (n - x.size, 0), 'constant', constant_values=(pad,))

    def test_indicators(self, progress_callback):
        """Called once per second."""
        print("START test_indicators")
        # pair = self.mw.data.current.pair
        interval = "1m"
        for pair in self.mw.data.tickers.keys():
            
            if self.mw.historical_data.has_data(pair, interval):
                dataf = self.mw.historical_data.klines[pair][interval]
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

                # pd.options.display.float_format = '{:,.7f}'.format

                # Dataframe version; too expansive for every pair once a second.
                # ohlc = pd.DataFrame(time, columns=["time"])
                # ohlc["close"] = close
                # ohlc["bbandsl"] = self.pad_left(bbands[0], ohlc.time.size)
                # ohlc["bbandsm"] = self.pad_left(bbands[1], ohlc.time.size)
                # ohlc["bbandsh"] = self.pad_left(bbands[2], ohlc.time.size)
                # ohlc["macd1"] = self.pad_left(macd[0], ohlc.time.size)
                # ohlc["macd2"] = self.pad_left(macd[1], ohlc.time.size)
                # ohlc["macd3"] = self.pad_left(macd[2], ohlc.time.size)
                # ohlc["time"] = pd.to_datetime(ohlc["time"], unit="ms", utc=True)
                ohlc = dict()
                ohlc["close"] = close
                ohlc["time"] = time
                ohlc["bbandsl"] = self.pad_left(bbands[0], ohlc["time"].size)
                ohlc["bbandsm"] = self.pad_left(bbands[1], ohlc["time"].size)
                ohlc["bbandsh"] = self.pad_left(bbands[2], ohlc["time"].size)
                ohlc["macd1"] = self.pad_left(macd[0], ohlc["time"].size)
                ohlc["macd2"] = self.pad_left(macd[1], ohlc["time"].size)
                ohlc["macd3"] = self.pad_left(macd[2], ohlc["time"].size)
                

                # ohlc["close"] = ohlc["close"] / 10000
                # ohlc["bbandsl"] = ohlc["bbandsl"] / 10000
                # ohlc["bbandsm"] = ohlc["bbandsm"] / 10000
                # ohlc["bbandsh"] = ohlc["bbandsh"] / 10000
                # ohlc["macd1"] = ohlc["macd1"] / 10000
                # ohlc["macd2"] = ohlc["macd2"] / 10000
                # ohlc["macd3"] = ohlc["macd3"] / 10000

                if pair == self.mw.data.current.pair:
                    result = {"interval": interval, "pair": pair, "time": ohlc["time"][-1], "close": ohlc["close"][-1], "bbandsl": ohlc["bbandsl"][-1], "bbandsm": ohlc["bbandsm"][-1], 
                    "bbandsh": ohlc["bbandsh"][-1]}
                    progress_callback.emit(result)

            # ohlc.to_csv("indicators.csv")
            # bbandsdf = pd.DataFrame(bbands)
            # bbandsdf = bbandsdf.transpose()
            # bbandsdf.columns = ["lower band", "middle band", "upper band"]
        # else:
        #     print("NOT ENOUGH DATA:", pair, "1m")

        # print("END test_indicators")
        return
        startt = timeit.timeit()
        print("TEST INDICATORS")
        # nano_close_1m = self.mw.historical_data.klines["NANOBTC"]["1m"].copy()
        df = pd.DataFrame(dataf)
        # df = pd.DataFrame.from_dict(nano_close_1m)
        df = df.apply(pd.to_numeric, errors='coerce')
        df = df.transpose()
        close = df.close_price.values.flatten()
        bbands = ti.bbands(close, period=5, stddev=2)
        bbandsdf = pd.DataFrame(bbands)
        bbandsdf = bbandsdf.transpose()
        bbandsdf.columns = ["lower band", "middle band", "upper band"]
        endtt = timeit.timeit()
        exect = endtt - startt
        print("EXEC TIME", exect)
            

        # print("bbands", bbands)

        # bbandsdf.to_csv("bbands.csv")
        # progress_callback.emit(bbandsdf)

        
        # pdb.set_trace()
        # return
        # df = pd.DataFrame(nano_close_1m)
        
        

        # better
        # close = df.close_price.values.flatten()
        # bbands = ti.bbands(close, period=5, stddev=2)
        # print("bbands", bbands)
        # bbandsdf = pd.DataFrame(bbands)
        # bbandsdf = bbandsdf.transpose()
        # bbandsdf.columns = ["lower band", "middle band", "upper band"]
        # # bbandsdf.to_csv("bbands.csv")
        # progress_callback.emit(bbandsdf)
        # return
        # return bbandsdf

    def calc_callback(self, msg):
        print("CALC CALLBACK")
        self.mw.lbl_iinterval.setText(msg["interval"])
        self.mw.lbl_ipair.setText(msg["pair"])
        self.mw.lbl_itime.setText(str(msg["time"]))
        self.mw.lbl_iclose.setText(str(msg["close"]))

        self.mw.lbl_iblow.setText(str(msg["bbandsl"]))
        self.mw.lbl_ibmid.setText(str(msg["bbandsm"]))
        self.mw.lbl_ibhigh.setText(str(msg["bbandsh"]))
        


    def new_gui_blink(self):
        self.mw.tradeTable.update()
        
        tab_index = self.mw.tabsBotLeft.currentIndex()

        if tab_index == 0:
            pass
            # self.mw.index_view.update()


        elif tab_index == 1:
            self.mw.open_orders_view.redraw()


        # This check should not be necessary
        if self.mw.coin_selector.completed_setup:
            self.mw.coin_selector.update()
        else:
            print("Coin selector setup not complete.")

        self.mw.live_data.set_history_values()

        # Redraw open orders since dynamic data is displayed
        # by delegates.
        


        if self.timer_count >= 4:
            if self.mw.is_connected:
                self.mw.data.ticker_df()

                self.mw.coin_selector.update()
            self.timer_count = 0

    def one_second_update(self):
        """Update some values every second."""

        try:
            total_btc_value = self.calc_total_btc()
            self.mw.total_btc_label.setText("<span style='color: #f3ba2e;'>" + total_btc_value + "</span>")

            total_usd_value = '{number:,.{digits}f}'.format(number=float(total_btc_value.replace(" BTC", "")) * float(self.mw.data.btc_price["lastPrice"]), digits=2) + "$"
            self.mw.total_usd_label.setText(total_usd_value)

            last_btc_price = float(self.mw.data.btc_price["lastPrice"])
            last_btc_price_formatted = '{number:,.{digits}f}'.format(number=last_btc_price, digits=2) + "$"

            if last_btc_price > self.last_btc_price:
                last_color = Colors.color_green
            elif last_btc_price == self.last_btc_price:
                last_color = Colors.color_lightgrey
            else:
                last_color = Colors.color_pink

            self.mw.btc_price_label.setText("<span style='color: " + last_color + "'>" + last_btc_price_formatted + "</span>")
            self.last_btc_price = last_btc_price

            operator = ""
            percent_change = float(self.mw.data.btc_price["priceChangePercent"])
            if percent_change > 0:
                operator = "+"
                percent_color = Colors.color_green
            else:
                percent_color = Colors.color_pink

            btc_percent = operator + '{number:,.{digits}f}'.format(number=percent_change, digits=2) + "%"
            self.mw.btc_percent_label.setText("<span style='color: " + percent_color + "'>" + btc_percent + "</span>")

            high = float(self.mw.data.btc_price["highPrice"])
            low = float(self.mw.data.btc_price["lowPrice"])
            vol = float(self.mw.data.btc_price["volume"])

            high_formatted = '{number:,.{digits}f}'.format(number=high, digits=2) + "$"
            low_formatted = '{number:,.{digits}f}'.format(number=low, digits=2) + "$"
            vol_formatted = '{number:,.{digits}f}'.format(number=vol, digits=2) + " BTC"

            self.mw.btc_high_label.setText("<span style='color: " + Colors.color_green + "'>" + high_formatted + "</span>")
            self.mw.btc_low_label.setText("<span style='color: " + Colors.color_pink + "'>" + low_formatted + "</span>")
            self.mw.btc_vol_label.setText("<span style='color: " + Colors.color_lightgrey + "'>" + vol_formatted + "</span>")
        except KeyError as e:
            print("1 sec update error:", e)

    def update_stats(self):
        """Reflect stats of the running application within the ui."""
        session_time = str(timedelta(seconds=self.runtime))
        total_time = str(timedelta(seconds=self.runtime + int(self.mw.cfg_manager.stats["Stats"]["timeRunning"])))



        self.mw.session_running.setText(session_time)
        self.mw.total_running.setText(total_time)

        self.mw.current_time.setText(str(time.strftime('%a, %d %b %Y %H:%M:%S')))

        # self.mw.explicit_api_calls_label.setText(str(val["apiCalls"]))
        try:
            self.mw.explicit_api_updates.setText(str(self.mw.websocket_manager.api_updates))
        except AttributeError:
            pass

    def check_websocket(self):
        """Check if websocket updates have stopped."""
        if self.update_count == int(self.mw.websocket_manager.api_updates):
            self.no_updates += 1
        else:
            self.no_updates = 0

        self.update_count = int(self.mw.websocket_manager.api_updates)

        if self.no_updates >= 2 and self.no_updates < 10:
            self.mw.status_label.setText("<span style='color:" + Colors.color_yellow + "'>waiting</span>")
        elif self.no_updates >= 10:
            self.mw.status_label.setText("<span style='color:" + Colors.color_pink + "'>disconnected!</span>")
        else:
            self.mw.status_label.setText("<span style='color:" + Colors.color_green + "'>connected</span>")


    def percent_changes(self):

        """Calculate and display price change values."""

        # close_t = float(val["klines"]["1m"].get(self.mw.data.current.pair, {})[-5][4])
        klines_data = self.mw.klines.get("1m")
        coin_data = klines_data.get(self.mw.data.current.pair)

        if isinstance(coin_data, list):
            close_5m = float(self.mw.klines["1m"][self.mw.data.current.pair][-5][4])
            close_15m = float(self.mw.klines["1m"][self.mw.data.current.pair][-15][4])
            # close_30m = float(self.mw.klines["1m"][self.mw.data.current.pair][-30][4])
            close_1h = float(self.mw.klines["1m"][self.mw.data.current.pair][-60][4])
            close_4h = float(self.mw.klines["1m"][self.mw.data.current.pair][-240][4])

            change_5m_value = ((float(self.mw.data.tickers[self.mw.data.current.pair]["lastPrice"]) / float(close_5m)) - 1) * 100
            change_15m_value = ((float(self.mw.data.tickers[self.mw.data.current.pair]["lastPrice"]) / float(close_15m)) - 1) * 100
            # change_30m_value = ((float(self.mw.data.tickers[self.mw.data.current.pair]["lastPrice"]) / float(close_30m)) - 1) * 100
            change_1h_value = ((float(self.mw.data.tickers[self.mw.data.current.pair]["lastPrice"]) / float(close_1h)) - 1) * 100
            change_4h_value = ((float(self.mw.data.tickers[self.mw.data.current.pair]["lastPrice"]) / float(close_4h)) - 1) * 100

            change_1d_value = float(self.mw.data.tickers[self.mw.data.current.pair]["priceChangePercent"])

            changes = [self.mw.change_5m, self.mw.change_15m, self.mw.change_1h, self.mw.change_4h, self.mw.change_1d]
            change_values = [change_5m_value, change_15m_value, change_1h_value, change_4h_value, change_1d_value]

            for i, change in enumerate(changes):
                if change_values[i] > 0:
                    operator = "+"
                    color = Colors.color_green
                elif change_values[i] < 0:
                    operator = ""
                    color = Colors.color_pink
                else:
                    operator = ""
                    color = Colors.color_grey

                # print(str(change))
                change.setText("<span style='color: " + color + "'>" + operator + "{0:.2f}".format(change_values[i]) + "%</span")


    # TODO: Make more generally available
    def calc_total_btc(self):
        """Multiply holdings by their current price to get
        the total account value."""
        total_btc_val = 0
        for holding in self.mw.user_data.holdings:
            free = self.mw.user_data.holdings[holding]["free"]
            locked = self.mw.user_data.holdings[holding]["locked"]
            total = float(free) + float(locked)

            if holding + "BTC" in self.mw.data.tickers:
                if holding != "BTC" and total * float(self.mw.data.tickers[holding + "BTC"]["lastPrice"]) > 0.001:

                    coin_total = total * float(self.mw.data.tickers[holding + "BTC"]["lastPrice"])
                    total_btc_val += coin_total

            elif holding == "BTC":
                total_btc_val += total

        # save in data dict
        self.mw.data.current.total_btc = '{number:.{digits}f}'.format(number=float(total_btc_val), digits=8)
        total_formatted = '{number:.{digits}f}'.format(number=float(total_btc_val), digits=8) + " BTC"

        # TODO: Verify
        # Set start btc if it has not been set yet
        if self.mw.data.user["start_btc"] == 0 and float(total_btc_val) > 0.0001:
            
            logging.info("Setting start btc " + total_formatted)
            self.mw.data.user.start_btc = self.mw.data.current.total_btc
        # else:
            # logging.info("ELSE" + self.mw.data.user["start_btc"] + " + " + total_btc_val)
        return total_formatted