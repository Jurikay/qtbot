import PyQt5.QtMultimedia as QtMultimedia
import PyQt5.QtCore as QtCore
from app.helpers import resource_path
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import app
# made by Jirrik

class Sounds:

    def __init__(self, mw):
        self.sound = QtMultimedia.QSound
        self.mw = mw        # self.sound.set

        self.sound_files = self.sounds()


        self.effect = QtMultimedia.QSoundEffect(mw)
        self.effect.setSource(QtCore.QUrl.fromLocalFile(self.sound_files["flat_click"]))
        self.effect.setVolume(0.01)



    def set_sound_effects(self):
        """Set different ui sound effects based on config values."""
        # TODO: Implement
        return

    def ps2(self):
        
        self.effect.play()



    def play_effect(self):
        sounds = self.sounds()

        effect = QtMultimedia.QSoundEffect(self.mw)
        effect.setSource(QtCore.QUrl.fromLocalFile(sounds["mouse_click"]))
        effect.setVolume(.51)
        effect.play()

    def sounds(self):
        return {
            "mouse_click": resource_path("sounds/SoundsUI/mouse_click.wav"),
            "tiny_click": resource_path("sounds/SoundsUI/tiny_click.wav"),
            "proud_click": resource_path("sounds/SoundsUI/proud_click.wav"),
            "bone_toggle": resource_path("sounds/SoundsUI/bone_toggle.wav"),
            "computer_toggle": resource_path("sounds/SoundsUI/computer_toggle.wav"),
            "flat_click": resource_path("sounds/SoundsUI/flat_click.wav"),
            "xylo_toggle": resource_path("sounds/SoundsUI/xylo_toggle.wav"),
        }

    def ps(self, sound):
        sounds = self.sounds()

        sf = sounds.get(sound, None)
        self.play_sound(sf)


    def play_sound(self, sound):
        self.sound.play(sound)
    
    def play_click(self):
        self.sound.play(self.sounds()["bone_toggle"])