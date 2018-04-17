# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import configparser
import os.path
import logging

# import app
from app.init import val


class ConfigManager:
    def __init__(self, mw):
        self.mw = mw
        mw.save_config.clicked.connect(self.write_config)



    def read_config(self):
        print("READING CFG")
        config = configparser.ConfigParser()

        if os.path.isfile("config.ini"):
            config.read('config.ini')

            print("Config found!")

        else:
            print("no config file present. Generating default config.")
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

        self.set_config_values()
        self.read_stats()
        self.set_stats()

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


    def set_config_values(self):
        try:
            self.mw.default_pair.setText(val["defaultPair"])

            self.mw.api_key.setText(val["api_key"])
            self.mw.api_secret.setText(val["api_secret"])

            self.mw.percent_1.setText(str(int(val["buttonPercentage"][0])))
            self.mw.percent_2.setText(str(int(val["buttonPercentage"][1])))
            self.mw.percent_3.setText(str(int(val["buttonPercentage"][2])))
            self.mw.percent_4.setText(str(int(val["buttonPercentage"][3])))
            self.mw.percent_5.setText(str(int(val["buttonPercentage"][4])))
            self.set_button_text()

            # self.mw.default_timeframe.setText(str(val["defaultTimeframe"]))

            raw_timeframes = [1, 3, 5, 15, 30, 45, 60, 120, 180, 240, 1440]

            # dtf = self.dtf_selector.currentText()
            for i, tf in enumerate(raw_timeframes):
                if val["defaultTimeframe"] == str(tf):
                    self.mw.dtf_selector.setCurrentIndex(i)

        except (TypeError, KeyError):
            pass


    def set_button_text(self):
        self.mw.limit_button0.setText(str(val["buttonPercentage"][0]) + "%")
        self.mw.limit_button1.setText(str(val["buttonPercentage"][1]) + "%")
        self.mw.limit_button2.setText(str(val["buttonPercentage"][2]) + "%")
        self.mw.limit_button3.setText(str(val["buttonPercentage"][3]) + "%")
        self.mw.limit_button4.setText(str(val["buttonPercentage"][4]) + "%")

        self.mw.limit_sbutton0.setText(str(val["buttonPercentage"][0]) + "%")
        self.mw.limit_sbutton1.setText(str(val["buttonPercentage"][1]) + "%")
        self.mw.limit_sbutton2.setText(str(val["buttonPercentage"][2]) + "%")
        self.mw.limit_sbutton3.setText(str(val["buttonPercentage"][3]) + "%")
        self.mw.limit_sbutton4.setText(str(val["buttonPercentage"][4]) + "%")


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

    @staticmethod
    def write_stats():
        total_running = int(val["stats"]["timeRunning"]) + int(val["timeRunning"])
        total_trades = int(val["stats"]["execTrades"]) + int(val["execTrades"])
        total_bot_trades = int(val["stats"]["execBotTrades"]) + int(val["execBotTrades"])
        api_updates = int(val["stats"]["apiUpdates"]) + int(val["apiUpdates"])
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
        self.mw.total_running.setText(str(val["stats"]["timeRunning"]))
        self.mw.total_trades.setText(str(val["stats"]["execTrades"]))
        self.mw.total_bot_trades.setText(str(val["stats"]["execBotTrades"]))
        self.mw.total_api_calls.setText(str(val["stats"]["apiCalls"]))
        self.mw.total_api_updates.setText(str(val["stats"]["apiUpdates"]))
