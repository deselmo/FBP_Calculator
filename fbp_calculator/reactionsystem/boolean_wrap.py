# -*- coding: utf-8 -*-

from pyeda.boolalg.expr import (
    Not,
    And,
    Or,
    expr,
    exprvar as var,
    Constant,
    Literal,
    Variable,
    Complement,
    NotOp,
    AndOp,
    OrOp,
    OrAndOp)

ZERO = expr(False)
ONE = expr(True)
