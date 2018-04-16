# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Set initial values based on API data."""

import os.path
import configparser
from binance.client import Client
# from config import binance_credentials
from app.init import val

from app.apiFunctions import getHoldings, getTickers, availablePairs
# from binance.depthcache import DepthCacheManager
#

from binance.exceptions import BinanceAPIException

from requests.exceptions import InvalidHeader
from app.elements.config import ConfigManager
import app


def read_stats():
    config = configparser.ConfigParser()

    # stat_vals = [val["stats"]["timeRunning"], val["stats"]["execTrades"], val["stats"]["execBotTrades"], val["stats"]["apiCalls"], val["stats"]["apiUpdates"]]


    if os.path.isfile("stats.ini"):
        config.read('stats.ini')

    else:
        config['Stats'] = {'timeRunning': 0,
                           'execTrades': 0,
                           'execBotTrades': 0,
                           'apiCalls': 0,
                           'apiUpdates': 0,
                           }
        with open('stats.ini', 'w') as configfile:
            config.write(configfile)
        print("Config file has been written.")

    print("reading stats")
    # for i, cfg in enumerate(config["Stats"]):
    #     stat_vals[i] = int(config["Stats"][cfg])
        

    #     print(str(config["Stats"][cfg]))
    val["stats"]["timeRunning"] = config["Stats"]["timeRunning"]
    val["stats"]["execTrades"] = config["Stats"]["execTrades"]
    val["stats"]["execBotTrades"] = config["Stats"]["execBotTrades"]
    val["stats"]["apiCalls"] = config["Stats"]["apiCalls"]
    val["stats"]["apiUpdates"] = config["Stats"]["apiUpdates"]


def set_pair_values():
    val["coin"] = val["pair"][:-3]


    val["decimals"] = len(str(val["coins"][val["pair"]]["tickSize"])) - 2


    if int(val["coins"][val["pair"]]["minTrade"]) == 1:
        val["assetDecimals"] = 0
    else:
        val["assetDecimals"] = len(str(val["coins"][val["pair"]]["minTrade"])) - 2




read_stats()

cfg = ConfigManager("init")
cfg.read_config()

try:
    client = Client(val["api_key"], val["api_secret"],
                    {"verify": True, "timeout": 61})
    val["client"] = client
except (TypeError, InvalidHeader):
    print("NO API KEY!")
# print("API CREDENTIALS:")
# print(str(val["api_key"]))


try:
    val["coins"] = availablePairs(client)

    val["accHoldings"] = getHoldings(client)

    # val["tether"] = get_tether(client)

    val["tickers"] = getTickers(client)

    val["apiCalls"] += 3
    # userMsg = dict()
    # accHoldings = dict()

    set_pair_values()
except (BinanceAPIException, NameError) as e:
    print("API ERROR")
    print(str(e))
    if "code=-1003" in str(e):
        print("ja ein api error :)")
