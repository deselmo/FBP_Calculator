# -*- coding: utf-8 -*-

from fbp_calculator.reactionsystem.boolean_wrap import (
    Not,
    And,
    ONE,
    var)

from fbp_calculator.reactionsystem.exceptions import ExceptionReactionSystem
import re

separator_regex = '\s' #pylint: disable=W1401
symbol_regex = '[a-zA-Z]+[a-zA-Z\d__]*' #pylint: disable=W1401
symbol_list_regex = '{}*({}{}+)*{}{}*'.format(
    separator_regex,
    symbol_regex,
    separator_regex,
    symbol_regex,
    separator_regex)
reaction_regex = '^{}->{}(\|{})?$'.format( #pylint: disable=W1401
            symbol_list_regex,symbol_list_regex,symbol_list_regex)

class Reaction:
    def __init__(self, string='', R='', P='', I=''):
        if string and Reaction.match(string):
            split = re.split('(->|\|)', string) #pylint: disable=W1401
            self.R = split[0]
            self.P = split[2]
            self.I = split[4] if len(split) == 5 else I
        else:
            self.R = R
            self.P = P
            self.I = I

    @staticmethod
    def match(string):
        return re.match(reaction_regex, string)

    @staticmethod
    def _get_symbol_regex():
        return symbol_regex

    @staticmethod
    def _get_symbol_list_regex():
        return symbol_list_regex

    @staticmethod
    def _check_symbol(s):
        if (not isinstance(s, str) or
            not re.match(symbol_regex, s)):
                raise ExceptionReactionSystem.InvalidSyntax()


    @staticmethod
    def _create_symbol_set(s):
        if not isinstance(s, str):
            raise ExceptionReactionSystem.InvalidSyntax()
        if s == '':
            return frozenset()
        if not re.match('^{}$'.format(symbol_list_regex), s):
            raise ExceptionReactionSystem.InvalidSyntax()
        s = set(re.sub('{}+'.format(separator_regex),' ',s).split(' ')) #pylint: disable=W1401
        s.discard('')
        return frozenset(s)
        

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
        string = '{} -> {}'.format(
            self._str_frozenset(self.R), self._str_frozenset(self.P))
        return string + (' | {}'.format(self._str_frozenset(self.I)) if len(self.I) > 0 else '')

    def __repr__(self):
        return 'Reaction(R: {}, I: {}, P: {})'.format(
            self._repr_frozenset(self.R), self._repr_frozenset(self.I), self._repr_frozenset(self.P))
