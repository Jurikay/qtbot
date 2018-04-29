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
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.my_model = HistoryModel(self)
        self.mw = app.mw
        self.setModel(self.my_model)
        self.setMouseTracking(True)
        self.setItemDelegate(HistoryDelegate(self))
        self.setup()
        # self.cellClicked.connect(self.cell_clicked)
        # self.clicked.connect(self.cell_clicked)
        self.clicked.connect(self.cell_clicked)


    def setup(self):
        print("setup")

        self.my_model.update(self.mw.new_history)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(15)

        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setDefaultSectionSize(75)
        self.emitChange()

    def funct(self, index):
        print("CLIC")
    # def onTableClicked(self, index):
    #     print("CLICK! " + str(index))

    def emitChange(self):
        # self.my_model.modelAboutToBeReset.emit()
        self.my_model.modelReset.emit()
        


    def cell_clicked(self, index):
        
        try:
            # print(str(index))
            # print(str(index.row()))
            row = index.row()
            col = index.column()
            if col == 0:
                self.mw.limit_buy_input.setValue(float(self.mw.new_history[row][0]))
                self.mw.limit_sell_input.setValue(float(self.mw.new_history[row][0]))
            elif col == 1:
                self.mw.limit_buy_amount.setValue(float(self.mw.new_history[row][1]))
                self.mw.limit_sell_amount.setValue(float(self.mw.new_history[row][1]))


        except IndexError as e:
            print("CELL CLICK ERROR: " + str(e))





class HistoryModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None, *args):
        super(HistoryModel, self).__init__()
        self.headers = ["Price", "Quantity", "Time"]
        self.mw = app.mw
        self.model_data = None
        self.blockSignals(True)
        

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.headers[section]

    def columnCount(self, parent=None):
        return 3

    def rowCount(self, parent):
        if self.model_data:
            return len(self.model_data)
        else:
            return 0

    def update(self, new_data):
        print("update")
        # self.layoutAboutToBeChanged.emit()
        self.model_data = new_data
        # self.layoutChanged.emit()
        # self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())


    def data(self, index, role):
        i = index.column()
        j = index.row()

        # Format and set trade history values
        if role == QtCore.Qt.DisplayRole:
            return(QtCore.QVariant(self.model_data[j][i]))
            # if i == 0:
            #     formatted_price = '{number:.{digits}f}'.format(number=float(self.model_data[j]["price"]), digits=val["decimals"])
            #     return QtCore.QVariant(formatted_price)
            # elif i == 1:
            #     formatted_quantity = '{number:.{digits}f}'.format(number=float(self.model_data[j]["quantity"]), digits=val["assetDecimals"])
            #     return QtCore.QVariant(formatted_quantity)
            # elif i == 2:
            #     time_str = str(datetime.fromtimestamp(int(str(self.model_data[j]["time"])[:-3])).strftime('%H:%M:%S.%f')[:-7])
            #     return QtCore.QVariant(time_str)
            # else:
            #     return QtCore.QVariant()


class HistoryDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent):
        super(HistoryDelegate, self).__init__(parent)
        self.parent = parent
        self.mw = app.mw

    def initStyleOption(self, option, index):
        if index.column() == 0:
            
            option.text = '{number:.{digits}f}'.format(number=float(index.data()), digits=val["decimals"])

        elif index.column() == 1:
            option.text = '{number:.{digits}f}'.format(number=float(index.data()), digits=val["assetDecimals"])

        elif index.column() == 2:
            option.text = str(datetime.fromtimestamp(int(str(self.parent.my_model.model_data[index.row()][3])[:-3])).strftime('%H:%M:%S.%f')[:-7])

        else:
            super(HistoryDelegate, self).initStyleOption(option, index)


    def paint(self, painter, option, index):
        painter.save()
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        font = QtGui.QFont()
    

        if index.column() == 0:
            if option.state & QtWidgets.QStyle.State_MouseOver:
                # if app.main_app.overrideCursor() != QtCore.Qt.PointingHandCursor:
                app.main_app.setOverrideCursor(QtCore.Qt.PointingHandCursor)
            # else:
            #     app.main_app.restoreOverrideCursor()

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
        else:
            app.main_app.restoreOverrideCursor()
    
        if index.column() == 1:
            if option.state & QtWidgets.QStyle.State_MouseOver:
                painter.setPen(QtGui.QColor(QtCore.Qt.white))
            else:
                painter.setPen(QtGui.QColor(Colors.color_lightgrey))
        
        elif index.column() == 2:
            painter.setPen(QtGui.QColor(Colors.color_grey))
            

        painter.drawText(option.rect, QtCore.Qt.AlignRight, options.text)
        painter.restore()

        # super(HistoryDelegate, self).paint(painter, option, index)
