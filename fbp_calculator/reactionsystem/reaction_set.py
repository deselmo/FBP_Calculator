# -*- coding: utf-8 -*-

from fbp_calculator.reactionsystem.boolean_wrap import (Or, ZERO)
    
from fbp_calculator.reactionsystem.reaction import Reaction
from fbp_calculator.reactionsystem.exceptions import ExceptionReactionSystem


class ReactionSet(set):
    def cause(self, symbol):
        Reaction._check_symbol(symbol)

        cause = ZERO
        for reaction in self:
            if symbol in reaction.P:
                cause = Or(cause, reaction.ap())
        return cause

