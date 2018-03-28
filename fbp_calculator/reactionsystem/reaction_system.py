from pyeda.inter import expr
from pyeda.inter import espresso_exprs

from .var import var

from boolexpr import \
    not_ as Not, \
    and_s as And, \
    or_s as Or, \
    ZERO, \
    ONE

from boolexpr.wrap import \
    Atom, \
    Constant, \
    Literal, \
    Variable, \
    Complement, \
    NegativeOperator as NotOp, \
    And as AndOp, \
    Or as OrOp

from .reaction import Reaction
from .reaction_set import ReactionSet
from .exceptions import ExceptionReactionSystem



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

    def fbp(self, symbols, steps, context_given_set=set(), context_not_given_set=set()):
        self._context_given_set = context_given_set
        self._context_not_given_set = context_not_given_set
        
        symbolSet = Reaction._create_symbol_set(symbols)
        formula = True
        for symbol in symbolSet:
            Reaction._check_symbol(symbol)
            if not isinstance(steps, int) or steps < 0: raise ExceptionReactionSystem.InvalidNumber()
            formula = And(formula, self._fbs(self.cause(symbol), steps))

        formula = expr(str(formula.to_dnf()))
        
        if  not isinstance(formula, Atom) and formula.is_dnf():
            formula = espresso_exprs(formula)[0]

        return formula


    def _fbs(self, formula, i):
        if isinstance(formula, Constant):
            formula_result = formula

        elif isinstance(formula, Variable):
            symbol = str(formula)
            if (i,symbol) in self._context_given_set:
                formula_result = ONE
            elif (i,symbol) in self._context_not_given_set:
                formula_result = ZERO
            else:
                formula_result = var('{}_{}'.format(symbol, i))
            if i > 0:
                formula_result = Or(formula_result, self._fbs(self.cause(symbol), i-1))

        elif isinstance(formula, Complement) or isinstance(formula, NotOp):
            formula_result = Not(self._fbs(Not(formula), i))

        elif isinstance(formula, AndOp):
            formula_result = ONE
            for formula_x in formula.args:
                formula_result = And(formula_result, self._fbs(formula_x, i))

        elif isinstance(formula, OrOp):
            formula_result = ZERO
            for formula_x in formula.args:
                formula_result = Or(formula_result, self._fbs(formula_x, i))

        return formula_result.simplify()



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


if __name__ == '__main__':
    rs = ReactionSystem(ReactionSet({
        Reaction({'A'},{'B'}),
        Reaction({'C','D'},{'E','F'}),
        Reaction({'G'},{'E'},{'B'})
    }))

    print(rs.fbp('E', 3))
