import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

# from app.colors import colors
from PyQt5 import Qt
from app.colors import Colors
import app


class CoinDelegate(QtWidgets.QStyledItemDelegate):
    """
    TAKEN FROM https://stackoverflow.com/questions/43300034/qt-itemdelegate-displaytext-with-a-qtablewidget-how-can-i-access-the-table-in/43300126#43300126
    AND https://stackoverflow.com/questions/41760474/pyqt-QtWidgets.QStyledItemDelegate-word-wrap-and-html/43417837
    The following methods are subclassed to replace display and editor of the
    QTableWidget.
    """
    def __init__(self, parent):
        """
        Pass instance `parent` of parent class (TestTable)
        """
        super(CoinDelegate, self).__init__(parent)
        self.parent = parent  # instance of the parent (not the base) class
        self.mw = app.mw

    def initStyleOption(self, option, index):
        """
        Initialize `option` with the values using the `index` index. When the
        item (0,1) is processed, it is styled especially. All other items are
        passed to the original `initStyleOption()` which then calls `displayText()`.
        """
        # print("delegate stuff")
        # print(self.parent.name())

        if self.parent.name == "CoinIndex":
            self.style_coin_index(option, index)
            self.filter_highlight(option, index)
        # set default values:
        elif self.parent.name == "TestTableView":
            self.test_style(option, index)

        else:
            super(CoinDelegate, self).initStyleOption(option, index)




    # def displayText(self, text, locale):
    #     """
    #     Display `text` in the selected with the selected number
    #     of digits

    #     text:   string / QVariant from QTableWidget to be rendered
    #     locale: locale for the text
    #     """
    #     data = text  # .toString() # Python 2: need to convert to "normal" string
    #     return "{0:>{1}}".format(data, 4)

    def test_style(self, option, index):
        color = "#cdcdcd"

        if index.column() < 4:
            # option.text = "<span style=' font-size: 13px; color:" + color + ";'>" + str(index.data()) + " / BTC</span>"
            option.text = index.data()

        if index.column() == 2:
            formatted_price = '{number:.{digits}f}'.format(number=float(index.data()), digits=8)
            # option.text = "<span style=' font-size: 13px; border-bottom: 3px solid #f3ba2e; color:" + Colors.color_yellow + ";'>" + str(formatted_price) + "</span>"
            option.text = formatted_price
            
       

        elif index.column() >= 4:
            super(CoinDelegate, self).initStyleOption(option, index)

    def filter_highlight(self, option, index):
        if self.mw.coinindex_filter.text() != "":
            for row in range(self.parent.rowCount()):
                if self.parent.isRowHidden(row):
                    continue
                else:
                    marked_row = row
                    break

            if index.row() == marked_row and index.column() == 1:
                print("coloring marked row: " + str(marked_row))
                option.text = "<span style=' font-size: 13px; border-bottom: 3px solid #f3ba2e; color:" + Colors.color_yellow + ";'>" + str(index.data()) + " / BTC</span>"


    def style_coin_index(self, option, index):
        color = "#cdcdcd"

        if index.column() == 1:
            option.text = "<span style=' font-size: 13px; color:" + color + ";'>" + str(index.data()) + " / BTC</span>"

        elif index.column() == 2:
            # orig = str(index.data())
            option.text = "<span style=' font-size: 13px; color:" + color + ";'>" + str(index.data()) + " BTC</span>"

        elif index.column() == 3 or index.column() == 10 or index.column() == 11 or index.column() == 12:
            value = index.data()
            try:
                percent_value = float(value)
            except TypeError:
                percent_value = 0

            if percent_value > 0:
                operator = "+"
                color = "#94c940"

            elif percent_value == 0.00:
                operator = "&nbsp;&nbsp;"
                color = "#cdcdcd"

            else:
                operator = ""
                color = "#ff007a"

            option.text = "<span style=' font-size: 13px; color:" + color + ";'>" + operator + "{0:.2f}".format(percent_value) + "%"
            option.textAlignmentRole = Qt.Qt.AlignRight


        elif index.column() == 4 or index.column() == 6 or index.column() == 7 or index.column() == 8 or index.column() == 9:
            value = index.data()

            try:
                percent_value = float(value)
            except TypeError:
                percent_value = 0

            if percent_value < 1:
                color = "#999"
                weight = "normal"

            elif index.column() == 6 and percent_value > 5:
                color = "white"
                weight = "bold"

            elif index.column() == 7 and percent_value > 50:
                color = "white"
                weight = "bold"

            else:
                color = "#cdcdcd"
                weight = "normal"

            option.text = "<span style=' font-size: 13px; font-weight: " + weight + "; color:" + color + ";'>" + "{0:,.2f}".format(percent_value) + " BTC</span>"

        else:
            # continue with the original `initStyleOption()`
            super(CoinDelegate, self).initStyleOption(option, index)

    def paint(self, painter, option, index):
        """Reimplement paint method to allow html rendering within tableWidgets."""
        painter.save()
        # print("PAINT METHOD: OPTION:" + str(dir(option)) + " INDEX:" + str(dir(index)))
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        if index.column() == 0:
            icon = QtGui.QIcon("images/ico/" + options.text + ".svg")
            iconRect = QtCore.QRect(option.rect.right() - option.rect.height(),
                                     option.rect.top(),
                                     option.rect.height(),
                                     option.rect.height())
            icon.paint(painter, iconRect, QtCore.Qt.AlignLeft)
        # else:
            # ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()
            # ctx.palette.setColor(QtGui.QPalette(QtGui.QColor("#fff")))
        #     doc = QtGui.QTextDocument()
        #     doc.documentLayout().draw(painter, ctx)
        # else:
        # print(str(option.state))
        # print("paint")
        else:
            # painter.setPen(QtGui.QColor(Colors.color_green))
            # super(CoinDelegate, self).paint(painter, option, index)
            # var = index.model()
            # color = var.data(index, QtCore.Qt.BackgroundRole)
            # text = var.data(index, QtCore.Qt.DisplayRole)
            # painter.fillRect(option.rect, color)
            option.palette.setColor(QtGui.QPalette(QtGui.QPalette.Normal, QtGui.QPalette.Foreground, QtCore.Qt.yellow))
            painter.drawText(option.rect, QtCore.Qt.AlignCenter, options.text)

        #     style = QtWidgets.QApplication.style() if options.widget is None else options.widget.style()

        #     doc = QtGui.QTextDocument()
        #     doc.setHtml(options.text)

        #     options.text = ""
        #     style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, options, painter)

        #     ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()
        #     if option.state & QtWidgets.QStyle.State_Selected:
        #         ctx.palette.setColor(QtGui.QPalette.Text, option.palette.color(QtGui.QPalette.Active, QtGui.QPalette.HighlightedText))
        #     else:
        #         ctx.palette.setColor(QtGui.QPalette.Text, option.palette.color(QtGui.QPalette.Active, QtGui.QPalette.HighlightedText))


        #     textRect = style.subElementRect(QtWidgets.QStyle.SE_ItemViewItemText, options)
        #     
        #     painter.translate(textRect.topLeft())
        #     painter.setClipRect(textRect.translated(-textRect.topLeft()))
        #     doc.documentLayout().draw(painter, ctx)
        painter.restore()



    def _create_item(self, text):
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel(text))
        layout.addStretch(2)


        item = QtWidgets.QLabel(text)
        # item.setLayout(layout)
        return item

    def sizeHint(self, option, index):
        """sizeHint has to be reimplemented as well."""
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        doc = QtGui.QTextDocument()
        doc.setHtml(options.text)
        doc.setTextWidth(options.rect.width())
        return QtCore.QSize(doc.idealWidth(), doc.size().height())
