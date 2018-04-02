# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Main application entry point."""

from PyQt5.QtWidgets import QApplication
from app.gui import *

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # QFontDatabase.addApplicationFont('static/Roboto-Bold.ttf')
    #

    app.setStyle(QStyleFactory.create('Fusion'))

    widget = beeserBot()
    widget.show()

    sys.exit(app.exec_())
