# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Main application entry point."""

import PyQt5.QtCore as QtCore

from PyQt5.QtWidgets import QApplication, QStyleFactory
from app.gui import beeserBot
import sys
import app
from datetime import datetime
import os


if __name__ == "__main__":

    # os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-logging"
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"
    os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "13337"
    os.environ["QT_SCALE_FACTOR"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    main_app = QApplication(sys.argv)

    # QFontDatabase.addmain_applicationFont('static/Roboto-Bold.ttf')
    

    main_app.setStyle(QStyleFactory.create('Fusion'))
    main_app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    if hasattr(QStyleFactory, 'AA_UseHighDpiPixmaps'):
        main_app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)

    widget = beeserBot()
    widget.show()
    main_app.aboutToQuit.connect(widget.shutdown_bot)

    app.main_app = main_app



    sys.exit(main_app.exec_())
