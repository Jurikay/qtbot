# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from app.init import val


class fishing_bot():
    """Class containing fishing bot methods."""
    # def __init__():
    #     combo_box = QtWidgets.QComboBox()

    def add_order(self):
        """Ad a new order to the fishing bot table."""

        coin_combo_box = QtWidgets.QComboBox()
        
        for coin in val["coins"]:
            icon = QtGui.QIcon("images/ico/" + coin[:-3] + ".svg")
            coin_combo_box.addItem(icon, coin[:-3])

        side_combo_box = QtWidgets.QComboBox()
        side_combo_box.addItem("Buy")
        side_combo_box.addItem("Sell")

        row_count = self.fishbot_table.rowCount()

        self.fishbot_table.insertRow(row_count)
        self.fishbot_table.setCellWidget(row_count, 0, coin_combo_box)
        self.fishbot_table.setCellWidget(row_count, 1, side_combo_box)


        self.coin_selector.model().sort(0)
        self.fishbot_table.setCellWidget(row_count, 3, QtWidgets.QPushButton("cancel"))
        


    def remove_order(self):
        pass
