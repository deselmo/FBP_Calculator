#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets
from fbp_calculator import MainWindowFBP
from fbp_calculator import increase_recursion_limit

increase_recursion_limit()
app = QtWidgets.QApplication(sys.argv)
MainWindowFBP = MainWindowFBP(app)
MainWindowFBP.show()
sys.exit(app.exec_())
