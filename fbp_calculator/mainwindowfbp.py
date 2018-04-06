# -*- coding: utf-8 -*-

import re
from copy import deepcopy
from PyQt5 import QtCore, QtGui, QtWidgets
from fbp_calculator.reactionsystem import (
    Reaction,
    ReactionSet,
    ExceptionReactionSystem)
from fbp_calculator.ui_mainwindowfbp import Ui_MainWindowFBP
from fbp_calculator.dialogfbp import DialogFBP
from fbp_calculator.reaction_adapter import reaction_adapter, reaction_invadapter
from fbp_calculator import __version__


class MainWindowFBP(QtWidgets.QMainWindow, Ui_MainWindowFBP):
    def __init__(self, app, parent=None):
        super(MainWindowFBP, self).__init__(parent)

        self.setupUi(self)

        self._translate = QtCore.QCoreApplication.translate
 
        self.statusbarStyle = self.statusbar.styleSheet()

        self.reaction_list = []
        
        self.temp_file_name = ''
        self.current_file_name = ''

        self.validatorLineEditSymbols_regex = '^([a-zA-Z]|\d|\s|,)+$' # pylint: disable=W1401
        self.validatorLineEditSymbols = QtGui.QRegExpValidator(QtCore.QRegExp(self.validatorLineEditSymbols_regex))
        self.validatorLineEditSymbols_empty_regex = '^([a-zA-Z]|\d|\s|,)*$' # pylint: disable=W1401
        self.validatorLineEditSymbols_empty = QtGui.QRegExpValidator(QtCore.QRegExp(self.validatorLineEditSymbols_empty_regex))
        self.validatorContextProperties_regex = '^([a-zA-Z]|\d|\s|,|%)+$' # pylint: disable=W1401
        self.validatorContextProperties = QtGui.QRegExpValidator(QtCore.QRegExp(self.validatorContextProperties_regex))


        self.lineEditReactants.setValidator(self.validatorLineEditSymbols)
        self.lineEditProducts.setValidator(self.validatorLineEditSymbols)
        self.lineEditInhibitors.setValidator(self.validatorLineEditSymbols_empty)
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

        height = self.tableWidgetProperties.horizontalHeader().size().height()
        height += self.tableWidgetProperties.rowHeight(0)
        height += self.tableWidgetProperties.rowHeight(1)
        height += self.tableWidgetProperties.horizontalScrollBar().size().height()
        self.tableWidgetProperties.setFixedHeight(height+4)

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
                'TXT files (*.txt);;All files (*)')
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
        except Exception as e:
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
            self._translate('MainWindowFBP', 'FBP Calculator'),
            'version {}\n'.format(__version__) +
            'Written by William Guglielmo.\n' + \
            'Based on the work of:\n' + \
            'Roberto Barbuti\n' + \
            'Roberta Gori\n' + \
            'Paolo Milazzo\n' + \
            'Francesca Levi\n')

    @staticmethod 
    def text2reaction_list(text):
        reaction_list = []
        text.replace('\r', ' ')
        reactions = text.split('\n')
        for reaction in reactions:
            if (re.match('^\s*#', reaction) or re.match('^\s*$', reaction)): # pylint: disable=W1401
                continue
            reaction_list.append(Reaction(reaction_adapter(reaction)))
        return reaction_list

    @staticmethod
    def reaction_list2text(reaction_list):
        text = ''
        for reaction in reaction_list:
            text += reaction_invadapter(str(reaction)) + '\r\n'
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
            reaction = Reaction(
                R=reaction_adapter(reactants),
                P=reaction_adapter(products),
                I=reaction_adapter(inhibitors))
        except Exception as e:
            self._manageExceptionReactionSystem(e)
            return

        if reaction in self.reaction_list:
            self.notify('Error: this reaction is already present')
            return
        
        self.reaction_list.append(reaction)

        self.listWidgetReactions_addReaction(reaction)
        self.notify('Added ' + str(reaction).replace('->', '⟶'))

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
                self.reaction_list.remove(Reaction(reaction_adapter(item.text()).replace('⟶', '->')))
                self.listWidgetReactions._checked_item_number -= 1
            else: i += 1
        self.pushButtonDelete.setEnabled(False)

        self.pushButtonCalculate_enable()
        self.actionSave.setEnabled(True)


    def pushButtonCalculate_clicked(self):
        if not self.pushButtonCalculate_generateContextPropertieSet():
            return

        DialogFBP(self,
            deepcopy(reaction_adapter(self.lineEditCalculatorSymbols.text())),
            deepcopy(self.spinBoxCalculatorSteps.value()),
            ReactionSet(deepcopy(self.reaction_list)),
            deepcopy(self.context_given_set[0]),
            deepcopy(self.context_given_set[1])
        ).show()

    def pushButtonCalculate_generateContextPropertieSet(self):
        self.context_given_set = [set(), set()]
        steps = self.spinBoxCalculatorSteps.value()

        for j in range(0, self.tableWidgetProperties.columnCount()):
            for i in range(0, len(self.context_given_set)):
                cellContent = reaction_adapter(
                    self.tableWidgetProperties.cellWidget(i, j).text())
                symbol_regex = Reaction._get_symbol_regex()

                symbol_list_regex = '^\s*(%?{}\s+)*%?{}\s*$'.format(symbol_regex, symbol_regex) # pylint: disable=W1401
                
                if (len(cellContent) and not cellContent.isspace() and
                        not re.match(symbol_list_regex, cellContent)):
                    self.notify('Error: invalid syntax in step {}'.format(str(j+1)))
                    return False
                
                pattern = '%{}'.format(symbol_regex)
                context_given_from = re.findall(pattern, cellContent)
                context_given = re.sub(pattern, '', cellContent)
                context_given = re.findall(symbol_regex, context_given)
                
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
        item = QtWidgets.QListWidgetItem(reaction_invadapter(str(reaction)).replace('->', '⟶'))
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
        
        self.tableWidgetProperties.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)

    def tableWidgetProperties_fillSpace(self):
        if not self.tableWidgetProperties.isEnabled():
            return

        for _ in range(self.tableWidgetProperties.columnCount(), self.spinBoxCalculatorSteps.value()):
            scrollbar = self.tableWidgetProperties.horizontalScrollBar()
            if scrollbar.maximum() != 0 and scrollbar.maximum() != scrollbar.value() :
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
                lineEdit.setValidator(self.validatorContextProperties)
                lineEdit.returnPressed.connect(self.pushButtonCalculate.click)
                lineEdit.setStatusTip("Example: A B %C D (%C means C from this step)")
                self.tableWidgetProperties.setCellWidget(i, column, lineEdit)
        # self.tableWidgetProperties.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)


    def statusbarChanged(self, string):
        if string and string[0:5] == 'Error':
            self.statusbar.setStyleSheet("QStatusBar{background:rgba(255,0,0,255);color:black;font-weight:bold;}")
        else:
            self.statusbar.setStyleSheet(self.statusbarStyle)


    def notify(self, message):
        self.statusbar.showMessage(message, msecs=4000)

        
    def _manageExceptionReactionSystem(self, e):
        if isinstance(e, ExceptionReactionSystem.InvalidSyntax):
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
