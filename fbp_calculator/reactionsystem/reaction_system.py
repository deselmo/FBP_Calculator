from sympy import Symbol
from sympy import Not
from sympy import And
from sympy import Or
from sympy import to_dnf

from .reaction import Reaction
from .reaction_set import ReactionSet
from .exceptions import ExceptionReactionSystem


def simplify_dnf(formula):
    if formula == True or formula == False:
        return formula

    str_formula = (str(to_dnf(formula))
            .replace(' ', '')
            .replace('(', '')
            .replace(')', '')
            .split('|'))

    dnf_formula = list(map(lambda o: set(o.split('&')), str_formula))

    for current_formula in dnf_formula[:]:
        for compare_formula in dnf_formula:
            if current_formula > compare_formula:
                dnf_formula.remove(current_formula)
                break

    or_formula = False
    for current_formula in dnf_formula:
        and_formula = True
        for symbol in current_formula:
            and_formula = And(and_formula, Symbol(symbol))
        or_formula = Or(or_formula, and_formula)

    return or_formula


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

    def fbp(self, symbols, steps, context_true_set=set(), context_false_set=set()):
        self._context_true_set = context_true_set
        self._context_false_set = context_false_set
        
        symbolSet = Reaction._create_symbol_set(symbols)
        formula = True
        for symbol in symbolSet:
            Reaction._check_symbol(symbol)
            if not isinstance(steps, int) or steps < 0: raise ExceptionReactionSystem.InvalidNumber()
            formula = simplify_dnf(And(formula, self._fbs(self.cause(symbol), steps)))
        
        return formula


    def _fbs(self, formula, i):
        if isinstance(formula, Symbol):
            symbol = str(formula)
            if (i, symbol) in self._context_true_set:
                formula = True
            elif (i, symbol) in self._context_false_set:
                formula = False
            else:
                formula = Symbol(symbol + '_' + str(i))
            if i > 0:
                formula = Or(formula, self._fbs(self.cause(symbol), i-1))

        elif isinstance(formula, Not):
            formula = Not(self._fbs(formula.args[0], i))

        elif isinstance(formula, And):
            formula = And(self._fbs(formula.args[0], i), self._fbs(formula.args[1], i))

        elif isinstance(formula, Or):
            formula = Or(self._fbs(formula.args[0], i), self._fbs(formula.args[1], i))

        return simplify_dnf(formula)



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
