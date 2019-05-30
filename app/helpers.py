import os, sys, math
from datetime import datetime
import dateparser
import pytz
import os
# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller.
    src: https://stackoverflow.com/a/13790741"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def check_file_exists(file_path):
    """Return true if a file exists at the given path."""
    return os.path.isfile(resource_path(file_path))

def date_to_milliseconds(date_str):
    """Convert UTC date to milliseconds
    If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"
    See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/
    :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours ago UTC", "now UTC"
    :type date_str: str

    Taken from: https://github.com/sammchardy/python-binance/tree/master/examples
    """
    # get epoch value in UTC
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    # parse our date string
    d = dateparser.parse(date_str)
    # if the date is not timezone aware apply UTC timezone
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)

    # return the difference in time
    return int((d - epoch).total_seconds() * 1000.0)

def read_file(file_path):
    """Read a text file and return it's contents as one single string."""
    location = resource_path(file_path)
    if os.path.isfile(location):
        with open(resource_path(file_path), "r") as file:
            content = file.read().replace('\n', '')
        return content

def round_decimals(number, digits):
    return '{number:.{digits}f}'.format(number=float(number), digits=digits)