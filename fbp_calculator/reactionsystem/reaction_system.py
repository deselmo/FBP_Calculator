from pyeda.inter import \
    expr, \
    exprvar, \
    Not, \
    And, \
    Or, \
    espresso_exprs

from pyeda.boolalg.expr import \
    Constant, \
    Literal, \
    Variable, \
    Complement, \
    NotOp, \
    AndOp, \
    OrOp


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
        
        if (formula.is_dnf() and
            not isinstance(formula, Constant) and
            not isinstance(formula, Literal)):
                formula = espresso_exprs(formula)[0]

        return formula


    def _fbs(self, formula, i):
        if isinstance(formula, Constant):
            formula_result = formula

        elif isinstance(formula, Variable):
            symbol = formula.name
            if (i,symbol) in self._context_given_set:
                formula_result = expr(True)
            elif (i,symbol) in self._context_not_given_set:
                formula_result = expr(False)
            else:
                formula_result = exprvar(symbol, i)
            if i > 0:
                formula_result = Or(formula_result, self._fbs(self.cause(symbol), i-1))

        elif isinstance(formula, Complement) or isinstance(formula, NotOp):
            formula_result = Not(self._fbs(Not(formula), i))

        elif isinstance(formula, AndOp):
            formula_result = expr(True)
            for formula_x in formula.xs:
                formula_result = And(formula_result, self._fbs(formula_x, i))

        elif isinstance(formula, OrOp):
            formula_result = expr(False)
            for formula_x in formula.xs:
                formula_result = Or(formula_result, self._fbs(formula_x, i))

        return formula_result



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
