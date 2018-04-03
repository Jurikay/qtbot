# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Set initial values based on API data."""

import os.path
import configparser
from binance.client import Client
# from config import binance_credentials
from app.init import val

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
def read_config():
    config = configparser.ConfigParser()


    if os.path.isfile("config.ini"):
        config.read('config.ini')

        print("Config found!")

    else:
        config['CONFIG'] = {'DefaultPair': 'BNBBTC',
                            'ButtonPercentages': '10, 25, 33, 50, 100',
                            'DefaultTimeframe': 15,
                            'CopyPrice': True,
                            'CopyQuantity': False,
                            }
        config["API"] = {"Key": "PLEASE ENTER YOUR API KEY HERE", "Secret": "PLEASE ENTER YOUR API SECRET HERE"}

        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        print("Config file has been written.")

    val["pair"] = config["CONFIG"]["DefaultPair"]
    val["defaultPair"] = config["CONFIG"]["DefaultPair"]
    val["buttonPercentage"] = config["CONFIG"]["ButtonPercentages"].split(",")
    val["api_key"] = config["API"]["Key"]
    val["api_secret"] = config["API"]["Secret"]
    val["defaultTimeframe"] = config["CONFIG"]["DefaultTimeframe"]
    val["copy_price"] = config["CONFIG"]["CopyPrice"]
    val["copy_qty"] = config["CONFIG"]["CopyQuantity"]


def set_pair_values():
    val["coin"] = val["pair"][:-3]


    val["decimals"] = len(str(val["coins"][val["pair"]]["tickSize"]))-2


    if int(val["coins"][val["pair"]]["minTrade"]) == 1:
        val["assetDecimals"] = 0
    else:
        val["assetDecimals"] = len(str(val["coins"][val["pair"]]["minTrade"]))-2
    print("mintrade: " + str(val["assetDecimals"]))

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
