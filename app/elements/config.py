# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import configparser
import os.path
import logging

# import app
from app.init import val
from app.charts import Webpages


class ConfigManager:
    def __init__(self, mw):
        self.mw = mw

        mw.save_config.clicked.connect(self.write_config)
        mw.ui_updates_box.valueChanged.connect(self.ui_value_text)
        mw.default_timeframe_selector.currentIndexChanged.connect(self.update_chart)
        mw.btc_timeframe_selector.currentIndexChanged.connect(self.update_btc_chart)
        mw.btc_exchange_selector.currentIndexChanged.connect(self.update_btc_chart)


        self.pair = ""
        self.coin = ""
        self.defaultPair = None
        self.rememberDefault = False
        self.buttonPercentage = None
        self.api_key = None
        self.api_secret = None
        self.defaultTimeframe = None
        self.btcTimeframe = None
        self.btcExchange = None
        self.copy_price = None
        self.copy_qty = None
        self.ui_updates = 1


    def initialize(self):
        """Read config.ini or create a default file if it doesn't exist."""
        config = configparser.ConfigParser()
        if os.path.isfile("config.ini"):
            config.read('config.ini')
            print("Config found!")
        else:
            print("no config file present. Generating default config.")
            config['CONFIG'] = {'DefaultPair': 'BNBBTC',
                                'rememberDefault': False,
                                'ButtonPercentages': '10, 25, 33, 50, 100',
                                'DefaultTimeframe': 15,
                                'BtcTimeframe': 60,
                                'BtcExchange': "COINBASE",
                                'CopyPrice': True,
                                'CopyQuantity': False,
                                'UiUpdates': 1,
                                }
            config["API"] = {"Key": "", "Secret": ""}

            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            print("Config file has been written.")

        self.pair = config["CONFIG"]["DefaultPair"]

        self.coin = self.pair[:-3]

        self.mw.default_pair_label.setText(self.pair)

        self.read_config(config)


    def read_config(self, config):
        print("READING CFG")
        try:
            # self.pair = config["CONFIG"]["DefaultPair"]
            self.defaultPair = config["CONFIG"]["DefaultPair"]
            if config["CONFIG"]["rememberDefault"] == "True":
                self.rememberDefault = True
            else:
                self.rememberDefault = False

            self.buttonPercentage = config["CONFIG"]["ButtonPercentages"].split(", ")
            self.api_key = config["API"]["Key"]
            self.api_secret = config["API"]["Secret"]
            self.defaultTimeframe = config["CONFIG"]["DefaultTimeframe"]
            self.btcTimeframe = config["CONFIG"]["BtcTimeframe"]
            self.btcExchange = config["CONFIG"]["BtcExchange"]
            self.copy_price = config["CONFIG"]["CopyPrice"]
            self.copy_qty = config["CONFIG"]["CopyQuantity"]
            self.ui_updates = config["CONFIG"]["UiUpdates"]
        except KeyError:
            print("CONFIG FILE BROKEN!")



        # refactor
        # self.mw.cfg_manager.pair = str(self.pair)

        # print()
        # print(self.mw.cfg_manager.pair)

        self.set_config_values()
        self.read_stats()
        self.set_stats()

    def write_config(self):
        print("write cfg")
        key = self.mw.api_key_label.text()
        secret = self.mw.api_secret_label.text()


        rememberDefault = self.mw.cfg_remember.isChecked()
        ui_updates = self.mw.ui_updates_box.value()
        btc_exchange = self.mw.btc_exchange_selector.currentText()


        if rememberDefault is True:
            print("REMEBER IS TRUE!!")
            defaultPair = self.pair
        else:
            defaultPair = self.mw.default_pair_label.text()

        # print("REMEMBER = " + str(rememberDefault))
        # print(type(rememberDefault))
        # defaultTimeframe = self.mw.default_timeframe.text()

        raw_timeframes = [1, 3, 5, 15, 30, 45, 60, 120, 180, 240, 1440, "1w"]

        default_timeframe = self.mw.default_timeframe_selector.currentText()
        btc_timeframe = self.mw.btc_timeframe_selector.currentText()

        for i, valid_tf in enumerate(val["validTimeframes"]):
            if str(valid_tf) == str(default_timeframe):
                tf_index = i

            if str(valid_tf) == str(btc_timeframe):
                btc_tf_index = i

        copy_price = self.mw.copy_price_box.isChecked()
        copy_qty = self.mw.copy_qty_box.isChecked()
        print("checkbox state:" + str(copy_price) + " " + str(copy_qty))

        percent_texts = [self.mw.percent_1, self.mw.percent_2, self.mw.percent_3, self.mw.percent_4, self.mw.percent_5]
        percent = self.buttonPercentage

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
                            'rememberDefault': rememberDefault,
                            'ButtonPercentages': percent[0] + ", " + percent[1] + ", " + percent[2] + ", " + percent[3] + ", " + percent[4],
                            'DefaultTimeframe': raw_timeframes[tf_index],
                            'BtcTimeframe': raw_timeframes[btc_tf_index],
                            'BtcExchange': btc_exchange,
                            'CopyPrice': copy_price,
                            'CopyQuantity': copy_qty,
                            'UiUpdates': ui_updates,
                            }
        config["API"] = {"Key": key, "Secret": secret}

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        self.read_config(config)
        self.set_button_text()
        logging.info("Saving config.")


    def set_config_values(self):
        try:

            self.mw.api_key_label.setText(self.api_key)
            self.mw.api_secret_label.setText(self.api_secret)
            self.mw.cfg_remember.setChecked(self.rememberDefault)

            pbuttons = [self.mw.percent_1, self.mw.percent_2, self.mw.percent_3, self.mw.percent_4, self.mw.percent_5]

            for i, p_btn in enumerate(pbuttons):
                p_btn.setText(str(int(self.buttonPercentage[i])))

            self.set_button_text()

            raw_timeframes = [1, 3, 5, 15, 30, 45, 60, 120, 180, 240, 1440]

            # dtf = self.dtf_selector.currentText()
            for i, tf in enumerate(raw_timeframes):
                if self.defaultTimeframe == str(tf):
                    self.mw.default_timeframe_selector.setCurrentIndex(i)
                if self.btcTimeframe == str(tf):
                    self.mw.btc_timeframe_selector.setCurrentIndex(i)

            btc_exchanges = ["COINBASE", "GEMINI", "BITSTAMP", "BITFINEX", "OKCOIN", "BINANCE"]
            for i, exchange in enumerate(btc_exchanges):
                if self.btcExchange == exchange:
                    self.mw.btc_exchange_selector.setCurrentIndex(i)

        except (TypeError, KeyError) as error:
            print("error on saving config")
            print("ERROR: " + str(error))


    def set_button_text(self):
        self.mw.limit_button0.setText(str(self.buttonPercentage[0]) + "%")
        self.mw.limit_button1.setText(str(self.buttonPercentage[1]) + "%")
        self.mw.limit_button2.setText(str(self.buttonPercentage[2]) + "%")
        self.mw.limit_button3.setText(str(self.buttonPercentage[3]) + "%")
        self.mw.limit_button4.setText(str(self.buttonPercentage[4]) + "%")

        self.mw.limit_sbutton0.setText(str(self.buttonPercentage[0]) + "%")
        self.mw.limit_sbutton1.setText(str(self.buttonPercentage[1]) + "%")
        self.mw.limit_sbutton2.setText(str(self.buttonPercentage[2]) + "%")
        self.mw.limit_sbutton3.setText(str(self.buttonPercentage[3]) + "%")
        self.mw.limit_sbutton4.setText(str(self.buttonPercentage[4]) + "%")


    ##########################
    # stats
    ##########################

    @staticmethod
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


    def write_stats(self):
        total_running = int(val["stats"]["timeRunning"]) + int(self.mw.gui_manager.runtime)
        total_trades = int(val["stats"]["execTrades"]) + int(val["execTrades"])
        total_bot_trades = int(val["stats"]["execBotTrades"]) + int(val["execBotTrades"])
        api_updates = int(val["stats"]["apiUpdates"]) + int(self.mw.websocket_manager.api_updates)
        api_calls = int(val["stats"]["apiCalls"]) + int(val["apiCalls"])

        config = configparser.ConfigParser()

        config["Stats"] = {"timeRunning": total_running,
                           "execTrades": total_trades,
                           "execBotTrades": total_bot_trades,
                           "apiUpdates": api_updates,
                           "apiCalls": api_calls}

        print("WRITING CONFIG")
        print(str(total_running) + " " + str(api_updates))

        with open('stats.ini', 'w') as configfile:
                    config.write(configfile)


    def set_stats(self):
        # self.mw.total_running.setText(str(val["stats"]["timeRunning"]))
        self.mw.total_trades.setText(str(val["stats"]["execTrades"]))
        self.mw.total_bot_trades.setText(str(val["stats"]["execBotTrades"]))
        self.mw.total_api_calls.setText(str(val["stats"]["apiCalls"]))
        self.mw.total_api_updates.setText(str(val["stats"]["apiUpdates"]))


    def ui_value_text(self):
        if self.mw.ui_updates_box.value() > 1:
            self.mw.ui_updates_label.setText("seconds")
        else:
            self.mw.ui_updates_label.setText("second")


    def update_btc_chart(self):
        self.mw.btc_chart.setHtml(Webpages.build_chart_btc("BTCUSD", self.mw.cfg_manager.btcTimeframe, self.mw.btc_exchange_selector.currentText()))

    def update_chart(self):
        self.mw.chart.setHtml(Webpages.build_chart2(self.pair, self.defaultTimeframe))
