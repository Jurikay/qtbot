from PyQt5 import QtCore, QtGui, QtWidgets, QtSql

class CheckSqlQueryModel(QtSql.QSqlQueryModel):
    def __init__(self, *args, **kwargs):
        QtSql.QSqlQueryModel.__init__(self, *args, **kwargs)
        self.checks = {}

    def checkState(self, pindex):
        if pindex not in self.checks.keys():
            self.checks[pindex] = QtCore.Qt.Unchecked
        return self.checks[pindex]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.CheckStateRole and index.isValid():
            return self.checkState(QtCore.QPersistentModelIndex(index))
        return QtSql.QSqlQueryModel.data(self, index, role)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.CheckStateRole and index.isValid():
            self.checks[QtCore.QPersistentModelIndex(index)] = value
            return True
        return QtSql.QSqlQueryModel(self, index, value, role)

    def flags(self, index):
        fl = QtSql.QSqlQueryModel.flags(self, index) & ~QtCore.Qt.ItemIsSelectable 
        fl |= QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable
        return fl

class CheckComboBox(QtWidgets.QComboBox):
    selectedChanged = QtCore.pyqtSignal(list)

    def hidePopup(self):
        results = []
        for i in range(self.count()):
            if self.itemData(i, QtCore.Qt.CheckStateRole) == QtCore.Qt.Checked:
                results.append(self.itemText(i))
        self.selectedChanged.emit(results)
        QtWidgets.QComboBox.hidePopup(self)

class CheckDelegate(QtWidgets.QStyledItemDelegate):
    def editorEvent(self, event, model, option, index):
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            val = index.data(QtCore.Qt.CheckStateRole)
            new_val = QtCore.Qt.Checked if val == QtCore.Qt.Unchecked else QtCore.Qt.Unchecked
            model.setData(index, new_val, QtCore.Qt.CheckStateRole)
            return True
        return QtWidgets.QStyledItemDelegate.editorEvent(self, event, model, option, index)


class Widget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        lay = QtWidgets.QVBoxLayout(self)

        combo = CheckComboBox()
        combo.setView(QtWidgets.QListView())
        combo.setItemDelegate(CheckDelegate(combo))
        model = CheckSqlQueryModel()
        model.setQuery("SELECT name FROM categories")
        combo.setModel(model)

        self.lw = QtWidgets.QListWidget()
        combo.selectedChanged.connect(self.on_selectedChanged)

        lay.addWidget(combo)
        lay.addWidget(self.lw)

    def on_selectedChanged(self, items):
        self.lw.clear()
        self.lw.addItems(items)

def createConnection():
    db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(":memory:")
    if not db.open():
        QtWidgets.QMessageBox.critical(None, "Cannot open database",
                             "Unable to establish a database connection.\n"
                             "This example needs SQLite support. Please read "
                             "the Qt SQL driver documentation for information how "
                             "to build it.\n\n"
                             "Click Cancel to exit.", QMessageBox.Cancel)
        return False
    query = QtSql.QSqlQuery()
    query.exec_("create table categories (id int primary key, name varchar(20))");
    for i in range(1, 10):
         query.exec_("insert into categories values({i}, 'categories-{i}')".format(i=i));

    return True

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    if not createConnection():
        sys.exit(-1)
    w = Widget()
    w.show()
    sys.exit(app.exec_())