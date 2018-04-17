from app.workers import Worker
# import PyQt5.QtWidgets as QtWidgets
# import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore


class TestKlasse:

    def __init__(self, mw):
        self.mw = mw
        self.threadpool = QtCore.QThreadPool()
        self.counter = 0


    def create_signal(self):

        worker = Worker(self.func_to_call)
        worker.signals.progress.connect(self.receiver)
        self.threadpool.start(worker)
        self.counter = 5

    def func_to_call(self, progress_callback):
        progress_callback.emit("Nachricht")
        self.counter += 1


    def receiver(self, msg):
        print(msg)
        print(str(self.counter))
