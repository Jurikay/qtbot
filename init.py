#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © Jurek Baumann 2018

from collections import defaultdict
import os.path
import configparser


val = defaultdict(dict)
val["test"] = "hi"

val["globalList"] = list()
val["tradeHistory"] = list()
val["tickers"] = dict()

val["buyAllowed"] = False
val["sellAllowed"] = False

val["history"] = dict()
val["timeRunning"] = 0

val["ticker"] = dict()
proxies = {
    'http': 'http://10.10.1.10:3128',
    'https': 'http://10.10.1.10:1080'
}

# def read_config():
#     if os.path.isfile("config.ini"):
#


def read_config():
    config = configparser.ConfigParser()


    if os.path.isfile("config.ini"):
        config.read('config.ini')

        print("Config found!")

    else:
        config['CONFIG'] = {'DefaultPair': 'BNBBTC',
                            'ButtonPercentages': '10, 25, 33, 50, 100',
                            'DefaultTimeframe': '15m',
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
