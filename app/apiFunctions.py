# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Collection of functions concerning api calls."""

def getHoldings(client):
    """Make an inital API call to get BTC and coin holdings."""
    # API Call:
    order = client.get_account()
    accHoldings = dict()
    for i in range(len(order["balances"])):
        accHoldings[order["balances"][i]["asset"]] = {"free": order["balances"][i]["free"], "locked": order["balances"][i]["locked"]}

    return accHoldings


def getTickers(client):
    """Make an initial API call to get ticker data."""
    ticker = client.get_ticker()
    # print(str(ticker))
    all_tickers = dict()
    for _, ticker_data in enumerate(ticker):
        if "BTC" in ticker_data["symbol"]:
            # print(str(ticker_data))
            all_tickers[ticker_data["symbol"]] = ticker_data

    return all_tickers


def getTradehistory(client, pair):
    """Make an initial API call to get the trade history of a given pair. This is used until updated by websocket data"""
    # API call
    globalList = list()
    trades = client.get_aggregate_trades(symbol=pair, limit=50)
    for _, val in enumerate(trades):
        globalList.insert(0, {"price": str(val["p"]), "quantity": str(val["q"]), "maker": bool(val["m"]), "time": str(val["T"])})

    return globalList


def getDepth(client, symbol):
    # API Call
    depth = client.get_order_book(symbol=symbol, limit=20)

    asks = depth["asks"]
    bids = depth["bids"]
    return {"bids": bids, "asks": asks}



def get_open_orders(client, symbol):
    client.get_open_orders(symbol=symbol)


def availablePairs(client):
    """
    Create a dictonary containing all BTC tradepairs excluding USDT.

    Keys are:
    {'symbol': 'ETHBTC', 'tradedMoney': 3024.89552855, 'baseAssetUnit': 'Ξ', 'active': True, 'minTrade': '0.00100000', 'baseAsset': 'ETH', 'activeSell': 66254.102, 'withdrawFee': '0', 'tickSize': '0.000001', 'prevClose': 0.044214, 'activeBuy': 0, 'volume': '66254.102000', 'high': '0.047998', 'lastAggTradeId': 2809764, 'decimalPlaces': 8, 'low': '0.043997', 'quoteAssetUnit': '฿', 'matchingUnitType': 'STANDARD', 'close': '0.047656', 'quoteAsset': 'BTC', 'open': '0.044214', 'status': 'TRADING', 'minQty': '1E-8'}
    """
    # create a local dictionary
    coins = dict()

    # API Call
    products = client.get_products()

    # For every entry in API answer:
    for i, pair in enumerate(products["data"]):

        # Check if pair contains BTC, does not contain USDT and if volume is >0
        if "BTC" in pair["symbol"] and "USDT" not in pair["symbol"] and float(products["data"][i]["volume"]) > 0.0:
            # Create a temporary dictionary to store keys and values
            tempdict = dict()

            # Add every key-value pair to the temp dictionary
            for key, value in pair.items():
                tempdict[key] = value
            # Add every temp dictionary to the coin dictionary
            coins[tempdict["symbol"]] = tempdict

    # return the newly created coin dictionary

    # with open("coins.txt", "w") as f:
    #         f.write(str(coins))
    return coins


def percentage_ammount(total_btc, price, percentage, decimals):

    try:
        maxSize = (float(total_btc) / float(price)) * (percentage / 100)
    except ZeroDivisionError:
        maxSize = 0


    if decimals == 0:
        return int(maxSize)


    maxSizeRounded = int(maxSize * 10**decimals) / 10.0**decimals
    return maxSizeRounded


def get_tether(client):
    tether_info = client.get_ticker(symbol="BTCUSDT")
    return tether_info


def getOrders(client, symbol):
    orders = client.get_all_orders(symbol=symbol)
    return orders


def create_order(client):
    pass
