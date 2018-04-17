from app.workers import Worker
# import PyQt5.QtWidgets as QtWidgets
# import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore


class TestKlasse:

    def __init__(self, mw):
        self.mw = mw


    def create_signal(self):
        self.threadpool = QtCore.QThreadPool()

        worker = Worker(self.func_to_call)
        worker.signals.progress.connect(self.receiver)
        self.threadpool.start(worker)

    def func_to_call(self, progress_callback):
        progress_callback.emit("Nachricht")

    def receiver(self, msg):
        print(msg)
