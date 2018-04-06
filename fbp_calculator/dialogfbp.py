# -*- coding: utf-8 -*-

import re
import xlsxwriter
from PyQt5 import QtCore, QtGui, QtWidgets
from fbp_calculator.ui_dialogfbp import Ui_DialogFBP
from fbp_calculator.calculatorfbp import QThreadCalculatorFBP
from fbp_calculator.reaction_adapter import reaction_invadapter

class DialogFBP(QtWidgets.QDialog, Ui_DialogFBP):
    def __init__(self, parent,
            symbols, steps, reaction_set, context_given_set, context_not_given_set):
        super(DialogFBP, self).__init__(parent)
        self.setupUi(self)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.formulaType_defaultIndex = 1
        self.comboBoxFormulaType.setCurrentIndex(self.formulaType_defaultIndex)
        self.textBrowserFormula.setVisible(self.formulaType_defaultIndex == 0)
        self.listFormula.setVisible(self.formulaType_defaultIndex == 1)
        self.tableWidgetFormula.setVisible(self.formulaType_defaultIndex == 2)

        self.symbols = symbols
        self.steps = steps
        self.reaction_set = reaction_set
        self.context_given_set = context_given_set
        self.context_not_given_set = context_not_given_set

        self.lineEditSymbols.setText(reaction_invadapter(self.symbols))
        self.lineEditSteps.setText(str(self.steps))
        
        self.labelLoadingImage.setMovie(QtGui.QMovie(":/loader.gif"))
        self.labelLoadingImage.movie().start()

        self.toolButtonSave.setVisible(False)
        self.toolButtonSave.clicked.connect(self.toolButtonSave_clicked)

        self.comboBoxFormulaType.currentIndexChanged.connect(self.comboBoxFormulaType_currentIndexChanged)

        self.listFormula.verticalScrollBar().valueChanged.connect(self.listFormula_scrollBar_valueChanged)
        self.tableWidgetFormula.horizontalScrollBar().valueChanged.connect(self.tableWidgetFormula_horizontalScrollBar_valueChanged)
        self.tableWidgetFormula.verticalScrollBar().valueChanged.connect(self.tableWidgetFormula_verticalScrollBar_valueChanged)


        self.QThreadCalculatorFBP = QThreadCalculatorFBP(self)
        self.QThreadCalculatorFBP.finished.connect(self.QThread_finishedCalculatorFBP)
        self.QThreadCalculatorFBP.start()

    def toolButtonSave_clicked(self):
        formulaType_index = self.comboBoxFormulaType.currentIndex()
        if formulaType_index == 0:
            file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, 
                'Save result as', 
                'untitled.txt',
                'TXT files (*.txt)')

            if not file_name:
                return
            try:
                with open(file_name, 'w') as file:
                    file.write(self.save_text)
            except Exception as e:
                error_message = str(e)
                if 'Errno' in error_message:
                    error_message = error_message.split('] ')[1]
                QtWidgets.QMessageBox.critical(self,
                    'Error when saving the file',
                    '{}'.format(error_message),
                    QtWidgets.QMessageBox.Close,
                    QtWidgets.QMessageBox.Close)

        elif formulaType_index == 1:
            file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, 
                'Save result as', 
                'untitled.txt',
                'TXT files (*.txt)')
            
            if not file_name:
                return
            try:
                with open(file_name, 'w') as file:
                    file.write(self.save_list)
            except Exception as e:
                error_message = str(e)
                if 'Errno' in error_message:
                    error_message = error_message.split('] ')[1]
                QtWidgets.QMessageBox.critical(self,
                    'Error when saving the file',
                    '{}'.format(error_message),
                    QtWidgets.QMessageBox.Close,
                    QtWidgets.QMessageBox.Close)

        elif formulaType_index == 2:
            file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, 
                'Save result as', 
                'untitled.xlsx',
                'XLSX files (*.xlsx)')
            
            if not file_name:
                return
            workbook = xlsxwriter.Workbook(file_name)
            worksheet = workbook.add_worksheet()

            if isinstance(self.formula, bool):
                worksheet.write(0, 0, str(self.formula))

            else:
                for i in range(0, self.steps):
                    worksheet.write(0, i, str(i+1))

                for i in range(0, len(self.formula_table)):
                    row = self.formula_table[i]
                    for column in row:
                        text = row[column]
                        worksheet.write(i+1, column, text)

            try:
                workbook.close()
            except Exception as e:
                error_message = str(e)
                if 'Errno' in error_message:
                    error_message = error_message.split('] ')[1]
                QtWidgets.QMessageBox.critical(self,
                    'Error when saving the file',
                    '{}'.format(error_message),
                    QtWidgets.QMessageBox.Close,
                    QtWidgets.QMessageBox.Close)
            



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
        self.labelComputing.setVisible(False)

        if not self.QThreadCalculatorFBP.result['completed']:
            self.labelComputing.setStyleSheet("QLabel { color : red; font-weight:600; }")
            self.labelComputing.setText('Error during the fbp calculation')
            self.labelComputing.setVisible(True)
            return
        
        self.formula = self.QThreadCalculatorFBP.result['formula']
        self.formula_table = self.QThreadCalculatorFBP.result['formula_table']

        self.toolButtonSave.setVisible(True)

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
            text = str(self.formula)
            self.textBrowserFormula.setText(text)
            self.save_text = text
            return

        text_subbed = ''
        prebrackets = len(self.formula) > 1
        for i in range(0, len(self.formula)):
            if i > 0: text_subbed += ' ∨ '
            backets = prebrackets and len(self.formula[i]) > 1
            if backets: text_subbed += '('
            for j in range(0, len(self.formula[i])):
                if j > 0: text_subbed += ' ∧ '
                n, s = self.formula[i][j]
                text_subbed += '{}<sub>{}</sub>'.format(s, str(n))
            if backets: text_subbed += ')'
        self.textBrowserFormula.setText(text_subbed)
        save_text = text_subbed
        save_text = re.sub('<sub>', '_', save_text)
        save_text = re.sub('</sub>', '', save_text)
        self.save_text = save_text


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
            text = str(self.formula)
            self.listFormula.addItem(QtWidgets.QListWidgetItem(text))
            self.save_list = text
            return
        
        text = ''
        for f in self.formula:
            for i in range(0, len(f)):
                n, s = f[i]
                text += '{}_{} '.format(s, str(n))
            text = text[:-1]
            text += '\r\n'
        self.save_list = text

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
        text = ''
        for i in range(0, len(f)):
            n, s = f[i]
            text += '{}<sub>{}</sub> '.format(s, str(n))
        text = text[:-1]

        label = QtWidgets.QLabel(text)
        label.setContentsMargins(4,4,4,4)
        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(QtCore.QSize(0, label.sizeHint().height()+4))
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
            label.setAlignment(QtCore.Qt.AlignLeft)
            self.tableWidgetFormula.setCellWidget(row, column, label)
        else:
            raise Exception('Add a cell more than one time')

    def tableWidgetFormula_resizeToContent(self):
        self.tableWidgetFormula.horizontalHeader().setResizeContentsPrecision(self.tableWidgetFormula.rowCount())
        self.tableWidgetFormula.resizeColumnsToContents()
        self.tableWidgetFormula.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
