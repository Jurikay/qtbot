# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik


# import PyQt5.QtGui as QtGui
# import PyQt5.QtCore as QtCore
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
        self.page().JavaScriptConsoleMessageLevel(2)

        self.setPage(page)
        # print("CHART JESCHISCHTEN")


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
