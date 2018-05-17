# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


# import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
# import PyQt5.QtWidgets as QtWidgets


from PyQt5.QtWebEngineWidgets import (QWebEngineView, QWebEnginePage,
                                      QWebEngineScript)


class ChartPage(QWebEngineView):

    """Custom WebEngineView subclass"""

    def __init__(self, parent=None):
        super(ChartPage, self).__init__(parent)

        # theme_color = self.style().standardPalette().color(QtGui.QPalette.Base)
        # profile = webenginesettings.default_profile

        page = WebEnginePage()
        self.page().JavaScriptConsoleMessageLevel(3)

        self.setPage(page)
        # print("CHART JESCHISCHTEN")

        self.delayEnabled = False
        self.delayTimeout = 250

        self._resizeTimer = QtCore.QTimer(self)
        self._resizeTimer.timeout.connect(self._delayedUpdate)


    def resizeEvent(self, event):
        if self.delayEnabled:
            self._resizeTimer.start(self.delayTimeout)
            self.setUpdatesEnabled(False)

        super(ChartPage, self).resizeEvent(event)

    def _delayedUpdate(self):
        print("Performing actual update")
        self._resizeTimer.stop()
        self.setUpdatesEnabled(True)


    def inject_script(self):
        script = QWebEngineScript()
        script.setSourceCode('''
            console.log("hi javascript!");

        ''')
        script.setWorldId(QWebEngineScript.MainWorld)
        script.setInjectionPoint(QWebEngineScript.DocumentReady)
        script.setRunsOnSubFrames(False)
        self.page().scripts().insert(script)



class WebEnginePage(QWebEnginePage):
    """Custom QWebEnginePage subclass."""
    def __init__(self, parent=None):
        super(WebEnginePage, self).__init__()

        self.delayEnabled = False
        self.delayTimeout = 1000

        self._resizeTimer = QtCore.QTimer(self)
        self._resizeTimer.timeout.connect(self._delayedUpdate)


    def resizeEvent(self, event):
        if self.delayEnabled:
            self._resizeTimer.start(self.delayTimeout)
            self.setUpdatesEnabled(False)

        super(ChartPage, self).resizeEvent(event)

    def _delayedUpdate(self):
        print("Performing actual update")
        self._resizeTimer.stop()
        self.setUpdatesEnabled(True)
        # self.theme_color = theme_color
        # self.setBackgroundColor(QtGui.QColor(QtCore.Qt.blue))

        # self.JavaScriptConsoleMessageLevel(2)
