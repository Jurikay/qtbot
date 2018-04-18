from app.workers import Worker
# import PyQt5.QtWidgets as QtWidgets
# import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from app.init import val
import app
from functools import partial
from binance.websockets import BinanceSocketManager



class WebsocketManager:

    def __init__(self, mw):
        self.mw = mw
        self.threadpool = QtCore.QThreadPool()
        self.counter = 0
        self.client = app.client


    def create_signal(self):

        worker = Worker(self.func_to_call)
        worker.signals.progress.connect(self.receiver)
        self.threadpool.start(worker)
        self.counter = 5

    def func_to_call(self, progress_callback):
        progress_callback.emit("Nachricht")
        self.counter += 1


    def receiver(self, msg):
        print(msg)
        print(str(self.counter))



    # websockets
    def schedule_websockets(self):
        # Pass the function to execute
        worker = Worker(self.start_sockets)

        worker.signals.progress.connect(self.mw.live_data.progress_fn)

        # Execute
        self.threadpool.start(worker)




    # sockets
    def start_sockets(self, progress_callback):
        val["bm"] = BinanceSocketManager(app.client)
        self.websockets_symbol()
        # start user and ticker websocket separately since it does not need to be restarted
        val["userWebsocket"] = val["bm"].start_user_socket(self.user_callback)
        val["tickerWebsocket"] = val["bm"].start_ticker_socket(self.ticker_callback)
        val["bm"].start()

    def websockets_symbol(self):
        """Symbol specific websockets. This gets called on pair change."""
        val["aggtradeWebsocket"] = val["bm"].start_aggtrade_socket(val["pair"], self.trade_callback)
        val["depthWebsocket"] = val["bm"].start_depth_socket(val["pair"], self.depth_callback, depth=20)
        val["klineWebsocket"] = val["bm"].start_kline_socket(val["pair"], self.kline_callback)
        # logging.info('Starting websockets for %s' % str(val["pair"]))

    ###########################
    # CALLBACKS
    ###########################


    def trade_callback(self, msg):
        val["globalList"].insert(0, {"price": msg["p"], "quantity": msg["q"], "maker": bool(msg["m"]), "time": msg["T"]})

        if len(val["globalList"]) > 50:
            val["globalList"].pop()

        # make a copy to track changes later
        val["tradeHistory"] = val["globalList"][:]


        history = {"price": msg["p"], "quantity": msg["q"], "maker": bool(msg["m"]), "time": msg["T"]}
        worker = Worker(partial(self.socket_history, history))
        worker.signals.progress.connect(self.mw.live_data.progress_history)
        # worker.signals.finished.connect(self.t_complete)
        self.threadpool.start(worker)
        val["apiUpdates"] += 1


    def depth_callback(self, msg):
        old_bids = val["bids"]
        old_asks = val["asks"]

        val["bids"] = msg["bids"]
        val["asks"] = msg["asks"]

        if old_bids != val["bids"]:
            worker = Worker(partial(self.socket_orderbook, msg["bids"]))
            worker.signals.progress.connect(self.mw.live_data.progress_bids)
            # worker.signals.finished.connect(self.t_complete)
            self.threadpool.tryStart(worker)
        if old_asks != val["asks"]:
            worker = Worker(partial(self.socket_orderbook, msg["asks"]))
            worker.signals.progress.connect(self.mw.live_data.progress_asks)
            # worker.signals.finished.connect(self.t_complete)
            self.threadpool.tryStart(worker)
        val["apiUpdates"] += 1


    def user_callback(self, msg):

        # print("user callback")
        # print("####################")
        # print(str(self))
        # print(msg)
        userMsg = dict()
        val["apiUpdates"] += 1
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
            worker.signals.progress.connect(self.mw.holdings_table.holding_updated)
            self.threadpool.start(worker)


        elif userMsg["e"] == "executionReport":

            # prepare order dictionary
            order = dict()
            order = {"symbol": userMsg["s"], "price": userMsg["p"], "origQty": userMsg["q"], "side": userMsg["S"], "orderId": userMsg["i"], "status": userMsg["X"], "time": userMsg["T"], "type": userMsg["o"], "executedQty": userMsg["z"]}

            # propagate order
            worker = Worker(partial(self.socket_order, order))

            if userMsg["X"] == "NEW":
                worker.signals.progress.connect(self.mw.open_orders.add_to_open_orders)
                # worker.signals.progress.connect(self.play_sound_effect)

            elif userMsg["X"] == "CANCELED":
                worker.signals.progress.connect(self.mw.open_orders.remove_from_open_orders)

                # if order was canceled but partially filled, add to history
                if float(order["executedQty"]) > 0:
                    worker.signals.progress.connect(self.mw.history_table.add_to_history)


            elif userMsg["X"] == "PARTIALLY_FILLED":
                worker.signals.progress.connect(self.mw.open_orders.update_open_order)

            elif userMsg["X"] == "FILLED":
                worker.signals.progress.connect(self.mw.open_orders.remove_from_open_orders)
                worker.signals.progress.connect(self.mw.history_table.add_to_history)
                worker.signals.progress.connect(self.mw.holdings_table.check_add_to_holdings)


            else:
                print(msg)
            self.threadpool.start(worker)

        else:
            print(msg)


    def ticker_callback(self, msg):
        val["apiUpdates"] += 1
        # print("TICKER:" + str(dt.datetime.now()))
        for _, value in enumerate(msg):
            # ticker[key] = value
            # print("key: " + str(key))
            # print("value: " + str(value))
            # print("ticker: " + str(ticker))
            if "BTC" in value["s"]:
                ticker_data = {'symbol': value["s"], 'priceChange': value["p"], 'priceChangePercent': value["P"], 'weightedAvgPrice': value["w"], 'prevClosePrice': value["x"], 'lastPrice': value["c"], 'lastQty': value["Q"], 'bidPrice': value["b"], 'bidQty': value["B"], 'askPrice': value["a"], 'askQty': value["A"], 'openPrice': value["o"], 'highPrice': value["h"], 'lowPrice': value["l"], 'volume': value["v"], 'quoteVolume': value["q"], 'openTime': value["O"], 'closeTime': value["C"], 'firstId': value["F"], 'lastId': value["L"], 'count': value["n"]}
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
        # print("kline msg:")
        # print(msg)
        pass



    def socket_history(self, history, progress_callback):
        progress_callback.emit(history)


    def socket_orderbook(self, depth, progress_callback):
        progress_callback.emit(depth)


    def socket_order(self, order, progress_callback):
        progress_callback.emit(order)


    def socket_update_holdings(self, progress_callback):
        progress_callback.emit("update")
