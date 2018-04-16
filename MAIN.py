# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Main application entry point."""

from PyQt5.QtWidgets import QApplication, QStyleFactory
from app.gui import beeserBot
import sys


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # QFontDatabase.addApplicationFont('static/Roboto-Bold.ttf')
    #

    app.setStyle(QStyleFactory.create('Fusion'))

    widget = beeserBot()
    widget.show()
    app.aboutToQuit.connect(widget.shutdown_bot)

    sys.exit(app.exec_())
