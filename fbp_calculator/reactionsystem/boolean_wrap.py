# -*- coding: utf-8 -*-

from pyeda.boolalg.expr import (
    Not,
    And,
    Or,
    expr as parse,
    exprvar as var,
    Constant,
    Literal,
    Variable,
    Complement,
    NotOp,
    AndOp,
    OrOp,
    OrAndOp)

ZERO = parse(False)
ONE = parse(True)
