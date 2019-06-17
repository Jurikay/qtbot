import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtWidgets as QtWidges
import PyQt5.QtGui as QtGui
import random, string

import traceback
import sys
import time

from functools import partial
from PyQt5.QtCore import pyqtSlot, QObject, QRunnable, pyqtSignal


class WorkerSignals(QObject):

    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    """

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(object)


class Worker(QRunnable):

    """
    Worker thread

    Inherits from QRunnable to handle worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        """ Initialise the runner function with passed args, kwargs."""

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


def base_str():
    return random.choice(string.ascii_letters)+ random.choice(string.digits)

class CustomSortModel(QtCore.QSortFilterProxyModel):
    def lessThan(self, left, right):
        #USE CUSTOM SORTING LOGIC HERE

        lvalue = str(left.data())
        rvalue = str(right.data())
        return lvalue[::-1] < rvalue[::-1]

class CustomTableWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(CustomTableWidget, self).__init__(parent)
        self.model = QtGui.QStandardItemModel(rows, columns)
        self.table = QtWidgets.QTableView()
        self.proxy_model = CustomSortModel()
        self.setItems()
        self.table.setSortingEnabled(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.table)

        self.model.itemChanged.connect(self.update_proxy)

        self.update_proxy()

    def setItems(self):
        self.model.setHorizontalHeaderLabels([str(x) for x in range(1, columns+1)])
        for row in range(rows):
            for column in range(columns):
                item = QtGui.QStandardItem(str(base_str()))
                self.model.setItem(row, column, item)

    def update_proxy(self, item=None):
        self.proxy_model.setSourceModel(self.model)
        self.table.setModel(self.proxy_model)

class StandardTableWidget(QtWidgets.QTableWidget):
    def __init__(self, parent):
        super(StandardTableWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Dialog)
        self.setRowCount(rows)
        self.setColumnCount(columns)
        self.setSortingEnabled(True)
        self.setItems()
    
    def setItems(self, progress_callback=None):
        for row in range(rows):
            for column in range(columns):
                item = QtWidgets.QTableWidgetItem()
                item.setText(str(base_str()))
                self.setItem(row, column, item)



def thread_loop(tp, progress_callback):
    while True:
        worker2 = Worker(item_callback)
        worker2.signals.finished.connect(widget.setItems)
        tp.start(worker2)
        time.sleep(1)


def item_callback(msg=None, progress_callback=None):
    print("CALLBACK")
    time.sleep(2)

if ( __name__ == '__main__' ):

    rows = 250
    columns = 20
    useCustomSorting = False


    app = None
    if ( QtWidgets.QApplication.instance() is None ):
        app = QtWidgets.QApplication([])

    if useCustomSorting:
        widget = CustomTableWidget(None)
    else:
        widget = StandardTableWidget(None)
        
    tp = QtCore.QThreadPool()

    worker = Worker(partial(thread_loop, tp))
    worker.signals.finished.connect(item_callback)
    tp.start(worker)


    widget.show()

    if (app):
        app.exec_()