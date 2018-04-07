from PyQt5.QtWidgets import (QWidget, QApplication, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QStyledItemDelegate)
from PyQt5.QtWidgets import QStyle
from PyQt5.QtGui import QFont, QColor


class CoinDelegate(QStyledItemDelegate):
    """
    TAKEN FROM https://stackoverflow.com/questions/43300034/qt-itemdelegate-displaytext-with-a-qtablewidget-how-can-i-access-the-table-in/43300126#43300126
    The following methods are subclassed to replace display and editor of the
    QTableWidget.
    """
    def __init__(self, parent):
        """
        Pass instance `parent` of parent class (TestTable)
        """
        super(CoinDelegate, self).__init__(parent)
        self.parent = parent  # instance of the parent (not the base) class

    def initStyleOption(self, option, index):
        """
        Initialize `option` with the values using the `index` index. When the 
        item (0,1) is processed, it is styled especially. All other items are 
        passed to the original `initStyleOption()` which then calls `displayText()`.
        """
        # print("delegate stuff")
        if index.column() == 1:
            option.text = str(index.data()) + " / BTC"

        elif index.column() == 2 or index.column() == 4:
            # orig = str(index.data())
            option.text = str(index.data()) + " BTC"

        elif index.column() == 3:
            percent_value = float(index.data())
            if percent_value > 0:
                operator = "+"
                
            else:
                operator = ""

            option.text = operator + "{0:.2f}".format(percent_value) + "%"

        else:
            # print(index.data())
            # continue with the original `initStyleOption()`
            super(CoinDelegate, self).initStyleOption(option, index)


    def displayText(self, text, locale):
        """
        Display `text` in the selected with the selected number
        of digits

        text:   string / QVariant from QTableWidget to be rendered
        locale: locale for the text
        """
        data = text  # .toString() # Python 2: need to convert to "normal" string
        return "{0:>{1}}".format(data, 4)
