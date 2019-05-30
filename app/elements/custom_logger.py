# from app.workers import Worker
# import PyQt5.QtGui as QtGui
# import PyQt5.QtCore as QtCore
import logging
from logging.handlers import RotatingFileHandler
import PyQt5.QtWidgets as QtWidgets

# TODO Revisit; add more logging entries

class BotLogger:

    def __init__(self, mw):
        self.mw = mw
        # TODO create log dir here


    def init_logging(self):
        qtLogger = QPlainTextEditLogger(self.mw)
        qtLogger.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger = logging.getLogger()

        logger.addHandler(qtLogger)

        fh = RotatingFileHandler("log.txt", maxBytes=10000, backupCount=5)
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        logger.addHandler(fh)

        error_handler = RotatingFileHandler("error.txt", maxBytes=10000, backupCount=5)
        error_handler.setLevel(logging.ERROR)
        logger.addHandler(error_handler)

        # You can control the logging level
        logger.setLevel(logging.INFO)

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
