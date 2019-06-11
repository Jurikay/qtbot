# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Class containing websocket logic."""

from app.workers import Worker
# import PyQt5.QtWidgets as QtWidgets
# import PyQt5.QtGui as QtGui
# import PyQt5.QtCore as QtCore

# import app
from functools import partial
from binance.websockets import BinanceSocketManager
# from binance.depthcache import DepthCacheManager
import pandas as pd
import time


class WebsocketManager:

    def __init__(self, mw, tp, client, mutex):
        # print("INIT WEBSOCKET MANAGER")
        self.mw = mw
        self.threadpool = tp
        # self.counter = 0
        self.client = client
        self.api_updates = 0

        # self.socket_mgr = None

        self.tickers = dict()


        self.userWebsocket = None
        self.tickerWebsocket = None

        self.aggTradeSocket = None
        self.depthSocket = None
        self.klineSocket1 = None
        self.klineSocket5 = None

        # self.index_data = dict()
        self.index_df = None
        self.socket_mgr = BinanceSocketManager(self.client)
        self.mutex = mutex
        self.kline_sockets = dict()


    # websockets
    def schedule_websockets(self):
        # Pass the function to execute
        worker = Worker(self.start_sockets)
        worker.signals.finished.connect(self.sockets_connected)

        # Execute
        self.threadpool.start(worker)


    def sockets_connected(self):
        print("SOCKET CONNECTED")


    # sockets
    def start_sockets(self, progress_callback):
        """Called once in the beginning to initiate all websockets.
        Later only pair specific sockets will be changed. User and ticker stay open."""
        print("Start sockets")
        self.websockets_symbol()
        self.userWebsocket = self.socket_mgr.start_user_socket(self.user_callback)
        self.tickerWebsocket = self.socket_mgr.start_ticker_socket(self.ticker_callback)

        # # testing multiplex kline socket:
        # self.klineSocket = self.socket_mgr.start_multiplex_socket(['bnbbtc@kline_1m', 'neobtc@kline_1m'], self.kline_callback)

        self.socket_mgr.start()

        progress_callback.emit("sockets started")

    def stop_sockets(self):
        self.socket_mgr.stop_socket(self.aggTradeSocket)
        self.socket_mgr.stop_socket(self.depthSocket)

        # self.socket_mgr.stop_socket(self.klineSocket_1m)
        # self.socket_mgr.stop_socket(self.klineSocket_5m)
        # self.socket_mgr.stop_socket(self.klineSocket_15m)
        # self.socket_mgr.stop_socket(self.klineSocket_30m)




        # self.socket_mgr.stop_socket(self.klineSocket1)
        # self.socket_mgr.stop_socket(self.klineSocket5)


    def websockets_symbol(self):
        """Symbol specific websockets. This gets called on pair change."""
        self.depthSocket = self.socket_mgr.start_depth_socket(self.mw.data.current.pair, self.depth_callback, depth=20)
        self.aggTradeSocket = self.socket_mgr.start_aggtrade_socket(self.mw.data.current.pair, self.trade_callback)

    def start_kline_socket(self):
        """This has to be called later since ticker data must be present."""
        candle_timeframes = ["1m", "5m", "15m", "30m", "1h", "1d"]
        pairs = self.mw.data.tickers.keys()

        for tf in candle_timeframes:
            ticker_array = [x.lower() + "@kline_" + tf for x in pairs]
            self.kline_sockets[tf] = self.socket_mgr.start_multiplex_socket(ticker_array, self.kline_callback)
        

        # ticker_array_1m = [x.lower() + "@kline_1m" for x in pairs]
        # ticker_array_5m = [x.lower() + "@kline_5m" for x in pairs]
        # ticker_array_15m = [x.lower() + "@kline_15m" for x in pairs]
        # ticker_array_30m = [x.lower() + "@kline_30m" for x in pairs]

        # final_array = ticker_array_1m + ticker_array_5m + ticker_array_15m + ticker_array_30m
        # print("FINAL ARRAY", final_array)
        # self.klineSocket_1m = self.socket_mgr.start_multiplex_socket(ticker_array_1m, self.kline_callback)
        # self.klineSocket_5m = self.socket_mgr.start_multiplex_socket(ticker_array_5m, self.kline_callback)
        # self.klineSocket_15m = self.socket_mgr.start_multiplex_socket(ticker_array_15m, self.kline_callback)
        # self.klineSocket_30m = self.socket_mgr.start_multiplex_socket(ticker_array_30m, self.kline_callback)






    ###########################
    # CALLBACKS
    ###########################

    def trade_callback(self, msg):
        self.mw.trade_history.insert(0, {"price": msg["p"], "quantity": msg["q"], "maker": bool(msg["m"]), "time": msg["T"]})

        if len(self.mw.trade_history) > 50:
            self.mw.trade_history.pop()

        self.api_updates += 1

        # New Data
        self.mw.data.set_hist(msg)

        worker = Worker(self.socket_history)
        worker.signals.progress.connect(self.mw.live_data.new_last_price)
        self.threadpool.start(worker)

        
        

    def depth_callback(self, msg):

        # self.mw.mutex.lock()
        # self.mw.orderbook["bids"] = msg["bids"]
        # self.mw.orderbook["asks"] = msg["asks"]
        # self.mw.mutex.unlock()

        # NEW DATA

        # worker = Worker(self.socket_orderbook)
        worker = Worker(partial(self.socket_orderbook, msg))
        worker.signals.finished.connect(self.mw.live_data.set_spread)
        # worker.signals.finished.connect(partial(self.mw.data.set_depth, msg))
        worker.signals.finished.connect(self.mw.new_asks.update)
        worker.signals.finished.connect(self.mw.new_bids.update)

        worker.signals.finished.connect(partial(self.mw.limit_pane.determine_warnings, msg))
        # worker.signals.progress.connect(self.mw.asks_view.update)


        self.threadpool.start(worker)
        # self.api_updates += 1


    def user_callback(self, msg):

        userMsg = dict()
        self.api_updates += 1
        for key, value in msg.items():
            userMsg[key] = value

        if userMsg["e"] == "outboundAccountInfo":
            # for i in range(len(userMsg["B"])):
            #     pass

                # put account info in accHoldings dictionary. Access
                # free and locked holdings like so: accHoldings["BTC"]["free"]


                # self.mw.mutex.lock()
                # val["accHoldings"][userMsg["B"][i]["a"]] = {"free": userMsg["B"][i]["f"], "locked": userMsg["B"][i]["l"]}
                # self.mw.mutex.unlock()


            # self.mw.user_data.update_accholdings(userMsg["B"])


            worker = Worker(partial(self.socket_update_holdings, userMsg["B"]))

            # new: update values in holdings table new
            worker.signals.progress.connect(self.mw.user_data.update_holdings)

            self.threadpool.start(worker)


        elif userMsg["e"] == "executionReport":
            print("WSS: usermsg")
            # print(str(userMsg))
            # prepare order dictionary
            order = dict()
            order = {"symbol": userMsg["s"], "price": userMsg["L"], "orderPrice": userMsg["p"], "origQty": userMsg["q"], "side": userMsg["S"], "orderId": userMsg["i"], "status": userMsg["X"], "time": userMsg["E"], "type": userMsg["o"], "executedQty": userMsg["z"]}

            # propagate order
            worker = Worker(partial(self.socket_order, order))

            # this will be refactored

            if userMsg["X"] == "NEW":
                # add a new order to open orders table
                # old
                # worker.signals.progress.connect(self.mw.open_orders.add_to_open_orders)

                # new
                # self.mw.user_data.add_to_open_orders(order)
                worker.signals.progress.connect(self.mw.user_data.add_to_open_orders)



                self.mw.sound_manager.play_sound("order")
                # worker.signals.finished.connect(self.mw.sound_manager.order_sound)

                # update new table
                # worker.signals.progress.connect(self.mw.data_open_orders_table.update)


            elif userMsg["X"] == "CANCELED":
                # remove a cancelled order from open orders table
                # worker.signals.progress.connect(self.mw.open_orders.remove_from_open_orders)
                worker.signals.progress.connect(self.mw.user_data.remove_from_open_orders)


                # if order was canceled but partially filled, add to history
                if float(order["executedQty"]) > 0:
                    # worker.signals.progress.connect(self.mw.history_table.add_to_history)
                    worker.signals.progress.connect(self.mw.trade_history_view.websocket_update)

                self.mw.sound_manager.play_sound("cancel")


            elif userMsg["X"] == "PARTIALLY_FILLED":
                # update a partially filled open order and check if it has to be newly added.
                # worker.signals.progress.connect(self.mw.open_orders.update_open_order)
                # worker.signals.progress.connect(self.mw.user_data.holdings_table.check_add_to_holdings)

                worker.signals.progress.connect(self.mw.user_data.add_to_history)
                worker.signals.progress.connect(self.mw.user_data.add_to_open_orders)



            elif userMsg["X"] == "FILLED":
                # remove a filled order from open orders, add trade to history and check if it
                # has to be newly added.
                # worker.signals.progress.connect(self.mw.open_orders.remove_from_open_orders)
                # worker.signals.progress.connect(self.mw.history_table.add_to_history)
                # worker.signals.progress.connect(self.mw.user_data.holdings_table.check_add_to_holdings)

                # new
                worker.signals.progress.connect(self.mw.user_data.remove_from_open_orders)
                worker.signals.progress.connect(self.mw.user_data.add_to_history)
                worker.signals.progress.connect(self.mw.trade_history_view.websocket_update)

                if userMsg["S"] == "BUY":
                    self.mw.sound_manager.play_sound("buy")
                else:
                    self.mw.sound_manager.play_sound("sell")



            else:
                # catch and print any other trade callback messages.
                print("inner else", msg)

            self.threadpool.start(worker)

        else:
            print("outer else", msg)


    def ticker_callback(self, msg):
        self.api_updates += 1
        all_tickers = list()

        for value in msg:

            if value["s"][-3:] == "BTC" or value["s"] == "BTCUSDT":
                # print ("value", value)
                ticker_data = {'symbol': value["s"],
                               'priceChange': value["p"],
                               'priceChangePercent': float(value["P"]),
                               'weightedAvgPrice': value["w"],
                               'prevClosePrice': value["x"],
                               'lastPrice': float(value["c"]),
                               'lastQty': value["Q"],
                               'bidPrice': value["b"],
                               'bidQty': value["B"],
                               'askPrice': value["a"],
                               'askQty': value["A"],
                               'openPrice': value["o"],
                               'highPrice': value["h"],
                               'lowPrice': value["l"],
                               'volume': value["v"],
                               'quoteVolume': value["q"],
                               'openTime': value["O"],
                               'closeTime': value["C"],
                               'firstId': value["F"],
                               'lastId': value["L"],
                               'count': value["n"]}

                all_tickers.append(ticker_data)
                # ticker_dict[value["s"]] = ticker_data
                # print("APPEND", ticker_data)
                # savely set ticker item values
                # for item, item_value in ticker_data.items():
                #     if self.mw.tickers.get(value["s"], None):
                #         self.mutex.lock()
                #         self.mw.tickers[value["s"]][item] = item_value
                #         self.mutex.unlock()
                # df_data[value["s"]] = ticker_data
        # print("ALL TICKERS", all_tickers)
        # print("TICKER DICT", ticker_dict)
        if len(all_tickers) > 0:
            self.mw.data.set_tickers(all_tickers)

        # New Data
        # needs more refactoring..
        # self.mw.data.set_tickers(df_data)


        # self.mw.index_data.websocket_update(df_data)

        # worker = Worker(partial(self.socket_tickers, df_data))
        # worker.signals.progress.connect(self.mw.index_data.merge_df)
        # self.threadpool.start(worker)


        # Workaround to fix random crashes; TODO: refactor
        # if self.mw.index_data is not None:
        #     self.mw.index_data.merge_df(df_data)




    # def build_index_data(self, ticker_data):
    #     start_time = time.time()
    #     self.index_df = pd.DataFrame(ticker_data).transpose()
    #     print("DATAFRAME:", self.index_df)
    #     print("WS build index took", time.time() - start_time)

    
    def kline_callback(self, msg):
        relevant = msg["data"].get("k", dict())
        self.mw.historical_data.set_websocket_klines(relevant)
        # pair = msg["data"]["s"]
        # tf = msg["data"]["k"]["i"]
        # self.mw.data.klines[pair][tf] = msg["data"]

    def kline_callback_old(self, msg):
        kline_msg = dict()
        # New Data
        self.mw.data.set_klines(msg)

        for key, value in msg.items():
            kline_msg[key] = value
        # print("kline msg:")
        # print(msg)

        if msg["k"]["i"] == "1m":
            old_klines = self.mw.klines["1m"].get(self.mw.data.current.pair)
            if isinstance(old_klines, list):

                old_klines.pop()
                values = kline_msg["k"]
                new_entry = [values["t"], values["o"], values["h"], values["l"], values["c"], values["v"], values["T"], values["q"], values["n"], values["V"], values["Q"], values["B"]]
                old_klines.append(new_entry)


                self.mw.klines["1m"][self.mw.data.current.pair] = old_klines
        elif msg["k"]["i"] == "5m":
            # print("5m kline update")
            pass

    @staticmethod
    def socket_history(progress_callback):
        progress_callback.emit(1)

    def socket_orderbook(self, depth, progress_callback):
        self.mw.data.set_depth(depth)
        if depth.get("asks"):
            progress_callback.emit([depth["asks"], "asks"])
        if depth.get("bids"):
            progress_callback.emit([depth["bids"], "bids"])



    @staticmethod
    def socket_order(order, progress_callback):
        progress_callback.emit(order)

    @staticmethod
    def socket_update_holdings(holdings, progress_callback):
        progress_callback.emit(holdings)

    @staticmethod
    def socket_tickers(tickers, progress_callback):
        progress_callback.emit(tickers)
