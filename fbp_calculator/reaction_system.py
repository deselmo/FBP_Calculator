from sympy import Symbol
from sympy import Not
from sympy import And
from sympy import Or
from sympy import to_dnf


class ExceptionReactionSet(Exception): pass

class ExceptionImpossibleReaction(ExceptionReactionSet): pass
class ExceptionSymbolsMustBeLetters(ExceptionReactionSet): pass
class ExceptionReactantSetCannotBeEmpty(ExceptionReactionSet): pass
class ExceptionProductSetCannotBeEmpty(ExceptionReactionSet): pass
class ExceptionInvalidReaction(ExceptionReactionSet): pass
class ExceptionInvalidReactionSet(ExceptionReactionSet): pass
class ExceptionInvalidNumber(ExceptionReactionSet): pass
class ExceptionInvalidFormula(ExceptionReactionSet): pass


class Reaction:
    def __init__(self, R, I, P):
        self.R = R
        self.I = I
        self.P = P


    def _check_reaction_applicability(self):
        if self.R.issubset(self.I):
            raise ExceptionImpossibleReaction()


    @staticmethod
    def _check_symbol(e):
        if not isinstance(e, str) or not e.isalpha(): raise ExceptionSymbolsMustBeLetters()


    @staticmethod
    def _check_symbol_set(s):
        if isinstance(s, str):
            s = set(s.split(' '))
            if '' in s:
                s.remove('')
        s = frozenset(s)
        for e in s:
            Reaction._check_symbol(e)
        return s
        

    @staticmethod
    def _str_frozenset(s):
        return '{' + ('' if len(s) == 0 else ', '.join(s)) + '}'


    @property
    def R(self): return self._R

    @R.setter
    def R(self, R):
        setR = Reaction._check_symbol_set(R)
        if len(setR) == 0: raise ExceptionReactantSetCannotBeEmpty()
        self._R = setR

        self._check_reaction_applicability()


    @property
    def I(self):
        try:
            return self._I
        except AttributeError:
            return set()

    @I.setter
    def I(self, I):
        setI = Reaction._check_symbol_set(I)
        self._I = setI

        self._check_reaction_applicability()


    @property
    def P(self): return self._P

    @P.setter
    def P(self, P):
        setP = Reaction._check_symbol_set(P)
        if len(setP) == 0: raise ExceptionProductSetCannotBeEmpty()
        self._P = setP


    def ap(self):
        f = True
        for symbol in self.R:
            f = And(f, Symbol(symbol))
        for symbol in self.I:
            f = And(f, Not(Symbol(symbol)))
        return f


    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.R == other.R and self.I == other.I and self.P == other.P

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.R, self.I, self.P))


    def __str__(self):
        return 'Reaction(R: {}, I: {}, P: {})'.format(
            self._str_frozenset(self.R), self._str_frozenset(self.I), self._str_frozenset(self.P))

    def __repr__(self):
        return str(self)



class ReactionSet(set):
    def __init__(self, reactions=None):
        if reactions is None:
            super(ReactionSet, self).__init__()
        else:
            for reaction in reactions:
                self.add(reaction)

    def add(self, reaction):
        if not isinstance(reaction, Reaction): raise ExceptionInvalidReaction()
        super(ReactionSet, self).add(reaction)


    def cause(self, symbol):
        Reaction._check_symbol(symbol)

        cause = False
        for reaction in self:
            if symbol in reaction.P:
                cause = Or(cause, reaction.ap())
        return cause



class ReactionSystem():
    def __init__(self, A):
        self.A = A

    @property
    def A(self): return self._A

    @A.setter
    def A(self, A):
        if not isinstance(A, ReactionSet): raise ExceptionInvalidReactionSet()
        self._A = A

    def cause(self, symbol):
        return self.A.cause(symbol)

    def fbp(self, symbol, steps):
        Reaction._check_symbol(symbol)
        if not isinstance(steps, int) or steps < 0: raise ExceptionInvalidNumber()
        return to_dnf(self._fbs(self.cause(symbol), steps))


    def _fbs(self, formula, i):
        if isinstance(formula, Symbol):
            if i > 0:
                return Or(Symbol(str(formula) + '_' + str(i)), self._fbs(self.cause(str(formula)), i-1))
            return Symbol(str(formula) + '_' + str(i))

        elif isinstance(formula, Not):
            return Not(self._fbs(formula.args[0], i))

        elif isinstance(formula, And):
            return And(self._fbs(formula.args[0], i), self._fbs(formula.args[1], i))

        elif isinstance(formula, Or):
            return Or(self._fbs(formula.args[0], i), self._fbs(formula.args[1], i))

        elif isinstance(formula, bool):
            return formula

        raise ExceptionInvalidFormula()


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



# rs = ReactionSystem(ReactionSet({
#     Reaction({'A'},{},{'B'}),
#     Reaction({'C','D'},{},{'E','F'}),
#     Reaction({'G'},{'B'},{'E'})
# }))

# print(rs.fbp('E', 3))
