# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


# import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
# import PyQt5.QtWidgets as QtWidgets


# from PyQt5.QtWebEngineWidgets import (QWebEngineView, QWebEnginePage,
#                                       QWebEngineScript)

from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEngineView, QWebEnginePage, QWebEngineProfile
from PyQt5.QtWebChannel import QWebChannel
import os
import webbrowser


class CallbackObject(QtCore.QObject):
    sigSetParentWindowTitle = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)

    @QtCore.pyqtSlot(str)
    def consolePrint(self, msg):
        print(msg)

    @QtCore.pyqtSlot(str)
    def openLink(self, url):
        # os.startfile(url)
        webbrowser.open(url)



    @QtCore.pyqtSlot(str)
    def setParentWindowTitle(self, msg):
        self.sigSetParentWindowTitle.emit(msg)

    @QtCore.pyqtSlot(str, str)
    def saveFile(self, content, fileName):
        with open(str(fileName), "w") as fp:
            fp.write(str(content))


class WebEnginePage(QWebEnginePage):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
    
    def javaScriptConsoleMessage(self, level, msg, linenumber, source_id):
        print("JAVSCRIPT MSG")

    def javaScriptAlert(self, url, js_msg):
        print("JS ALERT")


class ChartPage(QWebEngineView):

    """Custom QWebEngineView subclass"""

    def __init__(self, parent=None):
        QWebEngineView.__init__(self)

        self.__channel = QWebChannel(self.page())
        self.__my_object = CallbackObject(self)
        self.__channel.registerObject('MyObject', self.__my_object)
        self.page().setWebChannel(self.__channel)
        self.page().load(QtCore.QUrl.fromLocalFile("html/info.html"))
        self.disableJS()
        # page = WebEnginePage()
        # self.setPage(page)
    # def __init__(self, parent=None):
    #     super(ChartPage, self).__init__(parent)
        # self.JavaScriptConsoleMessageLevel = 2
        # print("WEBPAGE SET ATTRIBUTES")

        # theme_color = self.style().standardPalette().color(QtGui.QPalette.Base)
        



        # self.show()
        # print("CHART JESCHISCHTEN")

    # @QtCore.pyqtSlot()
    # def foo(self):
    #     print('bar')

    def urlChanged(self):
        print("URL CHANGE!!!")

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