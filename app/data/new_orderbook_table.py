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
from app.init import val


class DataAsks(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.my_model = AsksModel(self)
        self.data_dict = None
        self.df = None
        self.mw = app.mw
        # self.setItemDelegate(AsksDelegate(self))
        # self.proxy_model = QtCore.QSortFilterProxyModel()
        # self.setSortingEnabled(True)
        self.clicked.connect(self.cell_clicked)

    def setup(self):
        
        try:
            self.update()
        except (AttributeError, KeyError) as e:
            print("UPDATE ERROR!", e)
            return



        self.setModel(self.my_model)
        # self.proxy_model.setSourceModel(self.my_model)
        


        self.set_widths()

        self.sortByColumn(0, QtCore.Qt.DescendingOrder)



    def update(self):

        self.my_model.modelAboutToBeReset.emit()
        self.df = pd.DataFrame(val["asks"].copy())

        self.create_dataframe(val["asks"])

        self.my_model.update(self.df)

        self.my_model.modelReset.emit()

    def create_dataframe(self, data):
        print("create dataframe")
        for ask in val["asks"]:
            print(ask)


    def set_widths(self):
        self.horizontalHeader().setDefaultSectionSize(100)
        self.setColumnWidth(0, 130)
        self.setColumnWidth(1, 130)
        # self.setColumnWidth(2, 60)
        # self.setColumnWidth(3, 60)
        # for i in range(4, 9):
        #     self.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

    def cell_clicked(self, index):
        """Change pair or cancel order"""
        pass


class AsksModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None, *args):
        super(AsksModel, self).__init__()
        self.mw = app.mw
        self.datatable = None
        self.header_data = ["Price", "Amount", "Total"]

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Set header data."""
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.header_data[section]


    def update(self, dataIn):
        self.datatable = dataIn


    def rowCount(self, parent=QtCore.QModelIndex()):
        if not self.datatable.empty:
            return len(self.datatable.index)
        else:
            return 0

    def columnCount(self, parent=QtCore.QModelIndex()):
        if not self.datatable.empty:
            return len(self.datatable.columns.values)
        else:
            return 0

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if index.isValid():
                print("data:", str(self.datatable.iloc[index.row(), index.column()]))
                return str(self.datatable.iloc[index.row(), index.column()])


# class AsksDelegate(QtWidgets.QStyledItemDelegate):
#     """Class to define the style of index values."""

#     def __init__(self, parent):
#         super(AsksDelegate, self).__init__(parent)
#         self.parent = parent
#         self.mw = app.mw

#         self.center = int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
#         self.left = int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
#         self.right = int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

#     def initStyleOption(self, option, index):
#         """Set style options based on index column."""
#         if index.column() == 0:
#             option.text = str(datetime.fromtimestamp(int(str(index.data())[:-3])).strftime('%d.%m.%y - %H:%M:%S.%f')[:-7])
#         elif index.column() == 1:
#             option.icon = QtGui.QIcon("images/ico/" + index.data().replace("BTC", "") + ".svg")
#             option.text = str(index.data())

#         else:
#             super(AsksDelegate, self).initStyleOption(option, index)


#     def paint(self, painter, option, index):
#         """Reimplemented custom paint method."""
#         painter.save()
#         options = QtWidgets.QStyleOptionViewItem(option)
#         self.initStyleOption(options, index)
#         font = QtGui.QFont()
#         painter.setPen(QtGui.QColor(Colors.color_lightgrey))

