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
    OrOp)

ZERO = expr(False)
ONE = expr(True)
