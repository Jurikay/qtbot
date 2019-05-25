# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import configparser
import os.path
import logging
from app.helpers import resource_path

# initialize config manager in the very beginning:
# check for cfg file: if found read, if not create default
# ~~ cfg values loaded ~~

# check config
# read config
# create config
# write config to file
# change config

class ConfiManager:
    """Config manager class that acts as an interface between
    the config file and values."""
    def __init__(self, *args, **kwargs):
        self.config_filename = resource_path("config.ini")
        self.config = configparser.ConfigParser()
        self.initialize()

    def initialize(self):
        """Determine if a config file already exists. If so, read it.
        If not, create a default config and load the default values."""
        if os.path.isfile(self.config_filename):
            self.config.read(self.config_filename)
        else:
            config = self.create_config()
            self.config = config
        
        print("validating config...")
        parsed = self.parse_config(self.config)
        valid = self.validate_config(parsed)
        return self.config
            

    def validate_config(self, config_dict):
        """Determine if a given config conforms to expected keys and values."""
        clist = list(config_dict.keys())
        for cle in clist:
            print("CLE", cle)
        return clist

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


    def parse_config(self, cfg) -> dict():
        """Iterate over a config object and return it's values as dictionary."""
        c_dict = dict()
        for section in cfg:
            for key in cfg[section]:
                value = cfg[section][key]
                c_dict[key] = value
        return c_dict




    def create_config(self):
        """Create a config object with default values."""
        percent = [10, 25, 33, 50, 100]
        config = self.config
        config['CONFIG'] = {'DefaultPair': "BNBBTC",
                            'rememberDefault': True,
                            'ButtonPercentages': percent[0] + ", " + percent[1] + ", " + percent[2] + ", " + percent[3] + ", " + percent[4],
                            'DefaultTimeframe': "15m",
                            'BtcTimeframe': "1h",
                            'BtcExchange': "COINBASE",
                            # 'CopyPrice': copy_price,
                            # 'CopyQuantity': copy_qty,
                            'UiUpdates': 1,
                            'UiScale': 1,
                            }
        config["API"] = {"Key": "key", "Secret": "secret"}
        print("config obj:", config, "type:", type(config))
        return config

    def save_config(self):
        """Convenience function to instantly save active config."""
        self.write_config_to_file(self.config, self.config_filename)

    def write_config_to_file(self, config, file):
        """Write a config object to disk."""

        with open(file, "w") as configfile:
            config.write(configfile)
            logging.info("config file written.")