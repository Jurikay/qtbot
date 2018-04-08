from PyQt5.QtWidgets import (QApplication, QStyledItemDelegate, QStyleOptionViewItem)
from PyQt5.QtWidgets import QStyle
from PyQt5.QtGui import QTextDocument, QAbstractTextDocumentLayout, QPalette
from app.colors import colors
from PyQt5.QtCore import QSize
from PyQt5 import Qt


class CoinDelegate(QStyledItemDelegate):
    """
    TAKEN FROM https://stackoverflow.com/questions/43300034/qt-itemdelegate-displaytext-with-a-qtablewidget-how-can-i-access-the-table-in/43300126#43300126
    AND https://stackoverflow.com/questions/41760474/pyqt-qstyleditemdelegate-word-wrap-and-html/43417837
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
        # print(self.parent.name())
        if index.column() == 1:
            option.text = "<span style='color:#cdcdcd;'>" + str(index.data()) + " / BTC</span>"

        elif index.column() == 2:
            # orig = str(index.data())
            option.text = "<span style='color:#cdcdcd;'>" + str(index.data()) + " BTC</span>"

        elif index.column() == 3:
            percent_value = float(index.data())
            if percent_value > 0:
                operator = "+"
                color = "#94c940"

            elif percent_value == 0.00:
                operator = ""
                color = "#999"

            else:
                operator = ""
                color = "#ff007a"

            option.text = "<span style='color:" + color + ";'>" + operator + "{0:.2f}".format(percent_value) + "%"
            option.textAlignmentRole = Qt.Qt.AlignRight


        elif index.column() == 4:
            option.text = "<span style='color:#cdcdcd;'>" + "{0:,.1f}".format(float(index.data())) + " BTC</span>"

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


    def paint(self, painter, option, index):
        """Reimplement paint function to allow html rendering within tableWidgets."""
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        style = QApplication.style() if options.widget is None else options.widget.style()

        doc = QTextDocument()
        doc.setHtml(options.text)

        options.text = ""
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)

        ctx = QAbstractTextDocumentLayout.PaintContext()
        if option.state & QStyle.State_Selected:
            ctx.palette.setColor(QPalette.Text, option.palette.color(QPalette.Active, QPalette.HighlightedText))
        else:
            ctx.palette.setColor(QPalette.Text, option.palette.color(QPalette.Active, QPalette.HighlightedText))


        textRect = style.subElementRect(QStyle.SE_ItemViewItemText, options)
        painter.save()
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def sizeHint(self, option, index):
        """sizeHint has also to be reimplemented."""
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        doc = QTextDocument()
        doc.setHtml(options.text)
        doc.setTextWidth(options.rect.width())
        return QSize(doc.idealWidth(), doc.size().height())
