# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


# import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
# import PyQt5.QtWidgets as QtWidgets


# from PyQt5.QtWebEngineWidgets import (QWebEngineView, QWebEnginePage,
#                                       QWebEngineScript)

from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEngineView, QWebEnginePage, QWebEngineProfile






class WebEnginePage(QWebEnginePage):

    # def __init__(self, parent=None):
    #     super().__init__(parent=parent)

    @staticmethod
    def javaScriptConsoleMessage(level, msg, line, source):
        print("JAVSCRIPT MSG")

    def javaScriptAlert(self, url, js_msg):
        print("JS ALERT")

# class CustomWebEnginePage(QWebEnginePage):
#     def __init__(self):
        
#         # self.app = QApplication(sys.argv)
#         QWebEnginePage.__init__(self)
#         self.JavaScriptConsoleMessageLevel = 0
#         # self.html = ''
#         # self.loadFinished.connect(self._on_load_finished)
#         # self.load(QtCore.QUrl(url))
#         # self.app.exec_()

#     def javaScriptConsoleMessage(self, *args):
#         print("JS CONSOLE")
        
        
class ChartPage(QWebEngineView):

    """Custom QWebEngineView subclass"""

    def __init__(self, parent=None):
        super(ChartPage, self).__init__(parent)
        self.JavaScriptConsoleMessageLevel = 2
        # print("WEBPAGE SET ATTRIBUTES")

        # theme_color = self.style().standardPalette().color(QtGui.QPalette.Base)
        page = WebEnginePage()

        # self.page().JavaScriptConsoleMessageLevel(2)
        self.disableJS()
        self.setPage(page)
        # print("CHART JESCHISCHTEN")

    def javaScriptAlert(self, *args):
        print("js alert")

    def javaScriptConsoleMessage(self, *args):
        print("JS CONSOLE")

    def disableJS(self):
        settings = QWebEngineSettings.globalSettings()
        settings.setAttribute(QWebEngineSettings.XSSAuditingEnabled, False)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        # settings.setAttribute(QWebEngineSettings.DnsPrefetchEnabled, True)

        # self.setAttribute(QWebEngineSettings.XSSAuditingEnabled, False)
        # self.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
    # def inject_script(self):
    #     script = QWebEngineScript()
    #     script.setSourceCode('''
    #         console.log("hi javascript!");

    #     ''')
    #     script.setWorldId(QWebEngineScript.MainWorld)
    #     script.setInjectionPoint(QWebEngineScript.DocumentReady)
    #     script.setRunsOnSubFrames(False)
    #     self.page().scripts().insert(script)
    # def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
    #     print("JS CL")
        #Send the log entry to Python's logging or do whatever you want