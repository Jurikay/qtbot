# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import app
import pandas as pd
from datetime import datetime
from app.colors import Colors


class DataOpenOrders(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.my_model = OpenOrdersModel(self)
        self.data_dict = None
        self.df = None
        self.mw = app.mw
        self.setItemDelegate(OpenOrdersDelegate(self))



    def setup(self):
        print("DATA OPEN ORDER SETUP")

        try:
            self.update()
        except (AttributeError, KeyError) as e:
            print("UPDATE ERROR!", e)
            return

        self.setSortingEnabled(True)
        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.my_model)

        self.setModel(self.proxy_model)
        
    def update(self):
        self.my_model.modelAboutToBeReset.emit()
        self.df = self.mw.user_data.create_dataframe()
        self.my_model.update(self.df)
        self.my_model.modelReset.emit()



class OpenOrdersModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None, *args):
        super(OpenOrdersModel, self).__init__()
        self.mw = app.mw
        self.datatable = None
        self.header_data = ["Date & Time", "Pair", "Type", "Side", "Price", "Quantity", "Filled %", "Total", "id", "cancel"]

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Set header data."""
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                # return self.headers[section]
                # return self.datatable.columns[section]
                return self.header_data[section]


    def update(self, dataIn):
        self.datatable = dataIn


    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.index)


    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.columns.values)


    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            if index.isValid():
                return str(self.datatable.iloc[index.row(), index.column()])


class OpenOrdersDelegate(QtWidgets.QStyledItemDelegate):
    """Class to define the style of index values."""

    def __init__(self, parent):
        super(OpenOrdersDelegate, self).__init__(parent)
        self.parent = parent
        self.mw = app.mw

        self.center = int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.left = int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.right = int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    def initStyleOption(self, option, index):
        """Set style options based on index column."""
        if index.column() == 0:
            option.text = str(datetime.fromtimestamp(int(str(index.data())[:-3])).strftime('%d.%m.%y - %H:%M:%S.%f')[:-7])
        elif index.column() == 1:
            option.icon = QtGui.QIcon("images/ico/" + index.data().replace("BTC", "") + ".svg")
            option.text = str(index.data())

        else:
            super(OpenOrdersDelegate, self).initStyleOption(option, index)

    
    def paint(self, painter, option, index):
        """Reimplemented custom paint method."""
        painter.save()
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        font = QtGui.QFont()
        
        painter.setPen(QtGui.QColor(Colors.color_lightgrey))


        if index.column() == 1:
            font = QtGui.QFont()
            

            icon = QtGui.QIcon("images/ico/" + index.data().replace("BTC", "") + ".svg")
            iconRect = QtCore.QRect(option.rect.left(),
                                    option.rect.top(),
                                    option.rect.height(),
                                    option.rect.height())

        
            icon.paint(painter, iconRect, QtCore.Qt.AlignLeft)

            if option.state & QtWidgets.QStyle.State_MouseOver:
                painter.setPen(QtGui.QColor(Colors.color_yellow))
                font.setBold(True)
                painter.setFont(font)
            else:
                painter.setPen(QtGui.QColor(Colors.color_lightgrey))

            painter.drawText(option.rect, self.right, options.text)


        elif index.column() == 3:
            if index.data() == "SELL":
                painter.setPen(QtGui.QColor(Colors.color_pink))
            else:
                painter.setPen(QtGui.QColor(Colors.color_green))

            painter.drawText(option.rect, self.center, options.text)

        elif index.column() == 9:
            # painter.setPen(QtGui.QColor(Colors.color_yellow))
            # painter.drawText(option.rect, self.center, options.text)

            if option.state & QtWidgets.QStyle.State_MouseOver:
                painter.setPen(QtGui.QColor(Colors.color_yellow))
                font.setBold(True)
                font.setUnderline(True)
                painter.setFont(font)
            else:
                painter.setPen(QtGui.QColor(Colors.color_pink))


        elif index.column() == 0:
            painter.setPen(QtGui.QColor(Colors.color_lightgrey))
            painter.drawText(option.rect, self.left, options.text)

        
        else:
            # super(OpenOrdersDelegate, self).initStyleOption(option, index)
        
        
            painter.drawText(option.rect, self.center, options.text)
        painter.restore()
    #     if index.column() == 0:
    #         option.text = index.data().replace("BTC", "") + " / BTC"
    #         option.icon = QtGui.QIcon("images/ico/" + index.data().replace("BTC", "") + ".svg")



    #     elif index.column() == 2 or index.column() >= 7:
    #         operator = ""
    #         if index.data() == 0.00:
    #             operator = " "
    #         elif index.data() > 0:
    #             operator = "+"
    #         option.text = operator + '{number:.{digits}f}'.format(number=float(index.data()), digits=2) + "%"

    #     elif index.column() == 1:
    #         option.text = '{number:,.{digits}f}'.format(number=float(index.data()), digits=8) + " BTC"

    #     else:
    #         for i in range(3, 7):
    #             if index.column() == i:
    #                 option.text = '{number:,.{digits}f}'.format(number=float(index.data()), digits=2)


    #     # super(OpenOrdersDelegate, self).initStyleOption(option, index)


    # def paint(self, painter, option, index):
    #     """Reimplemented custom paint method."""
    #     painter.save()
    #     options = QtWidgets.QStyleOptionViewItem(option)
    #     self.initStyleOption(options, index)
    #     # font = QtGui.QFont()
        
    #     # painter.setPen(QtGui.QColor(Colors.color_lightgrey))

    #     self.center = int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    #     if index.column() == 0:
    #         font = QtGui.QFont()
            

    #         icon = QtGui.QIcon("images/ico/" + index.data().replace("BTC", "") + ".svg")
    #         iconRect = QtCore.QRect(option.rect.left() + 35 - option.rect.height(),
    #                                 option.rect.top(),
    #                                 option.rect.height(),
    #                                 option.rect.height())

        
    #         icon.paint(painter, iconRect, QtCore.Qt.AlignLeft)

    #         if option.state & QtWidgets.QStyle.State_MouseOver:
    #             painter.setPen(QtGui.QColor(Colors.color_yellow))
    #             font.setBold(True)
    #             painter.setFont(font)
    #         else:
    #             painter.setPen(QtGui.QColor(Colors.color_lightgrey))
            
    #         painter.drawText(option.rect, alignment, options.text)

    #         # super(OpenOrdersDelegate, self).paint(painter, option, index)

    #     elif index.column() == 1:
    #         painter.drawText(option.rect, alignment, options.text)

    #     elif index.column() == 2 or index.column() >= 7:

    #         if index.data() < 0:
    #             painter.setPen(QtGui.QColor(Colors.color_pink))
    #         elif index.data() == 0.00:
    #             painter.setPen(QtGui.QColor(Colors.color_grey))
    #         else:
    #             painter.setPen(QtGui.QColor(Colors.color_green))

    #         painter.drawText(option.rect, alignment, options.text)

    #     else:
    #         # set volume colors
    #         for i in range(3, 7):
    #             if index.column() == i:
    #                 if index.data() == 0.00:
    #                     painter.setPen(QtGui.QColor(Colors.color_grey))
    #                 else:
    #                     painter.setPen(QtGui.QColor("#eff0f1"))



