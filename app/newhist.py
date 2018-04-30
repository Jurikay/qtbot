# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
from datetime import datetime

import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import app
from app.colors import Colors
from app. init import val


class NewHist(QtWidgets.QTableView):
    """View to display the global trade history of a pair."""

    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.my_model = HistoryModel(self)
        self.mw = app.mw
        self.setModel(self.my_model)
        self.setMouseTracking(True)
        self.setItemDelegate(HistoryDelegate(self))
        self.setup()
        self.clicked.connect(self.cell_clicked)


    def setup(self):
        """Setup the view."""
        self.my_model.update(self.mw.trade_history)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(15)

        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setDefaultSectionSize(75)
        self.emitChange()

    def emitChange(self):
        """Make QT redraw the table once it's model has changed."""
        # there might be a less expensive way
        self.my_model.modelReset.emit()


    def cell_clicked(self, index):
        """Copy price or quantity on click."""
        try:
            row = index.row()
            col = index.column()
            # copy price
            if col == 0:
                self.mw.limit_buy_input.setValue(float(self.mw.trade_history[row][0]))
                self.mw.limit_sell_input.setValue(float(self.mw.trade_history[row][0]))
            # copy quantity
            elif col == 1:
                self.mw.limit_buy_amount.setValue(float(self.mw.trade_history[row][1]))
                self.mw.limit_sell_amount.setValue(float(self.mw.trade_history[row][1]))


        except IndexError as e:
            print("CELL CLICK ERROR: " + str(e))


class HistoryModel(QtCore.QAbstractTableModel):
    """Model containing global trade history values."""
    def __init__(self, parent=None, *args):
        super(HistoryModel, self).__init__()
        self.headers = ["Price", "Quantity", "Time"]
        self.mw = app.mw
        self.model_data = None
        # self.blockSignals(True)


    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Set header data."""
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.headers[section]

    def columnCount(self, parent=None):
        """Return model column count."""
        return 3

    def rowCount(self, parent):
        """Return model row count."""
        if self.model_data:
            return len(self.model_data)
        else:
            return 0

    def update(self, new_data):
        """Update model data. Does not create a copy."""
        print("update")
        self.model_data = new_data

    def data(self, index, role):
        """Return model data by index."""
        if role == QtCore.Qt.DisplayRole:
            return(QtCore.QVariant(self.model_data[index.row()][index.column()]))
        else:
            return QtCore.QVariant()


class HistoryDelegate(QtWidgets.QStyledItemDelegate):
    """Class to define a custom item style."""

    def __init__(self, parent):
        super(HistoryDelegate, self).__init__(parent)
        self.parent = parent
        self.mw = app.mw

    def initStyleOption(self, option, index):
        """Set style options based on index column."""

        if index.column() == 0:
            option.text = '{number:.{digits}f}'.format(number=float(index.data()), digits=val["decimals"])

        elif index.column() == 1:
            option.text = '{number:.{digits}f}'.format(number=float(index.data()), digits=val["assetDecimals"])

        elif index.column() == 2:
            option.text = str(datetime.fromtimestamp(int(str(self.parent.my_model.model_data[index.row()][3])[:-3])).strftime('%H:%M:%S.%f')[:-7])

        else:
            super(HistoryDelegate, self).initStyleOption(option, index)


    def paint(self, painter, option, index):
        """Reimplemented custom paint method."""
        painter.save()
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        font = QtGui.QFont()


        if index.column() == 0:
            if self.parent.my_model.model_data[index.row()][2] is True:

                if option.state & QtWidgets.QStyle.State_MouseOver:
                    painter.setPen(QtGui.QColor("#ff58a8"))
                    font.setBold(True)
                else:
                    painter.setPen(QtGui.QColor(Colors.color_pink))
            else:

                if option.state & QtWidgets.QStyle.State_MouseOver:
                    painter.setPen(QtGui.QColor("#aaff00"))
                    font.setBold(True)
                else:
                    painter.setPen(QtGui.QColor(Colors.color_green))


            painter.setFont(font)

        elif index.column() == 1:
            if option.state & QtWidgets.QStyle.State_MouseOver:
                painter.setPen(QtGui.QColor(QtCore.Qt.white))
            else:
                painter.setPen(QtGui.QColor(Colors.color_lightgrey))

        elif index.column() == 2:
            painter.setPen(QtGui.QColor(Colors.color_grey))

        painter.drawText(option.rect, QtCore.Qt.AlignRight, options.text)
        painter.restore()
