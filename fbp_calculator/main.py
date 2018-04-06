import sys
import multiprocessing
from PyQt5 import QtWidgets
from fbp_calculator.mainwindowfbp import MainWindowFBP

def main():
    app = QtWidgets.QApplication(sys.argv)
    mainWindowFBP = MainWindowFBP(app)
    mainWindowFBP.show()
    sys.exit(app.exec_())
