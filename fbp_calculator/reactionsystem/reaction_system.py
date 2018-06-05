# -*- coding: utf-8 -*-

from pyeda.inter import expr
from pyeda.inter import espresso_exprs
from pyeda.boolalg.expr import Atom 

from fbp_calculator.reactionsystem.boolean_wrap import (
    Not,
    And,
    Or,
    Constant,
    Literal,
    Variable,
    Complement,
    AndOp,
    OrOp,
    OrAndOp,
    ZERO,
    ONE,
    var)

from fbp_calculator.reactionsystem.reaction import Reaction
from fbp_calculator.reactionsystem.reaction_set import ReactionSet
from fbp_calculator.reactionsystem.exceptions import ExceptionReactionSystem

from fbp_calculator.reactionsystem.fbs_iterate_item import FbsIterateItem
from fbp_calculator.reactionsystem.fbs_calculated_item import FbsCalculatedItem

import sys
if 'time' in sys.argv:
    import time


class ReactionSystem():
    def __init__(self, A):
        reactant_set = set()
        for reaction in A:
            reactant_set = reactant_set.union(reaction.P)
        self._causes = {}
        for reactant in reactant_set:
            self._causes[reactant] = A.cause(reactant)

    def cause(self, symbol):
        return self._causes.get(symbol, ZERO)

    def fbp(self, symbols, steps, context_given=set(), context_not_given=set()):
        symbolSet = Reaction._create_symbol_set(symbols)
        if not isinstance(steps, int) or steps < 0:
                raise ExceptionReactionSystem.InvalidNumber()
        if (not isinstance(context_given, set) or 
            not isinstance(context_not_given, set)):
                raise ExceptionReactionSystem.InvalidContextSet()
        
        self._cg = context_given
        self._cng = context_not_given

        self._calculated_items = {}

        if 'time' in sys.argv:
            start = time.time()

        formula = ONE
        for symbol in symbolSet:
            formula = And(formula, self.cause(symbol))
            formula = formula.to_dnf()
        
        formula = self._fbs_iterative(formula, steps)
        
        if not isinstance(formula, Atom) and formula.is_dnf():
            formula = espresso_exprs(formula)[0]

        if 'time' in sys.argv:
            print(time.time() - start)

        return formula

    def _fbs_iterative(self, formula, step):
        stack = [FbsIterateItem(
                formula=formula,
                parent=None,
                step=step,
                inv_nf=False)]
        
        while True:
            item = stack.pop()
            formula = item.formula

            if isinstance(formula, Constant):
                result = formula

                
            elif isinstance(formula, Variable):
                symbol = formula.name
                step = item.step
                inv_nf = item.inv_nf

                fbs_calculated_item = FbsCalculatedItem(symbol, step, inv_nf)
                if fbs_calculated_item in self._calculated_items:
                    result = self._calculated_items[fbs_calculated_item]

                else:
                    if not step or not item.remained:
                        if (step, symbol) in self._cg:
                            result = ONE
                        elif (step, symbol) in self._cng:
                            result = ZERO
                        else:
                            result = var('{}_{}'.format(symbol, step))
                        
                    elif item.remained:
                            item.remained = 1

                            stack.append(FbsIterateItem(
                                formula=self.cause(symbol),
                                parent=item,
                                step=step-1,
                                inv_nf=inv_nf))
                            continue
                        
                    if step > 0:
                        result = Or(result, item.childs[0])

                    result = result.to_cnf() if inv_nf else result.to_dnf()
                    self._calculated_items[fbs_calculated_item] = result

            elif isinstance(formula, Complement):
                if item.remained:
                    item.remained = 1
                    
                    stack.append(FbsIterateItem(
                        formula=Not(formula),
                        parent=item,
                        step=item.step,
                        inv_nf=not item.inv_nf))
                    continue
                
                else:
                    result = Not(item.childs[0])


            elif isinstance(formula, OrAndOp):
                Op = And if isinstance(formula, AndOp) else Or

                if item.remained:
                    item.remained = 2

                    stack.append(FbsIterateItem(
                        formula=formula.xs[0],
                        parent=item,
                        step=item.step,
                        inv_nf=item.inv_nf))
                    stack.append(FbsIterateItem(
                        formula=Op(*formula.xs[1:]),
                        parent=item,
                        step=item.step,
                        inv_nf=item.inv_nf))
                    continue
                
                else:
                    result = Op(item.childs[0], item.childs[1])


            result = result.to_cnf() if item.inv_nf else result.to_dnf()
            

            if item.parent == None:
                break
            else:
                item.parent.remained -= 1
                item.parent.childs.append(result)
                if not item.parent.remained:
                    stack.append(item.parent)
                continue


        return result
        
    
    def _fbs(self, formula, step, inv_nf=False):
        if isinstance(formula, Constant):
            pass

        elif isinstance(formula, Variable):
            symbol = formula.name

            fbs_calculated_item = FbsCalculatedItem(symbol, step, inv_nf)
            if fbs_calculated_item in self._calculated_items:
                formula = self._calculated_items[fbs_calculated_item]

            else:
                if (step,symbol) in self._cg:
                    self._calculated_items[fbs_calculated_item] = ONE
                    return ONE
                elif (step,symbol) in self._cng:
                    formula = ZERO
                else:
                    formula = var('{}_{}'.format(symbol, step))
                
                if step > 0:
                    formula = Or(formula, self._fbs(self.cause(symbol), step-1, inv_nf))

                formula = formula.to_cnf() if inv_nf else formula.to_dnf()
                self._calculated_items[fbs_calculated_item] = formula
        
        
        elif isinstance(formula, Complement):
            formula = Not(self._fbs(Not(formula), step, not inv_nf))

        elif isinstance(formula, OrAndOp):
            Op = And if isinstance(formula, AndOp) else Or
            formula = Op(
                self._fbs(formula.xs[0], step, inv_nf),
                self._fbs(Op(*formula.xs[1:]), step, inv_nf))

        else:
            assert()

        formula = formula.to_cnf() if inv_nf else formula.to_dnf()

        return formula


    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self._causes == other._causes

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._causes)

    def __str__(self):
        return 'ReactionSystem({})'.format(str(self._causes))

    def __repr__(self):
        return str(self)
