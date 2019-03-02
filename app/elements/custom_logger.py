# from app.workers import Worker
import PyQt5.QtWidgets as QtWidgets
# import PyQt5.QtGui as QtGui
# import PyQt5.QtCore as QtCore
from app.gui import logging

# TODO Revisit; add more logging entries

class BotLogger:

    def __init__(self, mw):
        self.mw = mw


    def init_logging(self):
        qtLogger = QPlainTextEditLogger(self.mw)
        qtLogger.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(qtLogger)

        # You can control the logging level
        logging.getLogger().setLevel(logging.INFO)

        self.mw.widget_2.setWidget(qtLogger.widget)


# logging
class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)
        self.widget.update()
        # print(msg)
