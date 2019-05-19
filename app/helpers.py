import os, sys

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