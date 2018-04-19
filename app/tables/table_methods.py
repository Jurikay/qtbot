

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui


class TableMethods:
    def __init__(self, mw):
        self.mw = mw

    def create_icon_item(self, symbol):
        """Takes a coin as str and returns an icon object."""

        icon = QtGui.QIcon("images/ico/" + symbol + ".svg")
        icon_item = QtWidgets.QTableWidgetItem()
        icon_item.setIcon(icon)
        return icon_item

