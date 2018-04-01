from .boolean_wrap import (
    Or,
    ZERO)
    
from .reaction import Reaction
from .exceptions import ExceptionReactionSystem


class ReactionSet(set):
    def __init__(self, reactions=None):
        if reactions is None:
            super(ReactionSet, self).__init__()
        else:
            for reaction in reactions:
                self.add(reaction)

    def add(self, reaction):
        if not isinstance(reaction, Reaction): raise ExceptionReactionSystem.InvalidReaction()
        super(ReactionSet, self).add(reaction)


    def cause(self, symbol):
        Reaction._check_symbol(symbol)

        cause = ZERO
        for reaction in self:
            if symbol in reaction.P:
                cause = Or(cause, reaction.ap())
        return cause

