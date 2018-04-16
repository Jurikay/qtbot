# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import configparser
import os.path
import logging

import app
from app.init import val


class ConfigManager:
    def __init__(self, mw):
        print("init")
        self.mw = app.mw
        print(str(self.mw))


    def read_config(self):
        print("READING CFG")
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

    def connect_cfg(self):
        print("CONNECT CFG")
        print(str(self.mw))
        print(str(self.mw.save_config))
        app.mw.save_config.clicked.connect(self.write_config)

    def write_config(self):
        print("write cfg")
        key = self.mw.api_key.text()
        secret = self.mw.api_secret.text()
        defaultPair = self.mw.default_pair.text()
        # defaultTimeframe = self.mw.default_timeframe.text()

        raw_timeframes = [1, 3, 5, 15, 30, 45, 60, 120, 180, 240, 1440, "1w"]

        dtf = self.mw.dtf_selector.currentText()
        for i, tf in enumerate(val["validTimeframes"]):
            if str(dtf) == str(tf):
                # self.mw.dtf_selector.setCurrentIndex(i)
                tf_index = i

        copy_price = self.mw.copy_price_box.isChecked()
        copy_qty = self.mw.copy_qty_box.isChecked()
        print("checkbox state:" + str(copy_price) + " " + str(copy_qty))

        percent_texts = [self.mw.percent_1, self.mw.percent_2, self.mw.percent_3, self.mw.percent_4, self.mw.percent_5]
        percent = val["buttonPercentage"]

        for i, _ in enumerate(percent):

            try:
                if float(percent_texts[i].text()) >= 0 and float(percent_texts[i].text()) <= 100:
                    percent[i] = percent_texts[i].text()
                    percent_texts[i].setStyleSheet("color: #f3f3f3;")
                else:
                    percent_texts[i].setStyleSheet("color: #ff077a;")
            except ValueError:
                percent_texts[i].setStyleSheet("color: #ff077a;")

        config = configparser.ConfigParser()

        if key != val["api_key"] or secret != val["api_secret"]:
            self.mw.restart_warning.setStyleSheet("color: red;")

        print("saving config...")

        config['CONFIG'] = {'DefaultPair': defaultPair,
                            'ButtonPercentages': percent[0] + ", " + percent[1] + ", " + percent[2] + ", " + percent[3] + ", " + percent[4],
                            'DefaultTimeframe': raw_timeframes[tf_index],
                            'CopyPrice': copy_price,
                            'CopyQuantity': copy_qty,
                            }
        config["API"] = {"Key": key, "Secret": secret}

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        self.read_config()
        self.set_button_text()
        logging.info("Saving config.")