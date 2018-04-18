from PyQt5.QtWebEngineWidgets import QWebEnginePage

class TQWebEnginePage(QWebEnginePage):
    def __init__(self):
        super(TQWebEnginePage, self).__init__(parent)