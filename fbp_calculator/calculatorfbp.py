# -*- coding: utf-8 -*-

import multiprocessing
from PyQt5 import QtCore
from fbp_calculator.reactionsystem.boolean_wrap import (
    Not,
    Constant,
    Literal,
    Complement,
    NotOp,
    AndOp,
    OrOp)

from fbp_calculator.reactionsystem import ReactionSystem, ReactionSet, Reaction

from fbp_calculator.reaction_adapter import reaction_invadapter

class QThreadCalculatorFBP(QtCore.QThread):
    stopped = False

    def __init__(self, dialog):
        self.result = multiprocessing.Manager().dict()
        self.result['completed'] = False
        self.result['formula'] = None
        self.result['formula_table'] = None

        self._process = ProcessCalculateFBP(
            dialog.steps,
            dialog.symbols,
            dialog.reaction_set,
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
    def __init__(self, steps, symbols, reaction_set, context_given_set, context_not_given_set, result):
        self.steps = steps
        self.symbols = symbols
        self.reaction_set = reaction_set
        self.context_given_set = context_given_set
        self.context_not_given_set = context_not_given_set
        self.result = result
        
        super(ProcessCalculateFBP, self).__init__()

    def run(self):
        self.rs = ReactionSystem(self.reaction_set)

        formula = self.rs.fbp(
            self.symbols, self.steps-1,
            self.context_given_set, self.context_not_given_set)

        if isinstance(formula, Constant):
            self.result['completed'] = True
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


        self.result['completed'] = True
        self.result['formula'] = formula_list_or
        self.result['formula_table'] = formula_table_or


    @staticmethod
    def case_literal(formula):
        if isinstance(formula, Complement):
            formula = Not(formula)
            negative = '¬'
        else:
            negative = ''

        name, index = reaction_invadapter(str(formula)).split('_')
        name = negative + name
        index = int(index) + 1
        return [index, name]

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
