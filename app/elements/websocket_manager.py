from app.workers import Worker
# import PyQt5.QtWidgets as QtWidgets
# import PyQt5.QtGui as QtGui
# import PyQt5.QtCore as QtCore
from app.init import val
import app
from functools import partial
from binance.websockets import BinanceSocketManager



class WebsocketManager:

    def __init__(self, mw, tp, client):
        self.mw = mw
        self.threadpool = tp
        # self.counter = 0
        self.client = client
        self.api_updates = 0

        self.socket_mgr = None

        self.tickers = dict()



    # websockets
    def schedule_websockets(self):
        print("SCHEDULE SOCKETS!!!!")
        # Pass the function to execute
        worker = Worker(self.start_sockets)


        # Execute
        self.threadpool.start(worker)



    # sockets
    def start_sockets(self, progress_callback):
        print("START SOCKETS!!!")
        self.socket_mgr = BinanceSocketManager(app.client)
        self.websockets_symbol()
        # start user and ticker websocket separately since it does not need to be restarted
        val["userWebsocket"] = self.socket_mgr.start_user_socket(self.user_callback)
        val["tickerWebsocket"] = self.socket_mgr.start_ticker_socket(self.ticker_callback)
        self.socket_mgr.start()

    def stop_sockets(self):
        self.socket_mgr.stop_socket(val["aggtradeWebsocket"])
        self.socket_mgr.stop_socket(val["depthWebsocket"])
        self.socket_mgr.stop_socket(val["klineWebsocket"])
        self.socket_mgr.stop_socket(val["klineWebsocket5"])


    def websockets_symbol(self):
        """Symbol specific websockets. This gets called on pair change."""
        val["aggtradeWebsocket"] = self.socket_mgr.start_aggtrade_socket(self.mw.cfg_manager.pair, self.trade_callback)
        val["depthWebsocket"] = self.socket_mgr.start_depth_socket(self.mw.cfg_manager.pair, self.depth_callback, depth=20)
        val["klineWebsocket"] = self.socket_mgr.start_kline_socket(self.mw.cfg_manager.pair, self.kline_callback, interval="1m")
        val["klineWebsocket5"] = self.socket_mgr.start_kline_socket(self.mw.cfg_manager.pair, self.kline_callback, interval="5m")
        # logging.info('Starting websockets for %s' % str(self.mw.cfg_manager.pair))

    ###########################
    # CALLBACKS
    ###########################


    def trade_callback(self, msg):
        self.mw.trade_history.insert(0, [msg["p"], msg["q"], bool(msg["m"]), msg["T"]])

        if len(self.mw.trade_history) > 50:
            self.mw.trade_history.pop()

        self.api_updates += 1

        worker = Worker(self.socket_history)
        worker.signals.progress.connect(self.mw.live_data.set_orderbook_values)
        self.threadpool.start(worker)


    def depth_callback(self, msg):

        val["bids"] = msg["bids"]
        val["asks"] = msg["asks"]

        worker = Worker(partial(self.socket_orderbook, msg))
        worker.signals.progress.connect(self.mw.live_data.progress_orderbook)
        self.threadpool.tryStart(worker)
        self.api_updates += 1


    def user_callback(self, msg):

        userMsg = dict()
        self.api_updates += 1
        for key, value in msg.items():
            userMsg[key] = value

        if userMsg["e"] == "outboundAccountInfo":
            for i in range(len(userMsg["B"])):

                # put account info in accHoldings dictionary. Access
                # free and locked holdings like so: accHoldings["BTC"]["free"]
                val["accHoldings"][userMsg["B"][i]["a"]] = {"free": userMsg["B"][i]["f"], "locked": userMsg["B"][i]["l"]}

            # update holdings table in a separate thread
            worker = Worker(self.socket_update_holdings)

            # update values in holdings table
            worker.signals.finished.connect(self.mw.holdings_table.holding_updated)
            self.threadpool.start(worker)


        elif userMsg["e"] == "executionReport":
            print(str(userMsg))
            # prepare order dictionary
            order = dict()
            order = {"symbol": userMsg["s"], "price": userMsg["Ls"], "origQty": userMsg["q"], "side": userMsg["S"], "orderId": userMsg["i"], "status": userMsg["X"], "time": userMsg["E"], "type": userMsg["o"], "executedQty": userMsg["z"]}

            # propagate order
            worker = Worker(partial(self.socket_order, order))

            # this will be refactored

            if userMsg["X"] == "NEW":
                # add a new order to open orders table
                worker.signals.progress.connect(self.mw.open_orders.add_to_open_orders)

            elif userMsg["X"] == "CANCELED":
                # remove a cancelled order from open orders table
                worker.signals.progress.connect(self.mw.open_orders.remove_from_open_orders)

                # if order was canceled but partially filled, add to history
                if float(order["executedQty"]) > 0:
                    worker.signals.progress.connect(self.mw.history_table.add_to_history)


            elif userMsg["X"] == "PARTIALLY_FILLED":
                # update a partially filled open order and check if it has to be newly added.
                worker.signals.progress.connect(self.mw.open_orders.update_open_order)
                worker.signals.progress.connect(self.mw.holdings_table.check_add_to_holdings)


            elif userMsg["X"] == "FILLED":
                # remove a filled order from open orders, add trade to history and check if it
                # has to be newly added.
                worker.signals.progress.connect(self.mw.open_orders.remove_from_open_orders)
                worker.signals.progress.connect(self.mw.history_table.add_to_history)
                worker.signals.progress.connect(self.mw.holdings_table.check_add_to_holdings)


            else:
                # catch and print any other trade callback messages.
                print(msg)

            self.threadpool.start(worker)

        else:
            print(msg)


    def ticker_callback(self, msg):
        self.api_updates += 1
        for value in msg:
            # ticker[key] = value
            # print("key: " + str(key))
            # print("value: " + str(value))
            # print("ticker: " + str(ticker))
            if "BTC" in value["s"]:
                ticker_data = {'symbol': value["s"], 'priceChange': value["p"], 'priceChangePercent': float(value["P"]), 'weightedAvgPrice': value["w"], 'prevClosePrice': value["x"], 'lastPrice': float(value["c"]), 'lastQty': value["Q"], 'bidPrice': value["b"], 'bidQty': value["B"], 'askPrice': value["a"], 'askQty': value["A"], 'openPrice': value["o"], 'highPrice': value["h"], 'lowPrice': value["l"], 'volume': value["v"], 'quoteVolume': value["q"], 'openTime': value["O"], 'closeTime': value["C"], 'firstId': value["F"], 'lastId': value["L"], 'count': value["n"]}
                # print(str(ticker_data))

                val["tickers"][value["s"]] = ticker_data
                # print(ticker_data["symbol"])
            #
            # if "BTC" in coin["s"]:
            #     if coin["s"] == "BNBBTC":
            #         print(coin)
        # print("###########")
        # print(msg)
        # with open("tickerMsg.txt", "w") as f:
        #     f.write(str(msg))


    def kline_callback(self, msg):
        kline_msg = dict()
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
            print("5m kline update")

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
    def socket_update_holdings(progress_callback):
        progress_callback.emit("update")
