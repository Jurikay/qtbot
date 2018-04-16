# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Collection of functions concerning websocket callbacks."""

from functools import partial

from app.apiFunctions import getAllOrders, getDepth, getTradehistory
from app.init import val
from app.initApi import client
from app.workers import Worker
from app.strategies.limit_order import LimitOrder

def directCallback(self, msg):
    val["globalList"].insert(0, {"price": msg["p"], "quantity": msg["q"], "maker": bool(msg["m"]), "time": msg["T"]})

    if len(val["globalList"]) > 50:
        val["globalList"].pop()

    # make a copy to track changes later
    val["tradeHistory"] = val["globalList"][:]


    history = {"price": msg["p"], "quantity": msg["q"], "maker": bool(msg["m"]), "time": msg["T"]}
    worker = Worker(partial(socket_history, history))
    worker.signals.progress.connect(self.progress_history)
    # worker.signals.finished.connect(self.t_complete)
    self.threadpool.start(worker)
    val["apiUpdates"] += 1


def depthCallback(self, msg):
    old_bids = val["bids"]
    old_asks = val["asks"]

    val["bids"] = msg["bids"]
    val["asks"] = msg["asks"]

    if old_bids != val["bids"]:
        worker = Worker(partial(socket_orderbook, msg["bids"]))
        worker.signals.progress.connect(self.progress_bids)
        # worker.signals.finished.connect(self.t_complete)
        self.threadpool.tryStart(worker)
    if old_asks != val["asks"]:
        worker = Worker(partial(socket_orderbook, msg["asks"]))
        worker.signals.progress.connect(self.progress_asks)
        # worker.signals.finished.connect(self.t_complete)
        self.threadpool.tryStart(worker)
    val["apiUpdates"] += 1


def userCallback(self, msg):

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
        worker = Worker(update_holdings)

        # update values in holdings table
        worker.signals.progress.connect(self.holding_updated)
        self.threadpool.start(worker)


    elif userMsg["e"] == "executionReport":

        # prepare order dictionary
        order = dict()
        order = {"symbol": userMsg["s"], "price": userMsg["p"], "origQty": userMsg["q"], "side": userMsg["S"], "orderId": userMsg["i"], "status": userMsg["X"], "time": userMsg["T"], "type": userMsg["o"], "executedQty": userMsg["z"]}

        # propagate order
        worker = Worker(partial(socket_order, order))

        if userMsg["X"] == "NEW":
            worker.signals.progress.connect(self.add_to_open_orders)
            worker.signals.progress.connect(self.play_sound_effect)

        elif userMsg["X"] == "CANCELED":
            worker.signals.progress.connect(self.remove_from_open_orders)

            # if order was canceled but partially filled, add to history
            if float(order["executedQty"]) > 0:
                worker.signals.progress.connect(self.add_to_history)


        elif userMsg["X"] == "PARTIALLY_FILLED":
            worker.signals.progress.connect(self.update_open_order)

        elif userMsg["X"] == "FILLED":
            worker.signals.progress.connect(self.remove_from_open_orders)
            worker.signals.progress.connect(self.add_to_history)
            worker.signals.progress.connect(self.check_add_to_holdings)


        else:
            print(msg)
        self.threadpool.start(worker)

    else:
        print(msg)


def tickerCallback(self, msg):
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


def klineCallback(self, msg):
    # print("kline msg:")
    # print(msg)
    pass


def api_history(progress_callback):
    val["globalList"] = getTradehistory(client, val["pair"])
    progress_callback.emit({"history": reversed(val["globalList"])})
    val["apiCalls"] += 1


def api_depth(progress_callback):
    depth = getDepth(client, val["pair"])
    val["asks"] = depth["asks"]
    progress_callback.emit({"asks": val["asks"]})
    val["bids"] = depth["bids"]
    progress_callback.emit({"bids": val["bids"]})
    val["apiCalls"] += 1


def api_all_orders(progress_callback):
    orders = client.get_open_orders()
    progress_callback.emit(orders)
    numberPairs = sum(val["pairs"].values())
    print("number pairs: " + str(numberPairs))


def api_order_history(pair, progress_callback):
    orders = getAllOrders(client, pair)
    progress_callback.emit(orders)
    val["apiCalls"] += 1


def socket_history(history, progress_callback):
    progress_callback.emit(history)


def socket_orderbook(depth, progress_callback):
    progress_callback.emit(depth)


def socket_order(order, progress_callback):
    progress_callback.emit(order)


def update_holdings(progress_callback):
    progress_callback.emit("update")
