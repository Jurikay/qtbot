# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import configparser
import os.path
import logging
import app
from app.helpers import resource_path

# initialize config manager in the very beginning:
# check for cfg file: if found read, if not create default
# ~~ cfg values loaded ~~

# check if config exists
# read config
# validate config
# create config
# write config to file
# change config
# get/ set config value



##################

class ConfiManager:
    """Config manager class that acts as an interface between
    the config file and values."""

    def __init__(self, cfg_path="config.ini"):
        self.config_filename = resource_path(cfg_path)
        self.stats_filename = resource_path("stats.ini")

        self.config = configparser.ConfigParser()
        self.stats = configparser.ConfigParser()
        self.initialize()

        # config values as attributes for easy access
        # TODO: Probably fit to refactor
        self.api_key = self.get_config_value("API", "key")
        self.api_secret = self.get_config_value("API", "secret")
        self.defaultTimeframe = self.get_config_value("CONFIG", "defaultTimeframe")
        self.btcTimeframe = self.get_config_value("CONFIG", "btcTimeframe")
        self.buttonPercentage = self.get_config_value("CONFIG", "buttonPercentages").split(", ")
        self.pair = self.get_config_value("CONFIG", "defaultpair")



    def initialize(self):
        """Determine if a config file already exists. If so, read it.
        If not, create a default config and return that."""
        if os.path.isfile(self.config_filename):
            print("read config file")
            self.config.read(self.config_filename)
            if self.validate_config(self.config):
                print("returning valid config from file")
                return self.config
        print("not valid")
        print("Generating new config")
        self.config = self.create_config()
        return self.config


    def init_stats(self):
        if os.path.isfile(self.stats_filename):
            self.stats.read(self.stats_filename)
            
        else:
            self.stats = self.create_stats()
        
        return self.stats

    def store_config(self, config_dict):
        """Receives a dict of config values. Store values
        as current config if validated."""
        print("store_config")
        config_obj = self.dict_to_config(config_dict)
        if self.validate_config(config_obj):
            print("Storing received config!")
            self.config = config_obj

    def get_config_value(self, key, section):
        return self.config.get(key, section)



    def dict_to_config(self, config_dict):
        """Takes a dictionary and returns a config object."""
        config = self.config
        config["CONFIG"] = config_dict["CONFIG"]
        config["API"] = config_dict["API"]
        return config



    def validate_config(self, config):
        """Check if a given config has valid values."""
        print("custom validate")
        config_valid = True
        non_valid_keys = list()
        for section in config.sections():
            for key, value in config.items(section):
                try:
                    if key == "defaultpair":
                        assert "BTC" in value
                    
                    if key == "rememberdefault":
                        assert value in ("False", "True")
                    
                    if key == "buttonpercentages":
                        assert len(value.split(",")) == 5
                        # for sub_value in value.split(","):
                        #     assert int(sub_value) <= 100

                    if key == "defaulttimeframe":
                        assert value in ("1", "3", "5", "15", "30", "60")
                    
                    if key == "btctimeframe":
                        assert value in ("1", "3", "5", "15", "30", "60")

                    if key == "copyprice":
                        assert value in ("False", "True")

                    if key == "uiscale":
                        assert float(value) >= 0.1 and float(value) <= 2

                    if key == "key":
                        assert value != "" and value is not None
                    
                    if key == "secret":
                        assert value != "" and value is not None
                    

                except AssertionError:
                    print("Error during config validation:")
                    print("key:", key, "value:", value)
                    non_valid_keys.append(key)
                    config_valid = False

        return config_valid


    def set_config_value(self, key, value):
        """Set a single config value. And write config to disk."""
        print("Setting config", key, "==", value)
        if self.config[key]:
            self.config[key] = value


    # not needed
    def read_config(self) -> dict():
        """Read a config file and return it's values as dict."""
        
        if os.path.isfile(self.config_filename):
            logging.info("Config found")

            self.config.read(self.config_filename)

        else:
            logging.info("No config file found. Creating")
            config = self.create_config()
            self.config = config
        
        return self.config

    def create_stats(self):
        stats = self.stats
        stats["Stats"] = {
            "timerunning": 0,
            "exectrades": 0,
            "apiupdates": 0,
            "apicalls": 0
        }
        return stats

    def create_config(self):
        """Create a config object with default values."""
        percent = ["10", "25", "33", "50", "100"]
        config = self.config
        config['CONFIG'] = {'DefaultPair': "BNBBTC",
                            'rememberDefault': True,
                            'ButtonPercentages': percent[0] + ", " + percent[1] + ", " + percent[2] + ", " + percent[3] + ", " + percent[4],
                            'DefaultTimeframe': "15",
                            'BtcTimeframe': "60",
                            'BtcExchange': "COINBASE",
                            # 'CopyPrice': copy_price,
                            # 'CopyQuantity': copy_qty,
                            'UiUpdates': 1,
                            'UiScale': 1,
                            }
        config["API"] = {"Key": "", "Secret": ""}
        print("config obj:", config, "type:", type(config))
        return config

    def save_config(self):
        """Convenience function to instantly save active config."""
        self.write_config_to_file(self.config, self.config_filename)

    def write_config_to_file(self, config, file):
        """Write a config object to disk."""

        with open(file, "w") as configfile:
            config.write(configfile)
            # logging.info(configfile, " written.")

    def write_config(self):
        # TODO: Implement
        print("writing config")

    ################################################
    # STATS
    ################################################
    def write_stats(self):
        self.write_config_to_file(self.stats, self.stats_filename)
        print("writing", str(self.stats_filename))
        