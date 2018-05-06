# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import app
from app.colors import Colors


class TestTableView(QtWidgets.QTableView):
    """
    TableView that holds coin index data.
    """
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.my_model = MyTableModel(self)
        self.mw = app.mw
        self.threadpool = app.threadpool

        self.setItemDelegate(IndexDelegate(self))
        self.setMouseTracking(True)
        self.df = None

    def setup(self):
        self.horizontalHeader().setDefaultSectionSize(50)

        self.df = self.mw.index_data.coin_index
        self.my_model.update(self.df)

        self.setModel(self.my_model)
        self.setSortingEnabled(True)

        self.mw.new_coin_table = True

        self.setColumnWidth(0, 150)
        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 100)
        self.setColumnWidth(3, 100)
        self.setColumnWidth(4, 100)
        self.clicked.connect(self.cell_clicked)


    def leaveEvent(self, event):
        app.main_app.restoreOverrideCursor()

    def cell_clicked(self, index):

        if index.column() == 0:
            coin = index.data().replace("BTC", "")
            print("SWITCH TO", coin)
            self.mw.gui_manager.change_to(coin)


    def coin_update(self):
        """Create a new DataFrame, update the model, (re) sort and filter and update the view."""

        self.df = self.mw.index_data.coin_index
        self.my_model.update(self.df)
        self.my_model.sort(self.my_model.order_col, self.my_model.order_dir)


    def search_edited(self, searchText=None):
        self.my_model.setFilter(searchText=searchText)


class MyTableModel(QtCore.QAbstractTableModel):

    header_labels = ['Icon', 'Pair', 'Price', '24h Change', "24h volume", "1m volume", "5m volume", "15m volume", "1h volume", "5m change", "15m change", "1h change"]

    def __init__(self, parent=None, *args):
        super(MyTableModel, self).__init__()
        self.mw = app.mw
        self.datatable = None
        self.order_col = 0
        self.order_dir = True

        self.searchText = None
        self.parent = parent


    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Set header data."""
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                # return self.headers[section]
                return self.datatable.columns[section]


    def update(self, dataIn):
        self.datatable = dataIn


    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.index)


    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.columns.values)


    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            if index.isValid():
                if index.column() > 0:
                    return float(self.datatable.iloc[index.row(), index.column()])
                else:
                    return str(self.datatable.iloc[index.row(), index.column()])


    def insertRows(self, row, item, column=1, index=QtCore.QModelIndex()):
        self.beginInsertRows(QtCore.QModelIndex(), row, row + 1)
        self.datatable.append(item)
        self.endInsertRows()


    def setFilter(self, searchText=None):

        self.searchText = searchText
        if searchText:
            for row in range(self.rowCount()):
                self.mw.test_table_view.setRowHidden(row, False)

                if str(searchText.upper()) in str(self.datatable.iloc[row, 0]):
                    self.mw.test_table_view.setRowHidden(row, False)
                else:
                    self.mw.test_table_view.setRowHidden(row, True)

        else:
            for row in range(self.rowCount()):
                self.mw.test_table_view.setRowHidden(row, False)


    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        print("sort")
        if Ncol >= 0:
            self.modelAboutToBeReset.emit()
            try:
                self.datatable = self.datatable.sort_values(self.datatable.columns[Ncol], ascending=not order)
            except TypeError as e:
                print("Sort error: " + str(e) + " " + str(Ncol))        

            # save order dir, order col
            self.order_col = Ncol
            self.order_dir = order

            if self.searchText:
                self.setFilter(searchText=self.searchText)

            self.modelReset.emit()



class IndexDelegate(QtWidgets.QStyledItemDelegate):
    """Class to define the style of index values."""

    def __init__(self, parent):
        super(IndexDelegate, self).__init__(parent)
        self.parent = parent
        self.mw = app.mw

    def initStyleOption(self, option, index):
        """Set style options based on index column."""

        if index.column() == 0:
            option.text = index.data().replace("BTC", "") + " / BTC"

        elif index.column() == 1:
            option.text = '{number:.{digits}f}'.format(number=float(index.data()), digits=2) + "%"

        elif index.column() == 2:
            option.text = '{number:,.{digits}f}'.format(number=float(index.data()), digits=8) + " BTC"

        else:
            super(IndexDelegate, self).initStyleOption(option, index)


    def paint(self, painter, option, index):
        """Reimplemented custom paint method."""
        painter.save()
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        # font = QtGui.QFont()
        
        painter.setPen(QtGui.QColor(Colors.color_lightgrey))

        alignment = int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        if index.column() == 0:
            font = QtGui.QFont()
            

            icon = QtGui.QIcon("images/ico/" + index.data().replace("BTC", "") + ".svg")
            iconRect = QtCore.QRect(35 - option.rect.height(),
                                     option.rect.top(),
                                     option.rect.height(),
                                     option.rect.height())

        
            icon.paint(painter, iconRect, QtCore.Qt.AlignLeft)

            if option.state & QtWidgets.QStyle.State_MouseOver:
                painter.setPen(QtGui.QColor(Colors.color_yellow))
                font.setBold(True)
                painter.setFont(font)
                painter.drawText(option.rect, alignment, options.text)
            else:
                painter.setPen(QtGui.QColor(Colors.color_lightgrey))
                painter.drawText(option.rect, alignment, options.text)

        elif index.column() == 1:
            operator = ""
            if index.data() < 0:
                painter.setPen(QtGui.QColor(Colors.color_pink))
            elif index.data() == 0:
                painter.setPen(QtGui.QColor(Colors.color_lightgrey))
                operator = " "
            else:
                painter.setPen(QtGui.QColor(Colors.color_green))
                operator = "+"

            painter.drawText(option.rect, alignment, operator + options.text)

        else:
            painter.drawText(option.rect, alignment, options.text)

        # if index.column() == 0:
        #     if self.parent.my_model.model_data[index.row()][2] is True:

        #         if option.state & QtWidgets.QStyle.State_MouseOver:
        #             painter.setPen(QtGui.QColor("#ff58a8"))
        #             font.setBold(True)
        #         else:
        #             painter.setPen(QtGui.QColor(Colors.color_pink))
        #     else:

        #         if option.state & QtWidgets.QStyle.State_MouseOver:
        #             painter.setPen(QtGui.QColor("#aaff00"))
        #             font.setBold(True)
        #         else:
        #             painter.setPen(QtGui.QColor(Colors.color_green))
        #     painter.setFont(font)
        #     painter.drawText(option.rect, QtCore.Qt.AlignRight, options.text)

        # elif index.column() == 1:
        #     if option.state & QtWidgets.QStyle.State_MouseOver:
        #         painter.setPen(QtGui.QColor(QtCore.Qt.white))
        #         font.setBold(True)
        #     else:
        #         painter.setPen(QtGui.QColor(Colors.color_lightgrey))
        #     painter.setFont(font)
        #     painter.drawText(option.rect, QtCore.Qt.AlignRight, options.text)

        # elif index.column() == 2:
        #     painter.setPen(QtGui.QColor(Colors.color_grey))
        #     painter.drawText(option.rect, QtCore.Qt.AlignHCenter, options.text)

        painter.restore()
