#!/usr/bin/python3

# -*- coding: utf-8 -*-

import sys
import os
import re
from copy import deepcopy

import jsonpickle

from PyQt5 import QtCore, QtGui, QtWidgets

from main_ui import Ui_MainWindowFBP
from formula_ui import Ui_DialogFBP

from reactionsystem import \
    Reaction, \
    ReactionSet, \
    ReactionSystem, \
    ExceptionReactionSystem


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindowFBP):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setupUi(self)

        self._translate = QtCore.QCoreApplication.translate
 
        self.statusbarStyle = self.statusbar.styleSheet()

        self.reaction_set = ReactionSet()
        
        self.current_file_name = ''

        validatorLineEditSymbols = QtGui.QRegExpValidator(QtCore.QRegExp("^[a-zA-Z ]+$")) # pylint: disable=W1401

        self.lineEditReactants.setValidator(validatorLineEditSymbols)
        self.lineEditProducts.setValidator(validatorLineEditSymbols)
        self.lineEditInhibitors.setValidator(validatorLineEditSymbols)
        self.lineEditCalculatorSymbols.setValidator(validatorLineEditSymbols)
        self.lineEditCalculatorSteps.setValidator(QtGui.QIntValidator(0, 999))

        self.statusbar.messageChanged.connect(self.statusbarChanged)

        self.pushButtonAdd.clicked.connect(self.pushButtonAdd_clicked)
        self.pushButtonDelete.clicked.connect(self.pushButtonDelete_clicked)
        self.pushButtonCalculate.clicked.connect(self.pushButtonCalculate_clicked)
        
        self.lineEditReactants.textChanged.connect(self.pushButtonAdd_enable)
        self.lineEditProducts.textChanged.connect(self.pushButtonAdd_enable)
        self.listWidgetReactions._checked_item_number = 0
        self.listWidgetReactions.itemChanged.connect(self.listWidgetReactions_itemChanged)
        self.lineEditCalculatorSymbols.textChanged.connect(self.pushButtonCalculate_enable)
        self.lineEditCalculatorSteps.textChanged.connect(self.pushButtonCalculate_enable)

        self.actionNew.triggered.connect(self.actionNew_triggered)
        self.actionOpen.triggered.connect(self.actionOpen_triggered)
        self.actionSave_as.triggered.connect(self.actionSave_as_triggered)
        self.actionSave.triggered.connect(self.actionSave_triggered)
        self.actionQuit.triggered.connect(self.actionQuit_triggered)

        self.actionAbout.triggered.connect(self.actionAbout_triggered)


    def pushButtonCalculate_clicked(self):
        FormulaWindow(self).show()


    def closeEvent(self, event):
        event.ignore()
        self.actionQuit_triggered()


    def actionNew_triggered(self, value=None):
        if not self.check_save():
            return
        self.current_file_name = ''
        self.reaction_set.clear()
        self.listWidgetReactions.clear()
        self.actionSave.setEnabled(False)


    def actionOpen_triggered(self, value=None):
        if not self.check_save():
            return
        self.current_file_name, _ = \
            QtWidgets.QFileDialog.getOpenFileName(self, 
                'Open a Reaction System file', 
                '',
                'JSON files (*.json)')
        if self.current_file_name:
            file = open(self.current_file_name, 'r')
            file_content = file.read()
            file.close()
            
            try:
                reaction_set_opened = jsonpickle.decode(file_content)
            except Exception:
                self.notify('Error: invalid file')
                return

            if not isinstance(reaction_set_opened, ReactionSet):
                self.notify('Error: invalid file')
                return

            self.reaction_set = reaction_set_opened
            self.listWidgetReactions.clear()

            for reaction in self.reaction_set:
                self.listWidgetReactions_addReaction(reaction)

            self.actionSave.setEnabled(False)
            self.notify('File ' + self.current_file_name + ' opened')


    def actionSave_triggered(self, value=None):
        if not self.current_file_name:
            self.actionSave_as_triggered()
            return
        self.saveFile()
    

    def actionSave_as_triggered(self, value=None):
        self.current_file_name, _ = \
            QtWidgets.QFileDialog.getSaveFileName(self, 
                'Save Reaction System As', 
                'untitled.json',
                'JSON files (*.json)')
        self.saveFile()

    
    def saveFile(self):
        if self.current_file_name:
            file = open(self.current_file_name, 'w')
            file.write(jsonpickle.encode(self.reaction_set))
            file.close()
            self.actionSave.setEnabled(False)
            self.notify('File ' + self.current_file_name + ' saved')


    def actionQuit_triggered(self, value=None):
        if not self.check_save():
            return
        QtCore.QCoreApplication.quit()


    def check_save(self):
        if self.actionSave.isEnabled() and len(self.reaction_set):
            buttonReply = QtWidgets.QMessageBox.warning(self,
                'Save changes before closing?',
                'Your changes will be lost if you don’t save them.',
                QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Save,
                QtWidgets.QMessageBox.Cancel)

            if buttonReply == QtWidgets.QMessageBox.Save:
                self.actionSave_triggered()
            elif buttonReply == QtWidgets.QMessageBox.Discard:
                pass
            else:
                return False
        return True


    def actionAbout_triggered(self):
        QtWidgets.QMessageBox.about(self,
            self._translate('MainWindow', 'FBP Calculator'),
            'version 1.0.0\n' +
            'Writtern by William Guglielmo')

    
    def pushButtonAdd_clicked(self):
        reactants = self.lineEditReactants.text()
        products = self.lineEditProducts.text()
        inhibitors = self.lineEditInhibitors.text()

        try:
            reaction = Reaction(reactants, products, inhibitors)
        except Exception as e:
            self._manageExceptionReactionSystem(e)
            return

        if reaction in self.reaction_set:
            self.notify('Error: this reaction is already present')
            return
        
        self.reaction_set.add(reaction)

        self.listWidgetReactions_addReaction(reaction)
        self.notify('Added ' + str(reaction))

        self.pushButtonCalculate_enable()
        self.actionSave.setEnabled(True)


    def pushButtonAdd_enable(self, string=None):
        if self.lineEditReactants.text() != '' and self.lineEditProducts.text() != '':
            self.pushButtonAdd.setEnabled(True)
        else:
            self.pushButtonAdd.setEnabled(False)


    def listWidgetReactions_addReaction(self, reaction):
        item = QtWidgets.QListWidgetItem(str(reaction))
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(QtCore.Qt.Unchecked)
        self.listWidgetReactions.addItem(item)
    

    def listWidgetReactions_itemChanged(self, item):
        if item.checkState():
            self.listWidgetReactions._checked_item_number += 1
            self.pushButtonDelete.setEnabled(True)
        else:
            self.listWidgetReactions._checked_item_number -= 1
            if not self.listWidgetReactions._checked_item_number:
                self.pushButtonDelete.setEnabled(False)
    

    def pushButtonDelete_clicked(self):
        i = 0
        while self.listWidgetReactions._checked_item_number:
            if self.listWidgetReactions.item(i).checkState():
                item = self.listWidgetReactions.takeItem(i)
                splitted = re.split('⟶ | \|', item.text()) # pylint: disable=W1401
                self.reaction_set.remove(Reaction(splitted[0], splitted[1],
                        splitted[2] if len(splitted) == 3 else set()))
                self.listWidgetReactions._checked_item_number -= 1
            else: i += 1
        self.pushButtonDelete.setEnabled(False)

        self.pushButtonCalculate_enable()
        self.actionSave.setEnabled(True)

    
    def pushButtonCalculate_enable(self, string=None):
        if self.lineEditCalculatorSymbols.text() != '' \
                and self.lineEditCalculatorSteps.text() != '' \
                and int(self.lineEditCalculatorSteps.text()) != 0 \
                and len(self.reaction_set):
            self.pushButtonCalculate.setEnabled(True)
        else:
            self.pushButtonCalculate.setEnabled(False)


    def statusbarChanged(self, string):
        if string and string[0:5] == 'Error':
            self.statusbar.setStyleSheet("QStatusBar{background:rgba(255,0,0,255);color:black;font-weight:bold;}")
        else:
            self.statusbar.setStyleSheet(self.statusbarStyle)


    def notify(self, message):
        self.statusbar.showMessage(message, msecs=2000)

        
    def _manageExceptionReactionSystem(self, e):
        if isinstance(e, ExceptionReactionSystem.ImpossibleReaction):
            message = 'Error: this reaction can never happened'
        elif isinstance(e, ExceptionReactionSystem.SymbolsMustBeLetters):
            message = 'Error: symbols must be strings of letters'
        elif isinstance(e, ExceptionReactionSystem.ReactantSetCannotBeEmpty):
            message = 'Error: reactants cannot be empty'
        elif isinstance(e, ExceptionReactionSystem.ProductSetCannotBeEmpty):
            message = 'Error: products cannot be empty'
        elif isinstance(e, ExceptionReactionSystem.InvalidReaction):
            message = 'Error: this reaction is invalid'
        elif isinstance(e, ExceptionReactionSystem.InvalidReactionSet):
            message = 'Error: this reaction set is invalid'
        elif isinstance(e, ExceptionReactionSystem.InvalidNumber):
            message = 'Error: only natural numbers are accepted '
        elif isinstance(e, ExceptionReactionSystem.InvalidFormula):
            message = 'Error: formula invalid'
        else:
            message = 'Error'

        self.notify(message)
        

class FormulaWindow(QtWidgets.QDialog, Ui_DialogFBP):
    def __init__(self, parent):
        super(FormulaWindow, self).__init__(parent)
        self.setupUi(self)

        self.comboBoxFormulaType.setCurrentIndex(1)
        self.textBrowserFormula.setVisible(False)
        self.tableWidgetFormula.setVisible(False)

        self.symbols = deepcopy(parent.lineEditCalculatorSymbols.text())
        self.steps = deepcopy(parent.lineEditCalculatorSteps.text())
        self.rs = ReactionSystem(deepcopy(parent.reaction_set))

        self.lineEditSymbols.setText(self.symbols)
        self.lineEditSteps.setText(self.steps)
        
        self.labelLoadingImage.setMovie(QtGui.QMovie(":/loader.gif"))
        self.labelLoadingImage.movie().start()

        self.comboBoxFormulaType.currentIndexChanged.connect(self.comboBoxFormulaType_currentIndexChanged)

        self.threadCalculateFBP = ThreadCalculateFBP(self)
        self.threadCalculateFBP.finished.connect(self.threadCalculateFBP_finished)
        self.threadCalculateFBP.start()

    
    def comboBoxFormulaType_currentIndexChanged(self, index):
        if index == 0:
            self.textBrowserFormula.setVisible(True)
            self.listWidgetFormula.setVisible(False)
            self.tableWidgetFormula.setVisible(False)
        elif index == 1:
            self.textBrowserFormula.setVisible(False)
            self.listWidgetFormula.setVisible(True)
            self.tableWidgetFormula.setVisible(False)
        elif index == 2:
            self.textBrowserFormula.setVisible(False)
            self.listWidgetFormula.setVisible(False)
            self.tableWidgetFormula.setVisible(True)


    def threadCalculateFBP_finished(self):
        self.labelComputing.setVisible(False)
        self.labelLoadingImage.setVisible(False)
        self.labelLoadingImage.movie().stop()

        self.comboBoxFormulaType.setEnabled(True)
        self.listWidgetFormula.setEnabled(True)

        self.textBrowserFormula.setText(self.formula)

        formula2 = (self.formula
            .replace('(', '')
            .replace(')', '')
            .split(' ∨ '))

        for f in formula2:
            self.listWidgetFormula.addItem(QtWidgets.QListWidgetItem(f))

        for f in self.structuredFormula:
            item = ''
            for i in range(0, len(f)-1):
                s, n = f[i]
                item += '{}_{} ∧ '.format(s, str(n))
            s, n = f[len(f)-1]
            item += '{}_{}'.format(s, str(n))

            self.tableWidgetFormula.addItem(QtWidgets.QListWidgetItem(item))

        self.raise_()



class ThreadCalculateFBP(QtCore.QThread):
    def __init__(self, parent):
        self.parent = parent
        super(ThreadCalculateFBP, self).__init__()

    def run(self):
        parent = self.parent
        formula = parent.rs.fbp(parent.symbols, int(parent.steps) - 1)

        formula = (str(formula)
            .replace('~', '¬')
            .replace('&', '∧')
            .replace('|', '∨'))

        structuredFormula = (formula
            .replace(' ', '')
            .replace('(', '')
            .replace(')', '')
            .split('∨'))

        # for i_structuredFormula in range(0, len(structuredFormula)):
        #     andListFormula = structuredFormula[i_structuredFormula].split('∧')
        #     l = []
        #     for i_andListFormula in range(0, len(andListFormula)):
        #         s, n = tuple(andListFormula[i_andListFormula].split('_'))
        #         l.append((s, int(n) + 1))
        #     structuredFormula[i_structuredFormula] = l

        convert = lambda l: (l[0], int(l[1])+1)
        structuredFormula = (
            list(map(lambda o: 
                list(map(lambda a:
                    convert(a.split('_')),
                o.split('∧'))), 
            structuredFormula)))

        parent.formula = formula
        parent.structuredFormula = structuredFormula




if __name__ == '__main__':
    sys.setrecursionlimit(10000)
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()

    mainWindow.setGeometry(
        QtWidgets.QStyle.alignedRect(
            QtCore.Qt.LeftToRight,
            QtCore.Qt.AlignCenter,
            mainWindow.size(),
            app.desktop().availableGeometry()))
    
    mainWindow.show()
    sys.exit(app.exec_())