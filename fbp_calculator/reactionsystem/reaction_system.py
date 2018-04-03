from pyeda.inter import expr
from pyeda.inter import espresso_exprs
from pyeda.boolalg.expr import Atom 

from .boolean_wrap import (
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
    var,
    parse)

from .reaction import Reaction
from .reaction_set import ReactionSet
from .exceptions import ExceptionReactionSystem

import sys
if 'time' in sys.argv:
    import time


class ReactionSystem():
    def __init__(self, A):
        self.A = A

    @property
    def A(self): return self._A

    @A.setter
    def A(self, A):
        if not isinstance(A, ReactionSet): raise ExceptionReactionSystem.InvalidReactionSet()
        self._A = A

    def cause(self, symbol):
        return self.A.cause(symbol)

    def fbp(self, symbols, steps, context_given=set(), context_not_given=set()):
        symbolSet = Reaction._create_symbol_set(symbols)
        if not isinstance(steps, int) or steps < 0:
                raise ExceptionReactionSystem.InvalidNumber()
        if (not isinstance(context_given, set) or 
            not isinstance(context_not_given, set)):
                raise ExceptionReactionSystem.InvalidContextSet()
        
        self.cg = context_given
        self.cng = context_not_given

        if 'time' in sys.argv:
            start = time.time()

        formula = ONE
        for symbol in symbolSet:
            formula = And(formula, self.cause(symbol))
            formula = formula.to_dnf()
        
        formula = self._fbs(formula, steps)
        
        if not isinstance(formula, Atom) and formula.is_dnf():
            formula = espresso_exprs(formula)[0]

        if 'time' in sys.argv:
            print(time.time() - start)

        return formula

    
    def _fbs(self, formula, i, inv_nf=False):
        if isinstance(formula, Constant):
            pass

        elif isinstance(formula, Variable):
            symbol = formula.name
            if (i,symbol) in self.cg:
                formula = ONE
            elif (i,symbol) in self.cng:
                formula = ZERO
            else:
                formula = var('{}_{}'.format(symbol, i))
            
            if i > 0:
                formula = Or(formula, self._fbs(self.cause(symbol), i-1, inv_nf))

        elif isinstance(formula, Complement):
            formula = Not(self._fbs(Not(formula), i, not inv_nf))

        elif isinstance(formula, OrAndOp):
            Op = And if isinstance(formula, AndOp) else Or
            formula = Op(
                self._fbs(formula.xs[0], i, inv_nf),
                self._fbs(Op(*formula.xs[1:]), i, inv_nf))

        else:
            assert()

        formula = formula.to_cnf() if inv_nf else formula.to_dnf()

        return formula


    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.A == other.A

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.A)

    def __str__(self):
        return 'ReactionSystem({})'.format(str(self.A))

    def __repr__(self):
        return str(self)
