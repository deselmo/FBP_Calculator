#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets
from fbp_calculator.mainwindowfbp import MainWindowFBP
from fbp_calculator.increase_recursion_limit import increase_recursion_limit

def main():
    increase_recursion_limit()
    app = QtWidgets.QApplication(sys.argv)
    mainWindowFBP = MainWindowFBP(app)
    mainWindowFBP.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()