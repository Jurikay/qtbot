from ui import *

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # QFontDatabase.addApplicationFont('static/Roboto-Bold.ttf')
    #

    app.setStyle(QStyleFactory.create('Fusion'))

    widget = beeserBot()
    widget.show()

    sys.exit(app.exec_())
