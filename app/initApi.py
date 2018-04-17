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





# print("API CREDENTIALS:")
# print(str(val["api_key"]))


# instantiate ApiCalls object


