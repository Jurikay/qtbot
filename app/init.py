# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Initialize needed variables."""


from collections import defaultdict
import locale
import argparse

# questionable if needed. Same is PyQt QLocale
locale.setlocale(locale.LC_ALL, 'C')
# locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# parse arguments (debug, verbose)
parser = argparse.ArgumentParser(description='Description of your program')
parser.add_argument('-d', '--debug', help='Enable debug mode', required=False, action='store_true')
parser.add_argument('-v', '--verbose', help='Enable verbose mode', required=False, action='store_true')
args = vars(parser.parse_args())

val = defaultdict(dict)

# set debug / verbose flags
if args['debug'] is True:
    print("debug enabled")
    # code here
    val["debug"] = True
else:
    val["debug"] = False

if args['verbose'] is True:
    print("verbose mode enabled")
    # code here
    val["verbose"] = False
else:
    val["verbose"] = False

val["test"] = "hi"

val["globalList"] = list()
val["tradeHistory"] = list()
val["tickers"] = dict()

val["buyAllowed"] = False
val["sellAllowed"] = False

val["history"] = dict()

val["validTimeframes"] = ["1m", "3m", "5m", "15m", "30m", "45m", "1h", "2h", "3h", "4h", "1d", "1w"]

val["ticker"] = dict()

val["stats"] = dict()

val["timeRunning"] = 0
val["execTrades"] = 0
val["execBotTrades"] = 0
val["apiCalls"] = 0
val["apiUpdates"] = 0

val["stats"]["timeRunning"] = 0
val["stats"]["execTrades"] = 0
val["stats"]["execBotTrades"] = 0
val["stats"]["apiCalls"] = 0
val["stats"]["apiUpdates"] = 0


val["klines"]["1m"] = dict()
val["klines"]["5m"] = dict()

val["volDirection"] = 0

val["indexTabOpen"] = False
proxies = {
    'http': 'http://10.10.1.10:3128',
    'https': 'http://10.10.1.10:1080'
}
