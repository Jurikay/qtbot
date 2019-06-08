import sys, os
from PyQt5 import QtGui, QtCore, QtWidgets

class Item(object):
    def __init__(self,ID=None,name=None,category=None,area=None):
        self.ID=ID
        self.name=name
        self.category=category
        self.area='South'

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.currentItems=[]
        self.items = []
        self.filterCategory = None
        self.searchField = None

        self.mainColumn=0
        self.order=QtCore.Qt.SortOrder.DescendingOrder

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len( self.currentItems )

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 5

    def data(self, index, role):
        if not index.isValid(): return 
        row=index.row()
        column=index.column()

        item=self.currentItems[row]

        if role == QtCore.Qt.DisplayRole:
            if column==0: return item.ID
            elif column==1: return item.name
            elif column==2: return item.category
            elif column==4 or column==5: return item.area

        if role == QtCore.Qt.UserRole:
            return item

    def insertRows(self, row, item, column=1, index=QtCore.QModelIndex()):
        self.beginInsertRows(QtCore.QModelIndex(), row, row+1)
        self.items.append(item)
        self.endInsertRows()

    def setFilter(self, comboText=None, searchText=None, mainColumn=None, order=None):
        if comboText: self.filterCategory=comboText
        if searchText: self.searchText=searchText
        if mainColumn!=None: self.mainColumn=mainColumn
        self.order=order

        self.currentItems=[item for item in self.items if item.category==self.filterCategory]
        if searchText:
            self.currentItems=[item for item in self.currentItems if searchText in '%s%s%s'%(item.ID, item.name, item.category)]

        values=[]
        if self.mainColumn==0: values=[[item.ID, item, False] for item in self.currentItems]
        elif self.mainColumn==1: values=[[item.name, item, False] for item in self.currentItems]
        elif self.mainColumn==2: values=[[item.category, item, False] for item in self.currentItems]
        elif self.mainColumn==3 or self.mainColumn==4: values=[[item.area, item, False] for item in self.currentItems]  

        keys=sorted([value[0] for value in values if isinstance(value, list)])
        if self.order==QtCore.Qt.AscendingOrder: keys=list(reversed(keys))

        filtered=[]
        for key in keys:
            for each in values:
                if each[0]!=key: continue
                if each[2]==True: continue
                item=each[1]

                filtered.append(item)
                each[2]=True

        if filtered: self.currentItems=filtered

        self.layoutChanged.emit()

class ItemDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        QtWidgets.QItemDelegate.__init__(self, parent)

    def flags(self, index):
        if (index.column() == 1):
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.ItemIsEnabled

    def createEditor(self, parent, option, index):
        tableView=parent.parent()
        model=tableView.model()

        item=model.data(index, QtCore.Qt.UserRole)

        combo=QtWidgets.QComboBox(parent)
        combo.addItems(['South','West','North','East'])
        combo.currentIndexChanged.connect(self.comboIndexChanged)    

        if item.area:
            comboIndex=combo.findText(item.area)
            if comboIndex>=0:
                combo.setCurrentIndex(comboIndex)
        else: combo.setCurrentIndex(0)

        return combo

    def comboIndexChanged(self):
        self.commitData.emit(self.sender())

    def setModelData(self, combo, model, index): 
        item=model.data(index, QtCore.Qt.UserRole)
        comboText=combo.currentText()
        item.area=comboText

class MyWindow(QtWidgets.QWidget):
    def __init__(self, *args):
        QtWidgets.QWidget.__init__(self, *args)
        vLayout=QtWidgets.QVBoxLayout(self)
        self.setLayout(vLayout)

        self.tableModel = TableModel()   

        self.searchLine=QtWidgets.QLineEdit()
        vLayout.addWidget(self.searchLine)

        self.searchLine.textEdited.connect(self.searchLineEditied)
        self.searchLine.returnPressed.connect(self.searchLineEditied)

        self.tableView=QtWidgets.QTableView(self)
        self.tableView.setSortingEnabled(True)
        # self.tableView.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Stretch) 
        self.tableView.setShowGrid(False) 
        self.tableView.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.tableView.setAlternatingRowColors(True)

        self.delegate=ItemDelegate(self.tableView)
        self.tableView.setItemDelegate(self.delegate)

        self.tableView.clicked.connect(self.viewClicked)
        vLayout.addWidget(self.tableView)

        for row in range(15):
            if row%2:  category='Pet' 
            else: category='Birds'
            item=Item(category=category, ID=row, name='%s_%s'%(category,row)) 
            self.tableModel.insertRows(row, item)

        self.tableView.setModel(self.tableModel)

        self.combo=QtWidgets.QComboBox()
        self.combo.addItems(['Pet','Birds'])
        self.combo.activated.connect(self.comboActivated)
        vLayout.addWidget(self.combo)

        currentComboCategory=self.combo.currentText()
        self.tableModel.setFilter(currentComboCategory)

        self.horizontalHeader=self.tableView.horizontalHeader()
        self.horizontalHeader.sortIndicatorChanged.connect(self.headerTriggered)
        self.addComboDelegates()

    def headerTriggered(self, mainColumn=None, order=None):
        self.tableModel.setFilter(mainColumn=mainColumn, order=order)
        self.deleteComboDelegates()
        self.addComboDelegates() 

    def comboActivated(self, comboIndex=None):
        self.deleteComboDelegates()
        comboText=self.combo.currentText()
        self.tableModel.setFilter(comboText=comboText)
        self.addComboDelegates()
        self.tableModel.layoutChanged.emit()

    def searchLineEditied(self, searchText=None):
        self.tableModel.setFilter(searchText=searchText)

    def viewClicked(self, indexClicked):
        item=self.tableModel.data(indexClicked, QtCore.Qt.UserRole)
        # print 'ID: %s, name: %s, category: %s'%(item.ID,item.name,item.category)

    def deleteComboDelegates(self):
        for row in range(self.tableModel.rowCount()):
            index=self.tableModel.index(row, 3, QtCore.QModelIndex())
            self.tableView.closePersistentEditor(index)

    def addComboDelegates(self):
        for row in range(self.tableModel.rowCount()):
            index=self.tableModel.index(row, 3, QtCore.QModelIndex())
            self.tableView.openPersistentEditor(index)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())