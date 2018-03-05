#!/usr/bin/python3

import sys

from PyQt5 import QtWidgets

from simple_ui import Ui_MainWindow
from reaction_system import Reaction, ReactionSet, ReactionSystem


if __name__ == '__main__':
    
    rs = ReactionSystem(ReactionSet({
        Reaction({'A'},{},{'B'}),
        Reaction({'C','D'},{},{'E','F'}),
        Reaction({'G'},{'B'},{'E'})
    }))

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    ui.statusbar.showMessage(str(rs.fbp('E', 3)))
    
    MainWindow.show()
    sys.exit(app.exec_())

