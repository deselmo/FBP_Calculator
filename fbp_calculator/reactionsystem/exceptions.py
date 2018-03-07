class ExceptionReactionSystem():
    class ImpossibleReaction(Exception): pass
    class SymbolsMustBeLetters(Exception): pass
    class ReactantSetCannotBeEmpty(Exception): pass
    class ProductSetCannotBeEmpty(Exception): pass
    class InvalidReaction(Exception): pass
    class InvalidReactionSet(Exception): pass
    class InvalidNumber(Exception): pass
    class InvalidFormula(Exception): pass