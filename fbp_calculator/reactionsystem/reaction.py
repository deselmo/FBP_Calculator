from .var import var

from boolexpr import \
    not_ as Not, \
    and_s as And, \
    ONE

from .exceptions import ExceptionReactionSystem


class Reaction:
    def __init__(self, R, P, I = set()):
        self.R = R
        self.P = P
        self.I = I

    @staticmethod
    def _check_symbol(e):
        if not isinstance(e, str) or not e.isalpha(): raise ExceptionReactionSystem.SymbolsMustBeLetters()


    @staticmethod
    def _create_symbol_set(s):
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
        return '' if len(s) == 0 else ' '.join(sorted(list(s)))

    @staticmethod
    def _repr_frozenset(s):
        return '{' + ('' if len(s) == 0 else ', '.join(sorted(list(s)))) + '}'


    @property
    def R(self): return self._R

    @R.setter
    def R(self, R):
        setR = Reaction._create_symbol_set(R)
        if len(setR) == 0: raise ExceptionReactionSystem.ReactantSetCannotBeEmpty()
        self._R = setR


    @property
    def P(self): return self._P

    @P.setter
    def P(self, P):
        setP = Reaction._create_symbol_set(P)
        if len(setP) == 0: raise ExceptionReactionSystem.ProductSetCannotBeEmpty()
        self._P = setP


    @property
    def I(self):
        try:
            return self._I
        except AttributeError:
            return set()

    @I.setter
    def I(self, I):
        setI = Reaction._create_symbol_set(I)
        self._I = setI


    def ap(self):
        f = ONE
        for symbol in self.R:
            f = And(f, var(symbol))
        for symbol in self.I:
            f = And(f, Not(var(symbol)))
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
        string = '{} ⟶ {}'.format(
            self._str_frozenset(self.R), self._str_frozenset(self.P))
        return string + (' | {}'.format(self._str_frozenset(self.I)) if len(self.I) > 0 else '')

    def __repr__(self):
        return 'Reaction(R: {}, I: {}, P: {})'.format(
            self._repr_frozenset(self.R), self._repr_frozenset(self.I), self._repr_frozenset(self.P))
