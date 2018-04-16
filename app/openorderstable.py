import PyQt5.QtWidgets as QtWidgets


class OpenOrdersTable(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super(QtWidgets.QTableWidget, self).__init__(parent)

    def mouseDoubleClickEvent(self, event):
        print("CLICK")
        print(str(self))
        print(str(self.parent()))

    def test_func(self):
        print("TEST FUNC")

