# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from app.init import val
from functools import partial
# import time


class fishing_bot():
    """Class containing fishing bot methods."""
    def __init__(self, bot):
        self.bot = bot

    def add_order(self, bot):
        """Ad a new order to the fishing bot table."""
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

        row_count = bot.fishbot_table.rowCount()

        bot.fishbot_table.insertRow(row_count)
        bot.fishbot_table.setCellWidget(row_count, 0, coin_combo_box)
        bot.fishbot_table.setCellWidget(row_count, 1, side_combo_box)

        cancel_button = QtWidgets.QPushButton("cancel")
        # cancel_button.setProperty("row", row_count)
        cancel_button.clicked.connect(partial(self.remove_order, bot))
        bot.fishbot_table.setCellWidget(row_count, 3, cancel_button)

        bot.fishbot_table.setItem(row_count, 2, QtWidgets.QTableWidgetItem(str(row_count)))
        self.set_properties(bot)


    def set_properties(self, bot):
        for i in range(bot.fishbot_table.rowCount()):
            widget = bot.fishbot_table.cellWidget(i, 3)
            widget.setProperty("row", i)
            bot.fishbot_table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(i)))


    def remove_order(self, bot):
        row = bot.sender().property("row")
        for i in range(bot.fishbot_table.rowCount()):
            widget = bot.fishbot_table.cellWidget(i, 3)
            try:
                if widget.property("row") == row:
                    bot.fishbot_table.removeRow(i)
            except Exception as e:
                print(str(e))
        self.set_properties(bot)


    def clear_all_orders(self, bot):
        row_count = bot.fishbot_table.rowCount()
        print("clearing %i rows." % int(bot.fishbot_table.rowCount()))
        for i in reversed(range(row_count)):
            print(str(i))
            bot.fishbot_table.removeRow(i)


    def update_table(self, bot):
        for i in range(bot.fishbot_table.rowCount()):
            # set current price from val tickers
            pass

    def parse_table_contents(self, bot):
        for i in range(bot.fishbot_table.rowCount()):
            # get values of every row and store in array
            pass
