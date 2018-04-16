# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from app.init import val
from functools import partial
import app
# import time


class FishingBot():
    """Class containing fishing bot methods."""
    def __init__(self, gui):
        FishingBot.gui = gui
        self.mw = gui

    @classmethod
    def add_order(self, arg2):
        """Ad a new order to the fishing bot table."""
        print("adde order")
        print(str(self) + " " + str(arg2))
        gui = FishingBot.gui

        coin_combo_box = QtWidgets.QComboBox()



        for coin in val["coins"]:
            icon = QtGui.QIcon("images/ico/" + coin[:-3] + ".svg")
            coin_combo_box.addItem(icon, coin[:-3])

        coinIndex = coin_combo_box.findText(val["coin"])
        coin_combo_box.setCurrentIndex(coinIndex)
        coin_combo_box.setEditable(True)
        coin_combo_box.setInsertPolicy(QtWidgets.QComboBox.NoInsert)

        side_combo_box = QtWidgets.QComboBox()
        side_combo_box.addItem("Buy")
        side_combo_box.addItem("Sell")

        row_count = gui.fishbot_table.rowCount()

        gui.fishbot_table.insertRow(row_count)
        gui.fishbot_table.setCellWidget(row_count, 0, coin_combo_box)
        gui.fishbot_table.setCellWidget(row_count, 1, side_combo_box)

        cancel_button = QtWidgets.QPushButton("cancel")
        # cancel_button.setProperty("row", row_count)
        cancel_button.clicked.connect(partial(self.remove_order, gui))
        gui.fishbot_table.setCellWidget(row_count, 3, cancel_button)

        gui.fishbot_table.setItem(row_count, 2, QtWidgets.QTableWidgetItem(str(row_count)))
        self.set_properties(gui)

    @staticmethod
    def set_properties(bot):
        for i in range(bot.fishbot_table.rowCount()):
            widget = bot.fishbot_table.cellWidget(i, 3)
            widget.setProperty("row", i)
            bot.fishbot_table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(i)))


    def remove_order(self, bot):
        print("selfmw: " + str(self.mw))
        row = bot.sender().property("row")
        for i in range(bot.fishbot_table.rowCount()):
            widget = bot.fishbot_table.cellWidget(i, 3)
            try:
                if widget.property("row") == row:
                    bot.fishbot_table.removeRow(i)
            except Exception as e:
                print(str(e))
        self.set_properties(bot)

    @staticmethod
    def clear_all_orders(self):
        print(str(app.mw))
        row_count = self.fishbot_table.rowCount()
        print("clearing %i rows." % int(self.fishbot_table.rowCount()))
        for i in reversed(range(row_count)):
            print(str(i))
            self.fishbot_table.removeRow(i)

    @staticmethod
    def update_table(self):
        for i in range(self.fishbot_table.rowCount()):
            # set current price from val tickers
            pass

    @staticmethod
    def parse_table_contents(bot):
        for i in range(bot.fishbot_table.rowCount()):
            # get values of every row and store in array
            pass

    @staticmethod
    def start_fishing(bot):
        pass