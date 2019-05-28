# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Main application entry point."""

import PyQt5.QtCore as QtCore
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QStyleFactory, QSplashScreen
from app.gui import beeserBot
import sys
import app
from datetime import datetime
import os
from app.helpers import resource_path
from app.elements.eastereggs import startup_sentence
from app.elements.configmanager import ConfiManager

# Verify usefulness
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


if __name__ == "__main__":

    cfg_manager = ConfiManager()
    # os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-logging"
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"
    os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "13337"
    os.environ["QT_SCALE_FACTOR"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    main_app = QApplication(sys.argv)

    # Splash screen
    splashFont = QFont()
    splashFont.setFamily("Source Sans Pro")
    splashFont.setWeight(100)
    # splashFont.setBold(True)
    splashFont.setPixelSize(20)
    # splashFont.setStretch(125)

    pixmap = QPixmap(resource_path("images/assets/splash.png"))
    splash = QSplashScreen(pixmap)
    splash.show()
    splash.setFont(splashFont)
    # splash.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    splash.showMessage(startup_sentence(), alignment=QtCore.Qt.AlignHCenter, color=QtCore.Qt.white)


    # Supposedly fixes QWebengineprocess orphans
    main_app.setAttribute(QtCore.Qt.AA_UseOpenGLES)

    # QFontDatabase.addmain_applicationFont('static/Roboto-Bold.ttf')
    

    main_app.setStyle(QStyleFactory.create('Fusion'))
    main_app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    # Disable popup menu animations since they appear glitchy in Qt < 5.12.3
    # TODO: Remove when fixed.
    main_app.setEffectEnabled(QtCore.Qt.UI_AnimateCombo, False)

    main_app.setAttribute(84, True)

    if hasattr(QStyleFactory, 'AA_UseHighDpiPixmaps'):
        main_app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)

    


    widget = beeserBot(cfg_manager)
    widget.show()
    # widget.setup()

    main_app.aboutToQuit.connect(widget.shutdown_bot)

    app.main_app = main_app


    
    splash.finish(widget)
    sys.exit(main_app.exec_())