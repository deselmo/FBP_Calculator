from sympy import Symbol
from sympy import Not
from sympy import And
from sympy import Or
from sympy import simplify_logic

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

    def fbp(self, symbols, steps):
        symbolSet = Reaction._create_symbol_set(symbols)
        formula = True
        for symbol in symbolSet:
            Reaction._check_symbol(symbol)
            if not isinstance(steps, int) or steps < 0: raise ExceptionReactionSystem.InvalidNumber()
            formula = simplify_logic(And(formula, self._fbs(self.cause(symbol), steps)), form='dnf', deep=False)
        
        return formula


    def _fbs(self, formula, i):
        if isinstance(formula, Symbol):
            if i > 0:
                return Or(Symbol(str(formula) + '_' + str(i)), self._fbs(self.cause(str(formula)), i-1))
            formula = Symbol(str(formula) + '_' + str(i))

        elif isinstance(formula, Not):
            formula = Not(self._fbs(formula.args[0], i))

        elif isinstance(formula, And):
            formula = And(self._fbs(formula.args[0], i), self._fbs(formula.args[1], i))

        elif isinstance(formula, Or):
            formula = Or(self._fbs(formula.args[0], i), self._fbs(formula.args[1], i))

        elif isinstance(formula, bool):
            pass

        else:
            raise ExceptionReactionSystem.InvalidFormula()

        return simplify_logic(formula, form='dnf', deep=False)



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
