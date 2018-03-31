from init import val
from initApi import *
from functools import partial
import datetime as dt
from workers import *



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


def depthCallback(self, msg):
    old_bids = val["bids"]
    old_asks = val["asks"]

    val["bids"] = msg["bids"]
    val["asks"] = msg["asks"]

    if old_bids != val["bids"]:
        worker = Worker(partial(socket_orderbook, msg["bids"]))
        worker.signals.progress.connect(self.progress_bids)
        # worker.signals.finished.connect(self.t_complete)
        self.threadpool.start(worker)
    if old_asks != val["asks"]:
        worker = Worker(partial(socket_orderbook, msg["asks"]))
        worker.signals.progress.connect(self.progress_asks)
        # worker.signals.finished.connect(self.t_complete)
        self.threadpool.start(worker)



def userCallback(self, msg):

    # print("user callback")
    # print("####################")
    # print(str(self))
    # print(msg)


    for key, value in msg.items():
        userMsg[key] = value

    if userMsg["e"] == "outboundAccountInfo":
        for i in range(len(userMsg["B"])):

            # put account info in accHoldings dictionary. Access free and locked holdings like so: accHoldings["BTC"]["free"]
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

            elif userMsg["X"] == "CANCELED":
                worker.signals.progress.connect(self.remove_from_open_orders)

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
    # print("TICKER:" + str(dt.datetime.now()))
    ticker = dict()
    for key, value in enumerate(msg):
        # ticker[key] = value
        # print("key: " + str(key))
        # print("value: " + str(value))
        # print("ticker: " + str(ticker))
        if "BTC" in value["s"]:
            ticker_data = {'symbol': value["s"], 'priceChange': value["p"], 'priceChangePercent': value["P"], 'weightedAvgPrice': value["w"], 'prevClosePrice': value["x"], 'lastPrice': value["c"], 'lastQty': value["Q"], 'bidPrice': value["b"], 'bidQty': value["B"], 'askPrice': value["a"], 'askQty': value["A"], 'openPrice': value["o"], 'highPrice': value["h"], 'lowPrice': value["l"], 'volume': value["v"], 'quoteVolume': value["q"], 'openTime': value["O"], 'closeTime': value["C"], 'firstId': value["F"], 'lastId': value["L"], 'count': value["n"]}
            # print(str(ticker_data))

            val["tickers"][value["s"]] = ticker_data

        #
        # if "BTC" in coin["s"]:
        #     if coin["s"] == "BNBBTC":
        #         print(coin)
    # print("###########")
    # print(msg)
    # with open("tickerMsg.txt", "w") as f:
    #     f.write(str(msg))


def api_history(progress_callback):
    val["globalList"] = getTradehistory(client, val["pair"])
    progress_callback.emit({"history": val["globalList"]})

def api_depth(progress_callback):
    depth = getDepth(client, val["pair"])
    val["asks"] = depth["asks"]
    progress_callback.emit({"asks": val["asks"]})
    val["bids"] = depth["bids"]
    progress_callback.emit({"bids": val["bids"]})

def api_order_history(progress_callback):
    orders = getOrders(client, val["pair"])
    progress_callback.emit(orders)

def socket_history(history, progress_callback):
    progress_callback.emit(history)

def socket_orderbook(depth, progress_callback):
    progress_callback.emit(depth)

def socket_order(order, progress_callback):
    progress_callback.emit(order)

def update_holdings(progress_callback):
    progress_callback.emit("update")
