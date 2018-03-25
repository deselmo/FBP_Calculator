#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import resource
import re
import math
from copy import deepcopy

import threading
import thread_with_exc

import jsonpickle

from reactionsystem import \
    Reaction, \
    ReactionSet, \
    ReactionSystem, \
    ExceptionReactionSystem

from PyQt5 import QtCore, QtGui, QtWidgets

from main_ui import Ui_MainWindowFBP
from formula_ui import Ui_DialogFBP

from pyeda.inter import Not
from pyeda.boolalg.expr import \
    Constant, \
    Literal, \
    Variable, \
    Complement, \
    NotOp, \
    AndOp, \
    OrOp


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindowFBP):
    def __init__(self, app, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setupUi(self)

        self._translate = QtCore.QCoreApplication.translate
 
        self.statusbarStyle = self.statusbar.styleSheet()

        self.reaction_list = []
        
        self.current_file_name = ''

        self.validatorLineEditSymbols = QtGui.QRegExpValidator(QtCore.QRegExp("^[a-zA-Z ]+$")) # pylint: disable=W1401

        self.lineEditReactants.setValidator(self.validatorLineEditSymbols)
        self.lineEditProducts.setValidator(self.validatorLineEditSymbols)
        self.lineEditInhibitors.setValidator(self.validatorLineEditSymbols)
        self.lineEditCalculatorSymbols.setValidator(self.validatorLineEditSymbols)

        self.statusbar.messageChanged.connect(self.statusbarChanged)

        self.pushButtonAdd.clicked.connect(self.pushButtonAdd_clicked)
        self.pushButtonDelete.clicked.connect(self.pushButtonDelete_clicked)
        self.pushButtonCalculate.clicked.connect(self.pushButtonCalculate_clicked)
        
        self.lineEditReactants.textChanged.connect(self.pushButtonAdd_enable)
        self.lineEditProducts.textChanged.connect(self.pushButtonAdd_enable)
        self.listWidgetReactions._checked_item_number = 0
        self.listWidgetReactions.itemChanged.connect(self.listWidgetReactions_itemChanged)
        self.lineEditCalculatorSymbols.textChanged.connect(self.pushButtonCalculate_enable)
        self.spinBoxCalculatorSteps.valueChanged.connect(self.pushButtonCalculate_enable)

        self.actionNew.triggered.connect(self.actionNew_triggered)
        self.actionOpen.triggered.connect(self.actionOpen_triggered)
        self.actionSave_as.triggered.connect(self.actionSave_as_triggered)
        self.actionSave.triggered.connect(self.actionSave_triggered)
        self.actionQuit.triggered.connect(self.actionQuit_triggered)

        self.actionAbout.triggered.connect(self.actionAbout_triggered)

        self.tableWidgetProperties.horizontalScrollBar().valueChanged.connect(self.tableWidgetProperties_scrollBar_valueChanged)

        self.tableWidgetProperties_addColumn()
        self.tableWidgetProperties.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.setGeometry(
            QtWidgets.QStyle.alignedRect(
                QtCore.Qt.LeftToRight,
                QtCore.Qt.AlignCenter,
                self.size(),
                app.desktop().availableGeometry()))


    def resizeEvent(self, event):
        self.pushButtonCalculate_enable()

    def closeEvent(self, event):
        event.ignore()
        self.actionQuit_triggered()


    def actionNew_triggered(self, value=None):
        if not self.check_save():
            return
        self.current_file_name = ''
        self.reaction_list.clear()
        self.listWidgetReactions_clear()

    def actionOpen_triggered(self, value=None):
        if not self.check_save():
            return
        self.current_file_name, _ = \
            QtWidgets.QFileDialog.getOpenFileName(self, 
                'Open a Reaction System file', 
                '',
                'JSON files (*.json)')
        if not self.current_file_name:
            return

        file = open(self.current_file_name, 'r')
        file_content = file.read()
        file.close()
        
        try:
            reaction_list_opened = jsonpickle.decode(file_content)
        except Exception:
            self.notify('Error: invalid file')
            return


        if not isinstance(reaction_list_opened, list) or \
            not isinstance(ReactionSet(reaction_list_opened), ReactionSet):
            self.notify('Error: invalid file')
            return

        self.reaction_list = reaction_list_opened
        self.listWidgetReactions_clear()

        for reaction in self.reaction_list:
            self.listWidgetReactions_addReaction(reaction)

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

    def actionQuit_triggered(self, value=None):
        if not self.check_save():
            return
        QtCore.QCoreApplication.quit()

    def actionAbout_triggered(self):
        QtWidgets.QMessageBox.about(self,
            self._translate('MainWindow', 'FBP Calculator'),
            'version 1.0.0\n' +
            'Writtern by William Guglielmo')


    def saveFile(self):
        if self.current_file_name:
            file = open(self.current_file_name, 'w')
            file.write(jsonpickle.encode(self.reaction_list))
            file.close()
            self.actionSave.setEnabled(False)
            self.notify('File ' + self.current_file_name + ' saved')

    def check_save(self):
        if self.actionSave.isEnabled() and len(self.reaction_list):
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

    
    def pushButtonAdd_clicked(self):
        reactants = self.lineEditReactants.text()
        products = self.lineEditProducts.text()
        inhibitors = self.lineEditInhibitors.text()

        try:
            reaction = Reaction(reactants, products, inhibitors)
        except Exception as e:
            self._manageExceptionReactionSystem(e)
            return

        if reaction in self.reaction_list:
            self.notify('Error: this reaction is already present')
            return
        
        self.reaction_list.append(reaction)

        self.listWidgetReactions_addReaction(reaction)
        self.notify('Added ' + str(reaction))

        self.pushButtonCalculate_enable()
        self.actionSave.setEnabled(True)

    def pushButtonAdd_enable(self, string=None):
        if self.lineEditReactants.text() != '' and self.lineEditProducts.text() != '':
            self.pushButtonAdd.setEnabled(True)
        else:
            self.pushButtonAdd.setEnabled(False)


    def pushButtonDelete_clicked(self):
        i = 0
        while self.listWidgetReactions._checked_item_number:
            if self.listWidgetReactions.item(i).checkState():
                item = self.listWidgetReactions.takeItem(i)
                splitted = re.split('⟶ | \|', item.text()) # pylint: disable=W1401
                self.reaction_list.remove(Reaction(
                    splitted[0], splitted[1], splitted[2]
                    if len(splitted) == 3  else []))
                self.listWidgetReactions._checked_item_number -= 1
            else: i += 1
        self.pushButtonDelete.setEnabled(False)

        self.pushButtonCalculate_enable()
        self.actionSave.setEnabled(True)


    def pushButtonCalculate_clicked(self):
        steps = self.tableWidgetProperties.columnCount()

        for j in range(0, steps):
            symbols_true = Reaction._create_symbol_set(self.tableWidgetProperties.cellWidget(0, j).text())
            symbols_false = Reaction._create_symbol_set(self.tableWidgetProperties.cellWidget(1, j).text())
            intersectionSet = symbols_true.intersection(symbols_false)
            if len(intersectionSet):
                self.notify('Error in context properties step {}: {}'.format(str(j+1), ' '.join(intersectionSet)))
                return


        FormulaWindow(self).show()

    def pushButtonCalculate_enable(self, string=None):
        if self.lineEditCalculatorSymbols.text() != '' \
                and self.spinBoxCalculatorSteps.value() != 0 \
                and len(self.reaction_list):
            self.pushButtonCalculate.setEnabled(True)

            self.tableWidgetProperties.setEnabled(True)
            self.tableWidgetProperties_initialize()

        else:
            self.pushButtonCalculate.setEnabled(False)
            self.tableWidgetProperties.setEnabled(False)


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
    
    def listWidgetReactions_clear(self):
        self.listWidgetReactions.clear()
        self.listWidgetReactions._checked_item_number = 0
        self.pushButtonDelete.setEnabled(False)
        self.actionSave.setEnabled(False)
        self.pushButtonCalculate_enable()


    def tableWidgetProperties_initialize(self):
        
        if self.tableWidgetProperties.columnCount() > self.spinBoxCalculatorSteps.value():
            self.tableWidgetProperties.setColumnCount(self.spinBoxCalculatorSteps.value())

        for _ in range(self.tableWidgetProperties.columnCount(), self.spinBoxCalculatorSteps.value()):
            self.tableWidgetProperties_addColumn()
            if self.tableWidgetProperties.horizontalScrollBar().maximum() != 0:
                break
        
        self.tableWidgetProperties.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
    
    def tableWidgetProperties_scrollBar_valueChanged(self, value=None):
        if not self.tableWidgetProperties.isEnabled():
            return

        if value == None:
            value = self.tableWidgetProperties.horizontalScrollBar().value()


        for _ in range(self.tableWidgetProperties.columnCount(), self.spinBoxCalculatorSteps.value()):
            if value == self.tableWidgetProperties.horizontalScrollBar().maximum():
                self.tableWidgetProperties_addColumn()
            else: break

        self.tableWidgetProperties.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
    
    def tableWidgetProperties_addColumn(self):
        column = self.tableWidgetProperties.columnCount()
        self.tableWidgetProperties.setColumnCount(column+1)

        self.tableWidgetProperties.setHorizontalHeaderItem(column, QtWidgets.QTableWidgetItem(str(column+1)))
        for i in range(0, self.tableWidgetProperties.rowCount()):
            cellWidget = self.tableWidgetProperties.cellWidget(i, column)
            if cellWidget == None:
                lineEdit = QtWidgets.QLineEdit()
                lineEdit.setValidator(self.validatorLineEditSymbols)
                lineEdit.returnPressed.connect(self.pushButtonCalculate.click)
                self.tableWidgetProperties.setCellWidget(i, column, lineEdit)        


    def statusbarChanged(self, string):
        if string and string[0:5] == 'Error':
            self.statusbar.setStyleSheet("QStatusBar{background:rgba(255,0,0,255);color:black;font-weight:bold;}")
        else:
            self.statusbar.setStyleSheet(self.statusbarStyle)


    def notify(self, message):
        self.statusbar.showMessage(message, msecs=4000)

        
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

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.formulaType_defaultIndex = 2
        self.comboBoxFormulaType.setCurrentIndex(self.formulaType_defaultIndex)
        self.textBrowserFormula.setVisible(self.formulaType_defaultIndex == 0)
        self.listFormula.setVisible(self.formulaType_defaultIndex == 1)
        self.tableWidgetFormula.setVisible(self.formulaType_defaultIndex == 2)

        self.parent = parent
        self.symbols = parent.lineEditCalculatorSymbols.text()
        self.steps = parent.spinBoxCalculatorSteps.value()
        self.rs = ReactionSystem(ReactionSet(deepcopy(parent.reaction_list)))
        
        columnCount = parent.tableWidgetProperties.columnCount()

        self.context_true_set = set()
        self.context_false_set = set()

        for j in range(0, columnCount):
            symbols_true = Reaction._create_symbol_set(parent.tableWidgetProperties.cellWidget(0, j).text())
            for symbol in symbols_true:
                self.context_true_set.add((j, symbol))
            
            symbols_false = Reaction._create_symbol_set(parent.tableWidgetProperties.cellWidget(1, j).text())
            for symbol in symbols_false:
                self.context_false_set.add((j, symbol))

        self.lineEditSymbols.setText(self.symbols)
        self.lineEditSteps.setText(str(self.steps))
        
        self.labelLoadingImage.setMovie(QtGui.QMovie(":/loader.gif"))
        self.labelLoadingImage.movie().start()

        self.comboBoxFormulaType.currentIndexChanged.connect(self.comboBoxFormulaType_currentIndexChanged)


        self.listFormula.verticalScrollBar().valueChanged.connect(self.listFormula_scrollBar_valueChanged)
        self.tableWidgetFormula.horizontalScrollBar().valueChanged.connect(self.tableWidgetFormula_horizontalScrollBar_valueChanged)
        self.tableWidgetFormula.verticalScrollBar().valueChanged.connect(self.tableWidgetFormula_verticalScrollBar_valueChanged)


        self.qthreadCalculateFBP = QThreadCalculateFBP(self)
        self.qthreadCalculateFBP.finished.connect(self.qthreadCalculateFBP_finished)
        self.qthreadCalculateFBP.start()


    def resizeEvent(self, event):
        self.listFormula_scrollBar_valueChanged()
        self.tableWidgetFormula_horizontalScrollBar_valueChanged()
        self.tableWidgetFormula_verticalScrollBar_valueChanged()

    def closeEvent(self, event):
        self.qthreadCalculateFBP.stop()
        self.qthreadCalculateFBP.wait()
        event.accept()
    
    def qthreadCalculateFBP_finished(self):
        if self.qthreadCalculateFBP.stopped:
            return

        try:
            self.formula
        except NameError:
            self.parent.notify('Error in fbp calculation')
            self.close()
            return

        self.labelComputing.setVisible(False)
        self.labelLoadingImage.setVisible(False)
        self.labelLoadingImage.movie().stop()

        self.comboBoxFormulaType.setEnabled(True)
        self.comboBoxFormulaType_currentIndexChanged(self.formulaType_defaultIndex)

        self.raise_()


    def comboBoxFormulaType_currentIndexChanged(self, index):
        if index == 0:
            self.textBrowserFormula_show()
        elif index == 1:
            self.listFormula_show()
        elif index == 2:
            self.tableWidgetFormula_show()


    def textBrowserFormula_show(self):
        self.listFormula.setVisible(False)
        self.tableWidgetFormula.setVisible(False)
        self.textBrowserFormula.setVisible(True)

        if not self.textBrowserFormula.isEnabled():
            self.textBrowserFormula.setEnabled(True)
            self.textBrowserFormula_initialize()
            
    def textBrowserFormula_initialize(self):
        if isinstance(self.formula, bool):
            self.textBrowserFormula.setText(str(self.formula))
            return

        stringFormula = ''
        prebrackets = len(self.formula) > 1
        for i in range(0, len(self.formula)):
            if i > 0: stringFormula += ' ∨ '
            backets = prebrackets and len(self.formula[i]) > 1
            if backets: stringFormula += '('
            for j in range(0, len(self.formula[i])):
                if j > 0: stringFormula += ' ∧ '
                n, s = self.formula[i][j]
                stringFormula += '{}<sub>{}</sub>'.format(s, str(n))
            if backets: stringFormula += ')'
        self.textBrowserFormula.setText(stringFormula)


    def listFormula_show(self):
        self.textBrowserFormula.setVisible(False)
        self.tableWidgetFormula.setVisible(False)
        self.listFormula.setVisible(True)

        if not self.listFormula.isEnabled():
            self.listFormula.setEnabled(True)
            self.listFormula_initialize()
        else:
            self.listFormula_scrollBar_valueChanged()
            
    def listFormula_initialize(self):
        if isinstance(self.formula, bool):
            self.listFormula.addItem(QtWidgets.QListWidgetItem(str(self.formula)))
            return

        for _ in self.formula:
            self.listFormula_addRow()

            if self.listFormula.verticalScrollBar().maximum() != 0:
                break
    
    def listFormula_scrollBar_valueChanged(self, value=None):
        if (not self.listFormula.isEnabled()) or isinstance(self.formula, bool):
            return

        if value == None:
            value = self.listFormula.verticalScrollBar().value()

        listFormula_len = self.listFormula.count()

        for _ in range(listFormula_len, len(self.formula)):
            if value == self.listFormula.verticalScrollBar().maximum():
                self.listFormula_addRow()
            else: break

    def listFormula_addRow(self):
        f = self.formula[self.listFormula.count()]
        string = ''
        for i in range(0, len(f)):
            if i > 0: string += ' '
            n, s = f[i]
            string += '{}<sub>{}</sub>'.format(s, str(n))

        label = QtWidgets.QLabel(string)
        label.setContentsMargins(4,4,4,4)
        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(label.sizeHint())
        self.listFormula.addItem(item)
        self.listFormula.setItemWidget(item, label)


    def tableWidgetFormula_show(self):
        self.textBrowserFormula.setVisible(False)
        self.listFormula.setVisible(False)
        self.tableWidgetFormula.setVisible(True)

        if not self.tableWidgetFormula.isEnabled():
            self.tableWidgetFormula.setEnabled(True)
            self.tableWidgetFormula_initialize()

    def tableWidgetFormula_initialize(self):
        if isinstance(self.formula, bool):
            self.tableWidgetFormula.horizontalHeader().setVisible(False)
            self.tableWidgetFormula.setRowCount(1)
            self.tableWidgetFormula.setColumnCount(1)
            self.tableWidgetFormula_addCell(0, 0, str(self.formula))

            self.tableWidgetFormula_resizeToContent()
            return
        
        table = self.tableWidgetFormula

        table.setColumnCount(1)

        for _ in self.formula:
            self.tableWidgetFormula_addRow()
            if self.tableWidgetFormula.verticalScrollBar().maximum() != 0:
                break

        for _ in range(1, self.steps):
            self.tableWidgetFormula_addColumn()
            if self.tableWidgetFormula.horizontalScrollBar().maximum() != 0:
                break
        
    def tableWidgetFormula_verticalScrollBar_valueChanged(self, value=None):
        if (not self.tableWidgetFormula.isEnabled()) or isinstance(self.formula, bool):
            return

        if value == None:
            value = self.tableWidgetFormula.verticalScrollBar().value()

        for _ in range(self.tableWidgetFormula.rowCount(), len(self.formula)):
            if value == self.tableWidgetFormula.verticalScrollBar().maximum():
                self.tableWidgetFormula_addRow()
            else: break

    def tableWidgetFormula_horizontalScrollBar_valueChanged(self, value=None):
        if (not self.tableWidgetFormula.isEnabled()) or isinstance(self.formula, bool):
            return

        if value == None:
            value = self.tableWidgetFormula.horizontalScrollBar().value()


        for _ in range(self.tableWidgetFormula.columnCount(), self.steps):
            if value == self.tableWidgetFormula.horizontalScrollBar().maximum():
                self.tableWidgetFormula_addColumn()
            else: break

    def tableWidgetFormula_addRow(self):
        column = self.tableWidgetFormula.columnCount()
        row = self.tableWidgetFormula.rowCount()
        self.tableWidgetFormula.setRowCount(row+1)
        
        f = self.formula_table[row]
        for i in range(0, column):
            if not i in f: continue
            s = f[i]
            self.tableWidgetFormula_addCell(row, i, s)

        self.tableWidgetFormula_resizeToContent()
    
    def tableWidgetFormula_addColumn(self):
        column = self.tableWidgetFormula.columnCount()
        row = self.tableWidgetFormula.rowCount()
        self.tableWidgetFormula.setColumnCount(column+1)

        self.tableWidgetFormula.setHorizontalHeaderItem(column, QtWidgets.QTableWidgetItem(str(column+1)))

        for i in range(0, row):
            f = self.formula_table[i]
            if not column in f: continue
            s = f[column]
            self.tableWidgetFormula_addCell(i, column, s)

        self.tableWidgetFormula_resizeToContent()

    def tableWidgetFormula_addCell(self, row, column, text):
        cellWidget = self.tableWidgetFormula.cellWidget(row, column)
        if cellWidget == None:
            label = QtWidgets.QLabel(text)
            label.setContentsMargins(8,2,8,2)
            label.setAlignment(QtCore.Qt.AlignCenter)
            self.tableWidgetFormula.setCellWidget(row, column, label)
        else:
            raise Exception('Add a cell more than one time')

    def tableWidgetFormula_resizeToContent(self):
        self.tableWidgetFormula.horizontalHeader().setResizeContentsPrecision(self.tableWidgetFormula.rowCount())
        self.tableWidgetFormula.resizeColumnsToContents()
        self.tableWidgetFormula.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)


class QThreadCalculateFBP(QtCore.QThread):
    stopped = False

    def __init__(self, parent):
        self.parent = parent
        super(QThreadCalculateFBP, self).__init__()

    def run(self):
        self._thread = ThreadCalculateFBP(self.parent)
        self._thread.setDaemon(True)
        self._thread.start()
        self._thread.join()

    def stop(self):
        self.stopped = True
        try:
            self._thread.terminate()
        except threading.ThreadError as e:
            if str(e) != 'the thread is not active': raise e


class ThreadCalculateFBP(thread_with_exc.Thread):
    def __init__(self, parent):
        self.parent = parent
        super(ThreadCalculateFBP, self).__init__()

    @staticmethod
    def case_literal(formula):
        if isinstance(formula, Complement):
            formula = Not(formula)
            return [formula.indices[0]+1, '¬'+formula.name]
        else:
            return [formula.indices[0]+1, formula.name]

    @staticmethod
    def case_andOp(formula):
        formula_list_and = []
        for formula_x in formula.xs:
            formula_list_and.append(ThreadCalculateFBP.case_literal(formula_x))
        return formula_list_and

    @staticmethod
    def case_orOp(formula):
        formula_list_or = []
        for formula_and in formula.xs:
            if isinstance(formula_and, Literal):
                formula_list_or.append([ThreadCalculateFBP.case_literal(formula_and)])
            elif isinstance(formula_and, AndOp):
                formula_list_or.append(ThreadCalculateFBP.case_andOp(formula_and))
        return formula_list_or
          

    def run(self):
        parent = self.parent

        formula = parent.rs.fbp(parent.symbols, parent.steps-1)

        if isinstance(formula, Constant):
            parent.formula = formula.VALUE
            return

        if isinstance(formula, Literal):
            formula_list_or = [[ThreadCalculateFBP.case_literal(formula)]]

        elif isinstance(formula, AndOp):
            formula_list_or = [ThreadCalculateFBP.case_andOp(formula)]

        elif isinstance(formula, OrOp):
            formula_list_or = ThreadCalculateFBP.case_orOp(formula)
        
        formula_list_or.sort()
        
        formula_table_or = []
        for formula_list_and in formula_list_or:
            formula_dict_and = {}
            for formula in formula_list_and:
                n, s = formula
                n -= 1
                if n in formula_dict_and:
                    formula_dict_and[n] += s
                else:
                   formula_dict_and[n] = s
            formula_table_or.append(formula_dict_and)

        parent.formula = formula_list_or
        parent.formula_table = formula_table_or


def increase_recursion_limit():
    resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
    sys.setrecursionlimit(2**31-1)
    

if __name__ == '__main__':
    increase_recursion_limit()
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow(app)
    mainWindow.show()
    sys.exit(app.exec_())