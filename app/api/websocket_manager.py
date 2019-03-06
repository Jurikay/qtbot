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

    # websockets
    def schedule_websockets(self):
        # print("SCHEDULE SOCKETS!!!!")
        # Pass the function to execute
        worker = Worker(self.start_sockets)


        # Execute
        self.threadpool.start(worker)



    # sockets
    def start_sockets(self, progress_callback):
        print("Start sockets")
        self.websockets_symbol()
        self.userWebsocket = self.socket_mgr.start_user_socket(self.user_callback)
        self.tickerWebsocket = self.socket_mgr.start_ticker_socket(self.ticker_callback)
        self.socket_mgr.start()

    def stop_sockets(self):
        self.socket_mgr.stop_socket(self.aggTradeSocket)
        self.socket_mgr.stop_socket(self.depthSocket)
        # self.socket_mgr.stop_socket(self.klineSocket1)
        # self.socket_mgr.stop_socket(self.klineSocket5)


    def websockets_symbol(self):
        """Symbol specific websockets. This gets called on pair change."""
        self.depthSocket = self.socket_mgr.start_depth_socket(self.mw.cfg_manager.pair, self.depth_callback, depth=20)
        self.aggTradeSocket = self.socket_mgr.start_aggtrade_socket(self.mw.cfg_manager.pair, self.trade_callback)

        # print("depth socket", self.depthSocket)
        # self.klineSocket1 = self.socket_mgr.start_kline_socket(self.mw.cfg_manager.pair, self.kline_callback, interval="1m")
        # self.klineSocket5 = self.socket_mgr.start_kline_socket(self.mw.cfg_manager.pair, self.kline_callback, interval="5m")
        # logging.info('Starting websockets for %s' % str(self.mw.cfg_manager.pair))



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
        worker.signals.progress.connect(self.mw.live_data.set_history_values)
        self.threadpool.start(worker)


    def depth_callback(self, msg):

        self.mw.mutex.lock()
        self.mw.orderbook["bids"] = msg["bids"]
        self.mw.orderbook["asks"] = msg["asks"]
        self.mw.mutex.unlock()

        # NEW DATA
        self.mw.data.set_depth(msg)

        worker = Worker(partial(self.socket_orderbook, msg))
        # worker.signals.progress.connect(self.mw.live_data.progress_orderbook)

        worker.signals.progress.connect(self.mw.new_asks.update)
        worker.signals.progress.connect(self.mw.new_bids.update)

        # worker.signals.progress.connect(self.mw.asks_view.update)


        self.threadpool.tryStart(worker)
        self.api_updates += 1


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

            else:
                # catch and print any other trade callback messages.
                print("inner else", msg)

            self.threadpool.start(worker)

        else:
            print("outer else", msg)


    def ticker_callback(self, msg):
        self.api_updates += 1
        df_data = dict()
        all_tickers = list()
        ticker_dict = dict()
        
        for value in msg:
            # ticker[key] = value
            # print("key: " + str(key))
            # print("value: " + str(value))
            # print("ticker: " + str(ticker))
            
            if value["s"][-3:] == "BTC":
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
        if self.mw.index_data is not None:
            self.mw.index_data.merge_df(df_data)




    # def build_index_data(self, ticker_data):
    #     start_time = time.time()
    #     self.index_df = pd.DataFrame(ticker_data).transpose()
    #     print("DATAFRAME:", self.index_df)
    #     print("WS build index took", time.time() - start_time)


    def kline_callback(self, msg):
        kline_msg = dict()
        # New Data
        self.mw.data.set_klines(msg)

        for key, value in msg.items():
            kline_msg[key] = value
        # print("kline msg:")
        # print(msg)

        if msg["k"]["i"] == "1m":
            old_klines = self.mw.klines["1m"].get(self.mw.cfg_manager.pair)
            if isinstance(old_klines, list):

                old_klines.pop()
                values = kline_msg["k"]
                new_entry = [values["t"], values["o"], values["h"], values["l"], values["c"], values["v"], values["T"], values["q"], values["n"], values["V"], values["Q"], values["B"]]
                old_klines.append(new_entry)


                self.mw.klines["1m"][self.mw.cfg_manager.pair] = old_klines
        elif msg["k"]["i"] == "5m":
            # print("5m kline update")
            pass

    @staticmethod
    def socket_history(progress_callback):
        progress_callback.emit(1)

    @staticmethod
    def socket_orderbook(depth, progress_callback):
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
