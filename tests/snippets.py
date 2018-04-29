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