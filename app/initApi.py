# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Set initial values based on API data."""


from binance.client import Client
# from config import binance_credentials
from app.init import val, read_config

from app.apiFunctions import *
# from binance.depthcache import DepthCacheManager
#

from binance.exceptions import BinanceAPIException

from requests.exceptions import InvalidHeader

# get api credentials from config
# def init_api():
# binanceAcc = binance_credentials["MainAcc"]

# val["api_key"] = binanceAcc[0]
# val["api_secret"] = binanceAcc[1]
def set_pair_values():
    val["coin"] = val["pair"][:-3]


    val["decimals"] = len(str(val["coins"][val["pair"]]["tickSize"]))-2


    if int(val["coins"][val["pair"]]["minTrade"]) == 1:
        val["assetDecimals"] = 0
    else:
        val["assetDecimals"] = len(str(val["coins"][val["pair"]]["minTrade"]))-2


read_config()

try:
    client = Client(val["api_key"], val["api_secret"])
    val["client"] = client
except (TypeError, InvalidHeader):
    print("NO API KEY!")
# print("API CREDENTIALS:")
# print(str(val["api_key"]))


try:
    val["coins"] = availablePairs(client)

    val["accHoldings"] = getHoldings(client)

    val["tether"] = get_tether(client)

    val["tickers"] = getTickers(client)



    userMsg = dict()
    accHoldings = dict()

    set_pair_values()

except (BinanceAPIException, NameError) as e:
    print("API ERROR")
    print(str(e))


#


# init_api()
