# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


# import PyQt5.QtGui as QtGui
# import PyQt5.QtCore as QtCore
# import PyQt5.QtWidgets as QtWidgets


# from PyQt5.QtWebEngineWidgets import (QWebEngineView, QWebEnginePage,
#                                       QWebEngineScript)

from PyQt5 import QtWebEngineWidgets


class ChartPage(QtWebEngineWidgets.QWebEngineView):

    """Custom QWebEngineView subclass"""

    def __init__(self, parent=None):
        super(ChartPage, self).__init__(parent)

        # theme_color = self.style().standardPalette().color(QtGui.QPalette.Base)
        # profile = webenginesettings.default_profile

        page = CustomWebEnginePage()

        # self.page().JavaScriptConsoleMessageLevel(2)

        self.setPage(page)
        print("CHART JESCHISCHTEN")


    # def inject_script(self):
    #     script = QWebEngineScript()
    #     script.setSourceCode('''
    #         console.log("hi javascript!");

    #     ''')
    #     script.setWorldId(QWebEngineScript.MainWorld)
    #     script.setInjectionPoint(QWebEngineScript.DocumentReady)
    #     script.setRunsOnSubFrames(False)
    #     self.page().scripts().insert(script)



class CustomWebEnginePage (QtWebEngineWidgets.QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        print("JS CL")
        #Send the log entry to Python's logging or do whatever you want