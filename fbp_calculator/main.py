#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import resource
import re
import math
from copy import deepcopy

import multiprocessing  

from reactionsystem import \
    Reaction, \
    ReactionSet, \
    ReactionSystem, \
    ExceptionReactionSystem

from main_ui import Ui_MainWindowFBP
from formula_ui import Ui_DialogFBP


from PyQt5 import QtCore, QtGui, QtWidgets

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
        
        self.temp_file_name = ''
        self.current_file_name = ''

        self.validatorLineEditSymbols = QtGui.QRegExpValidator(QtCore.QRegExp('^[a-zA-Z ]+$')) # pylint: disable=W1401

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

        self.setGeometry(
            QtWidgets.QStyle.alignedRect(
                QtCore.Qt.LeftToRight,
                QtCore.Qt.AlignCenter,
                self.size(),
                app.desktop().availableGeometry()))


    def resizeEvent(self, event):
        self.tableWidgetProperties_fillSpace()

    def closeEvent(self, event):
        event.ignore()
        self.actionQuit_triggered()


    def actionNew_triggered(self, value=None):
        if not self.check_save():
            return
            
        self.spinBoxCalculatorSteps.setValue(1)
        self.tableWidgetProperties.cellWidget(0,0).setText('')
        self.tableWidgetProperties.cellWidget(1,0).setText('')
        self.lineEditCalculatorSymbols.setText('')
        self.lineEditReactants.setText('')
        self.lineEditProducts.setText('')
        self.lineEditInhibitors.setText('')
        self.lineEditReactants.setFocus(True)

        self.current_file_name = ''
        self.reaction_list.clear()
        self.listWidgetReactions_clear()

    def actionOpen_triggered(self, value=None):
        if not self.check_save():
            return
        self.temp_file_name, _ = \
            QtWidgets.QFileDialog.getOpenFileName(self, 
                'Open a Reaction System file', 
                '',
                'TXT files (*.txt)')
        if not self.temp_file_name:
            return

        try:
            with open(self.temp_file_name, 'r') as file:
                file_content = file.read()
        except Exception as e:
            error_message = str(e)
            if 'Errno' in error_message:
                error_message = error_message.split('] ')[1]
            QtWidgets.QMessageBox.critical(self,
                'Error when opening the file',
                '{}'.format(error_message),
                QtWidgets.QMessageBox.Close,
                QtWidgets.QMessageBox.Close)
            return

        try:
            self.reaction_list = self.text2reaction_list(file_content)
        except ValueError as e:
            QtWidgets.QMessageBox.critical(self,
                'Error when opening the file',
                'Invalid syntax: \'{}\''.format(self.temp_file_name),
                QtWidgets.QMessageBox.Close,
                QtWidgets.QMessageBox.Close)
            return

        self.listWidgetReactions_clear()

        for reaction in self.reaction_list:
            self.listWidgetReactions_addReaction(reaction)

        self.current_file_name = self.temp_file_name

        self.notify('File ' + self.current_file_name + ' opened')

    def actionSave_triggered(self, value=None):
        if not self.current_file_name:
            self.actionSave_as_triggered()
            return
        self.save_file(self.current_file_name)
    
    def actionSave_as_triggered(self, value=None):
        file_name, _ = \
            QtWidgets.QFileDialog.getSaveFileName(self, 
                'Save Reaction System As', 
                'untitled.txt',
                'TXT files (*.txt)')
        self.save_file(file_name)

    def actionQuit_triggered(self, value=None):
        if not self.check_save():
            return
        QtCore.QCoreApplication.quit()

    def actionAbout_triggered(self):
        QtWidgets.QMessageBox.about(self,
            self._translate('MainWindow', 'FBP Calculator'),
            'version 1.0.0\n' +
            'Writtern by William Guglielmo')


    @staticmethod 
    def text2reaction_list(text):
        reaction_list = []
        text.replace('\r', ' ')
        text.replace('\t', ' ')
        reactions = text.split('\n')
        reactions_len = len(reactions)
        for i in range(0, reactions_len):
            reaction = reactions[i]
            if reaction == '' or reaction.isspace():
                for j in range(i, reactions_len):
                    if not(reactions[j] == '' or reactions[j].isspace):
                        raise ValueError()
                break
            split_r = reaction.split('->')
            if len(split_r) != 2: raise ValueError()
            r = split_r[0]
            split_p = split_r[1].split('|')
            split_p_len = len(split_p)
            if split_p_len > 2: raise ValueError()
            p = split_p[0]
            i = split_p[1] if split_p_len == 2 else ''
            try:
                reaction_list.append(Reaction(r, p, i))
            except Exception: raise ValueError()

        return reaction_list

    @staticmethod
    def reaction_list2text(reaction_list):
        text = ''
        for reaction in reaction_list:
            text += ' '.join(reaction.R)
            text += ' -> '
            text += ' '.join(reaction.P)
            if len(reaction.I):
                text += ' | '
                text += ' '.join(reaction.I)
            text += '\r\n'
        
        return text


    def save_file(self, file_name):
        if not file_name:
            return
        try:
            with open(file_name, 'w') as file:
                file.write(self.reaction_list2text(self.reaction_list))
        except Exception as e:
            error_message = str(e)
            if 'Errno' in error_message:
                error_message = error_message.split('] ')[1]
            QtWidgets.QMessageBox.critical(self,
                'Error when saving the file',
                '{}'.format(error_message),
                QtWidgets.QMessageBox.Close,
                QtWidgets.QMessageBox.Close)
            return
        self.actionSave.setEnabled(False)
        self.current_file_name = file_name
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
        if not self.pushButtonCalculate_generateContextPropertieSet():
            return

        FormulaWindow(self,
            deepcopy(self.lineEditCalculatorSymbols.text()),
            deepcopy(self.spinBoxCalculatorSteps.value()),
            ReactionSystem(ReactionSet(deepcopy(self.reaction_list))),
            deepcopy(self.context_given_set[0]),
            deepcopy(self.context_given_set[1])
        ).show()

    def pushButtonCalculate_generateContextPropertieSet(self):
        self.context_given_set = [set(), set()]
        steps = self.spinBoxCalculatorSteps.value()

        for j in range(0, self.tableWidgetProperties.columnCount()):
            for i in range(0, len(self.context_given_set)):
                cellContent = self.tableWidgetProperties.cellWidget(i, j).text()

                pattern = '%[a-zA-Z]+'
                context_given_from = re.findall(pattern, cellContent)
                context_given = re.sub(pattern, '', cellContent)

                if '%' in context_given:
                    self.notify('Error in context properties step {}: %'.format(str(j+1)))
                    return False
                
                context_given = re.sub(' +', ' ', context_given)
                context_given = context_given.split(' ')
                context_given = list(filter(lambda s: s != '', context_given))
                context_given = set(map(lambda s: (j, s), context_given))
                context_given_from = set(map(lambda s: s[1:], context_given_from))
                
                self.context_given_set[i] = self.context_given_set[i].union(context_given)

                for z in range(j, steps):
                    for symbol in context_given_from:
                        self.context_given_set[i].add((z, symbol))

            intersectionSet = self.context_given_set[0].intersection(self.context_given_set[1])
            if len(intersectionSet):
                symbols_set = sorted(list(set(map(lambda t: t[1], intersectionSet))))
                self.notify('Error in context properties step {}: {}'.format(str(j+1), ' '.join(symbols_set)))
                return False
        
        return True

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

        self.tableWidgetProperties_fillSpace()
        
        self.tableWidgetProperties.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    def tableWidgetProperties_fillSpace(self):
        if not self.tableWidgetProperties.isEnabled():
            return

        for _ in range(self.tableWidgetProperties.columnCount(), self.spinBoxCalculatorSteps.value()):
            if self.tableWidgetProperties.horizontalScrollBar().maximum() != 0:
                break
            self.tableWidgetProperties_addColumn()
    
    def tableWidgetProperties_scrollBar_valueChanged(self, value):
        if not self.tableWidgetProperties.isEnabled():
            return

        if (self.tableWidgetProperties.columnCount() < self.spinBoxCalculatorSteps.value() and 
                value == self.tableWidgetProperties.horizontalScrollBar().maximum()):
            self.tableWidgetProperties_addColumn()


    def tableWidgetProperties_addColumn(self):
        column = self.tableWidgetProperties.columnCount()
        self.tableWidgetProperties.setColumnCount(column+1)

        self.tableWidgetProperties.setHorizontalHeaderItem(column, QtWidgets.QTableWidgetItem(str(column+1)))
        for i in range(0, self.tableWidgetProperties.rowCount()):
            cellWidget = self.tableWidgetProperties.cellWidget(i, column)
            if cellWidget == None:
                lineEdit = QtWidgets.QLineEdit()
                lineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("^[a-zA-Z %]+$")))
                lineEdit.returnPressed.connect(self.pushButtonCalculate.click)
                lineEdit.setStatusTip("Example: A B %C D (%C means C from this step)")
                self.tableWidgetProperties.setCellWidget(i, column, lineEdit)
        self.tableWidgetProperties.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)


    def statusbarChanged(self, string):
        if string and string[0:5] == 'Error':
            self.statusbar.setStyleSheet("QStatusBar{background:rgba(255,0,0,255);color:black;font-weight:bold;}")
        else:
            self.statusbar.setStyleSheet(self.statusbarStyle)


    def notify(self, message):
        self.statusbar.showMessage(message, msecs=4000)

        
    def _manageExceptionReactionSystem(self, e):
        if isinstance(e, ExceptionReactionSystem.SymbolsMustBeLetters):
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
    def __init__(self, parent,
            symbols, steps, rs, context_given_set, context_not_given_set):
        super(FormulaWindow, self).__init__(parent)
        self.setupUi(self)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.formulaType_defaultIndex = 2
        self.comboBoxFormulaType.setCurrentIndex(self.formulaType_defaultIndex)
        self.textBrowserFormula.setVisible(self.formulaType_defaultIndex == 0)
        self.listFormula.setVisible(self.formulaType_defaultIndex == 1)
        self.tableWidgetFormula.setVisible(self.formulaType_defaultIndex == 2)

        self.symbols = symbols
        self.steps = steps
        self.rs = rs
        self.context_given_set = context_given_set
        self.context_not_given_set = context_not_given_set

        self.lineEditSymbols.setText(self.symbols)
        self.lineEditSteps.setText(str(self.steps))
        
        self.labelLoadingImage.setMovie(QtGui.QMovie(":/loader.gif"))
        self.labelLoadingImage.movie().start()

        self.comboBoxFormulaType.currentIndexChanged.connect(self.comboBoxFormulaType_currentIndexChanged)


        self.listFormula.verticalScrollBar().valueChanged.connect(self.listFormula_scrollBar_valueChanged)
        self.tableWidgetFormula.horizontalScrollBar().valueChanged.connect(self.tableWidgetFormula_horizontalScrollBar_valueChanged)
        self.tableWidgetFormula.verticalScrollBar().valueChanged.connect(self.tableWidgetFormula_verticalScrollBar_valueChanged)


        self.QThreadCalculatorFBP = QThreadCalculatorFBP(self)
        self.QThreadCalculatorFBP.finished.connect(self.QThread_finishedCalculatorFBP)
        self.QThreadCalculatorFBP.start()


    def resizeEvent(self, event):
        self.listFormula_fillSpace()
        self.tableWidgetFormula_fillVerticalSpace()
        self.tableWidgetFormula_fillHorizontalSpace()

    def closeEvent(self, event):
        self.QThreadCalculatorFBP.stop()
        self.QThreadCalculatorFBP.wait()
        event.accept()
    
    def QThread_finishedCalculatorFBP(self):
        if self.QThreadCalculatorFBP.stopped:
            return

        self.labelLoadingImage.setVisible(False)
        self.labelLoadingImage.movie().stop()

        try:
            self.formula = self.QThreadCalculatorFBP.result['formula']
            self.formula_table = self.QThreadCalculatorFBP.result['formula_table']
        except Exception:
            self.labelComputing.setStyleSheet("QLabel { color : red; font-weight:600; }")
            self.labelComputing.setText('Error in fbp calculation')
            return

        self.labelComputing.setVisible(False)

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
            self.listFormula_fillSpace()
            
    def listFormula_initialize(self):
        if isinstance(self.formula, bool):
            self.listFormula.addItem(QtWidgets.QListWidgetItem(str(self.formula)))
            return

        self.listFormula_fillSpace()

    def listFormula_fillSpace(self):
        if (not self.listFormula.isEnabled() or not self.listFormula.isVisible()
                or isinstance(self.formula, bool)):
            return

        for _ in range(self.listFormula.count(), len(self.formula)):
            if self.listFormula.verticalScrollBar().maximum() != 0:
                break
            self.listFormula_addRow()
    
    def listFormula_scrollBar_valueChanged(self, value):
        if (not self.listFormula.isEnabled() or not self.listFormula.isVisible()
                or isinstance(self.formula, bool)):
            return

        listFormula_len = self.listFormula.count()

        if (listFormula_len < len(self.formula) and
                value == self.listFormula.verticalScrollBar().maximum()):
            self.listFormula_addRow()

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
        else:
            self.tableWidgetFormula_fillVerticalSpace()
            self.tableWidgetFormula_fillHorizontalSpace()

    def tableWidgetFormula_initialize(self):
        if isinstance(self.formula, bool):
            self.tableWidgetFormula.horizontalHeader().setVisible(False)
            self.tableWidgetFormula.setRowCount(1)
            self.tableWidgetFormula.setColumnCount(1)
            self.tableWidgetFormula_addCell(0, 0, str(self.formula))

            self.tableWidgetFormula_resizeToContent()
            return

        self.tableWidgetFormula_fillHorizontalSpace()
        self.tableWidgetFormula_fillVerticalSpace()
        
    def tableWidgetFormula_fillVerticalSpace(self):
        if (not self.tableWidgetFormula.isEnabled() or not self.tableWidgetFormula.isVisible()
                or isinstance(self.formula, bool)):
            return
        
        for _ in range(self.tableWidgetFormula.rowCount(), len(self.formula_table)):
            if self.tableWidgetFormula.verticalScrollBar().maximum() != 0:
                break
            self.tableWidgetFormula_addRow()

    def tableWidgetFormula_fillHorizontalSpace(self):
        if (not self.tableWidgetFormula.isEnabled() or not self.tableWidgetFormula.isVisible()
                or isinstance(self.formula, bool)):
            return
        
        for _ in range(self.tableWidgetFormula.columnCount(), self.steps):
            if self.tableWidgetFormula.horizontalScrollBar().maximum() != 0:
                break
            self.tableWidgetFormula_addColumn()

    def tableWidgetFormula_verticalScrollBar_valueChanged(self, value):
        if (not self.tableWidgetFormula.isEnabled() or not self.tableWidgetFormula.isVisible()
                or isinstance(self.formula, bool)):
            return

        if (self.tableWidgetFormula.rowCount() < len(self.formula_table) and
                value == self.tableWidgetFormula.verticalScrollBar().maximum()):
            self.tableWidgetFormula_addRow()

    def tableWidgetFormula_horizontalScrollBar_valueChanged(self, value):
        if (not self.tableWidgetFormula.isEnabled()) or isinstance(self.formula, bool):
            return

        if (self.tableWidgetFormula.columnCount() < self.steps and
                value == self.tableWidgetFormula.horizontalScrollBar().maximum()):
            self.tableWidgetFormula_addColumn()

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


class QThreadCalculatorFBP(QtCore.QThread):
    stopped = False

    def __init__(self, dialog):
        self.result = multiprocessing.Manager().dict()
        self._process = ProcessCalculateFBP(
            dialog.steps,
            dialog.symbols,
            dialog.rs,
            dialog.context_given_set,
            dialog.context_not_given_set,
            self.result)
        self._process.daemon = True

        super(QThreadCalculatorFBP, self).__init__()

    def run(self):
        self._process.start()
        self._process.join()

    def stop(self):
        self.stopped = True
        try:
            self._process.terminate()
        except Exception: pass


class ProcessCalculateFBP(multiprocessing.Process):
    def __init__(self, steps, symbols, rs, context_given_set, context_not_given_set, result):
        self.steps = steps
        self.symbols = symbols
        self.rs = rs
        self.context_given_set = context_given_set
        self.context_not_given_set = context_not_given_set
        self.result = result

        super(ProcessCalculateFBP, self).__init__()

    def run(self):
        formula = self.rs.fbp(
            self.symbols, self.steps-1,
            self.context_given_set, self.context_not_given_set)

        if isinstance(formula, Constant):
            self.result['formula'] = formula.VALUE
            self.result['formula_table'] = formula.VALUE
            return

        if isinstance(formula, Literal):
            formula_list_or = [[ProcessCalculateFBP.case_literal(formula)]]

        elif isinstance(formula, AndOp):
            formula_list_or = [ProcessCalculateFBP.case_andOp(formula)]

        elif isinstance(formula, OrOp):
            formula_list_or = ProcessCalculateFBP.case_orOp(formula)
        
        formula_list_or = list(map(lambda x: sorted(x), formula_list_or))
        formula_list_or.sort()
        
        formula_table_or = []
        for formula_list_and in formula_list_or:
            formula_dict_and = {}
            for formula in formula_list_and:
                n, s = formula
                n -= 1
                if n in formula_dict_and:
                    formula_dict_and[n] += ' ' + s
                else:
                   formula_dict_and[n] = s
            formula_table_or.append(formula_dict_and)

        self.result['formula'] = formula_list_or
        self.result['formula_table'] = formula_table_or


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
            formula_list_and.append(ProcessCalculateFBP.case_literal(formula_x))
        return formula_list_and

    @staticmethod
    def case_orOp(formula):
        formula_list_or = []
        for formula_and in formula.xs:
            if isinstance(formula_and, Literal):
                formula_list_or.append([ProcessCalculateFBP.case_literal(formula_and)])
            elif isinstance(formula_and, AndOp):
                formula_list_or.append(ProcessCalculateFBP.case_andOp(formula_and))
        return formula_list_or



def increase_recursion_limit():
    resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
    sys.setrecursionlimit(2**31-1)
    

if __name__ == '__main__':
    increase_recursion_limit()
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow(app)
    mainWindow.show()
    sys.exit(app.exec_())
    