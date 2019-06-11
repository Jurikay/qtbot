
import PyQt5.QtMultimedia as QtMultimedia
import PyQt5.QtCore as QtCore
from app.helpers import resource_path
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import app
# made by Jirrik

# implement config check:
# assignments
# global volume
# global on off

class Sounds:

    def __init__(self, mw):
        self.sound = QtMultimedia.QSound
        self.mw = mw        # self.sound.set

        self.sound_files = self.sound_file_paths()


        self.effect = QtMultimedia.QSoundEffect(mw)

        self.button = QtMultimedia.QSoundEffect(mw)
        self.buy_filled = QtMultimedia.QSoundEffect(mw)
        self.sell_filled = QtMultimedia.QSoundEffect(mw)
        self.order_created = QtMultimedia.QSoundEffect(mw)
        self.order_canceled = QtMultimedia.QSoundEffect(mw)

        self.set_sources()

    def set_sources(self):
        self.effect.setSource(QtCore.QUrl.fromLocalFile(self.sound_files["flat_click"]))
        self.effect.setVolume(0.01)
        self.button.setSource(QtCore.QUrl.fromLocalFile(self.sound_files["proud_click"]))
        self.button.setVolume(0.05)
        self.buy_filled.setSource(QtCore.QUrl.fromLocalFile(self.sound_files["xylo_toggle"]))
        self.buy_filled.setVolume(0.2)
        self.sell_filled.setSource(QtCore.QUrl.fromLocalFile(self.sound_files["bone_toggle"]))
        self.sell_filled.setVolume(0.2)
        self.order_created.setSource(QtCore.QUrl.fromLocalFile(self.sound_files["tiny_click"]))
        self.order_created.setVolume(0.2)
        self.order_canceled.setSource(QtCore.QUrl.fromLocalFile(self.sound_files["rasp_toggle"]))
        self.order_canceled.setVolume(0.075)


    def order_sound(self):
        print("PLAYING ORDER SOUND!!!")
        print("######")
        self.order_created.play()

    def play_sound(self, sound):
        """sound can be button, buy, sell, order."""
        if sound == "button":
            self.button.play()
        if sound == "buy":
            self.buy_filled.play()
        if sound == "sell":
            self.sell_filled.play()
        if sound == "order":
            self.order_created.play()
        if sound == "cancel":
            self.order_canceled.play()


    def set_sound_effects(self):
        """Set different ui sound effects based on config values."""
        # TODO: Implement
        return

    def ps2(self):
        
        self.effect.play()




    def sound_file_paths(self):
        return {
            "mouse_click": resource_path("sounds/SoundsUI/mouse_click.wav"),
            "tiny_click": resource_path("sounds/SoundsUI/tiny_click.wav"),  # order created
            "proud_click": resource_path("sounds/SoundsUI/proud_click.wav"),  # button
            "bone_toggle": resource_path("sounds/SoundsUI/bone_toggle.wav"),  # order filled
            "computer_toggle": resource_path("sounds/SoundsUI/computer_toggle.wav"),
            "flat_click": resource_path("sounds/SoundsUI/flat_click.wav"),
            "xylo_toggle": resource_path("sounds/SoundsUI/xylo_toggle.wav"),  # buy filled
            "rasp_toggle": resource_path("sounds/SoundsUI/rasp_toggle.wav"),  # buy filled
        }
