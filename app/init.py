# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Initialize needed variables."""


from collections import defaultdict
# import locale

# locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

val = defaultdict(dict)
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


val["indexTabOpen"] = False
proxies = {
    'http': 'http://10.10.1.10:3128',
    'https': 'http://10.10.1.10:1080'
}
