# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""CLass containing hotkey definitions."""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from functools import partial
# import app


class HotKeys:

    def __init__(self, mw):
        self.mw = mw

    def hotkey_pressed(self, key):
        if key == "F":
            print("F")
        elif key == "1":
            self.mw.bot_tabs.setCurrentIndex(0)
        elif key == "2":
            self.mw.bot_tabs.setCurrentIndex(1)
        elif key == "3":
            self.mw.bot_tabs.setCurrentIndex(2)
        elif key == "4":
            self.mw.bot_tabs.setCurrentIndex(3)
        elif key == "5":
            self.mw.bot_tabs.setCurrentIndex(4)
        elif key == "6":
            self.mw.bot_tabs.setCurrentIndex(5)

        elif key == "B":
            self.mw.limit_buy_input.setFocus()
        elif key == "S":
            self.mw.limit_sell_input.setFocus()

        elif key == "A":
            if self.mw.limit_buy_input.hasFocus():
                self.mw.limit_buy_amount.setFocus()
            elif self.mw.limit_sell_input.hasFocus():
                self.mw.limit_sell_amount.setFocus()


    def init_hotkeys(self):
        hotkey_F = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F), self.mw)
        hotkey_F.activated.connect(partial(self.hotkey_pressed, "F"))

        hotkey_1 = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_1), self.mw)
        hotkey_1.activated.connect(partial(self.hotkey_pressed, "1"))

        hotkey_2 = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_2), self.mw)
        hotkey_2.activated.connect(partial(self.hotkey_pressed, "2"))

        hotkey_3 = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_3), self.mw)
        hotkey_3.activated.connect(partial(self.hotkey_pressed, "3"))

        hotkey_4 = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_4), self.mw)
        hotkey_4.activated.connect(partial(self.hotkey_pressed, "4"))

        hotkey_5 = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_5), self.mw)
        hotkey_5.activated.connect(partial(self.hotkey_pressed, "5"))

        hotkey_6 = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_6), self.mw)
        hotkey_6.activated.connect(partial(self.hotkey_pressed, "6"))

        hotkey_B = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_B), self.mw)
        hotkey_B.activated.connect(partial(self.hotkey_pressed, "B"))

        hotkey_S = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_S), self.mw)
        hotkey_S.activated.connect(partial(self.hotkey_pressed, "S"))

        hotkey_P = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_P), self.mw)
        hotkey_P.activated.connect(partial(self.hotkey_pressed, "P"))

        hotkey_A = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_A), self.mw)
        hotkey_A.activated.connect(partial(self.hotkey_pressed, "A"))
