# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


# import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
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

        page = WebEnginePage()

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


class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):

    @staticmethod
    def javaScriptConsoleMessage(level, msg, line, source):
        print("JAVSCRIPT MSG")

    def javaScriptAlert(self, url, js_msg):
        print("JS ALERT")

class CustomWebEnginePage (QtWebEngineWidgets.QWebEnginePage):
    def __init__(self):
        
        # self.app = QApplication(sys.argv)
        QtWebEngineWidgets.QWebEnginePage.__init__(self)
        self.JavaScriptConsoleMessageLevel = 2
        # self.html = ''
        # self.loadFinished.connect(self._on_load_finished)
        # self.load(QtCore.QUrl(url))
        # self.app.exec_()

    def javaScriptConsoleMessage(self, level, msg, line, source):
        print("JS CONSOLE")
        
        

    # def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
    #     print("JS CL")
        #Send the log entry to Python's logging or do whatever you want