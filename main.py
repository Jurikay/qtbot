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

if __name__ == "__main__":


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
