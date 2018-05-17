from PyQt5.QtWebEngineWidgets import QWebEnginePage


class TQWebEnginePage(QWebEnginePage):
    def __init__(self, parent=None):
        super(TQWebEnginePage, self).__init__(parent)
