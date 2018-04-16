# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Set initial values based on API data."""

import os.path
import configparser
from binance.client import Client
# from config import binance_credentials
from app.init import val

# from app.apiFunctions import ApiCalls
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





read_stats()



# print("API CREDENTIALS:")
# print(str(val["api_key"]))


# instantiate ApiCalls object


