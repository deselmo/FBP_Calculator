import sys
from PyQt5 import QtWidgets
from .mainwindowfbp import MainWindowFBP
from .increase_recursion_limit import increase_recursion_limit

def main():
    increase_recursion_limit()
    app = QtWidgets.QApplication(sys.argv)
    mainWindowFBP = MainWindowFBP(app)
    mainWindowFBP.show()
    sys.exit(app.exec_())
