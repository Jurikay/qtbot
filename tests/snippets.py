class HistoryModel(QtCore.QAbstractTableModel):

    def data(self, index, role):
        # Set the text color dependant on side (maker True/False)
            if role == QtCore.Qt.ForegroundRole:
                if i == 0:
                    green = QtGui.QColor(Colors.color_green)
                    pink = QtGui.QColor(Colors.color_pink)

                    if self.model_data[j]["maker"] is True:
                        return QtGui.QBrush(pink)
                    else:
                        return QtGui.QBrush(green)

            # Set the text alignment
            if role == QtCore.Qt.TextAlignmentRole:
                if i == 0:
                    return QtCore.Qt.AlignRight
                elif i == 1:
                    return QtCore.Qt.AlignRight
                else:
                    return QtCore.Qt.AlignHCenter


        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.my_model)
        self.proxy_model.setDynamicSortFilter(False)
        self.proxy_model.setFilterCaseSensitivity(False)
        self.proxy_model.setSortLocaleAware(True)
        self.proxy_model.setRecursiveFilteringEnabled(False)



    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return self.header_labels[section]

        elif role == QtCore.Qt.InitialSortOrderRole:
            # set initial sort order of specific columns (sections)
            if section > 0:
                return QtCore.QVariant(QtCore.Qt.DescendingOrder)
            else:
                return QtCore.QVariant(QtCore.Qt.AscendingOrder)

        return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)
