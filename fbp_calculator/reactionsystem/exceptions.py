# -*- coding: utf-8 -*-

class ExceptionReactionSystem():
    class InvalidSyntax(Exception): pass
    class ReactantSetCannotBeEmpty(Exception): pass
    class ProductSetCannotBeEmpty(Exception): pass
    class InvalidReaction(Exception): pass
    class InvalidReactionSet(Exception): pass
    class InvalidNumber(Exception): pass
    class InvalidFormula(Exception): pass
    class InvalidContextSet(Exception): pass