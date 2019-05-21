import os, sys, math

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

def round2precision(val, precision: int = 0, which: str = ''):
    """Round float to specified position. Round up or down."""
    assert precision >= 0
    val *= 10 ** precision
    round_callback = round
    if which.lower() == 'up':
        round_callback = math.ceil
    if which.lower() == 'down':
        round_callback = math.floor
    return '{1:.{0}f}'.format(precision, round_callback(val) / 10 ** precision)
