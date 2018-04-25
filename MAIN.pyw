# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Main application entry point."""

import PyQt5.QtCore as QtCore

from PyQt5.QtWidgets import QApplication, QStyleFactory
from app.gui import beeserBot
import sys


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # QFontDatabase.addApplicationFont('static/Roboto-Bold.ttf')
    #

    app.setStyle(QStyleFactory.create('Fusion'))
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    if hasattr(QStyleFactory, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)

    widget = beeserBot()
    widget.show()
    app.aboutToQuit.connect(widget.shutdown_bot)

    sys.exit(app.exec_())
