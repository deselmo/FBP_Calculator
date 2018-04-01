from pyeda.boolalg.expr import \
    And, \
    Or, \
    expr, \
    AndOp, \
    OrOp
ZERO = expr(False)
ONE = expr(True)

# class a():
#     i = 0

#     def print(self):
#         print(self.i)
#         self.i+=1

# a = a()

def to_dnf(e):
    return nnf_to_dnf(e.to_nnf())


def nnf_to_dnf(e):
    if isinstance(e, OrOp):
        result = ZERO
        for x in e.xs:
            result = Or(result, nnf_to_dnf(x))
        return result
        
    elif isinstance(e, AndOp):
        or_formula = False
        other = ONE
        for x in e.xs:
            if not or_formula and isinstance(x, OrOp):
                or_formula = x
            else:
                other = And(other, x)
        
        if or_formula:
            result = ZERO
            for x in or_formula.xs:
                result = Or(result, nnf_to_dnf(And(x, other)))
            return result
    return e
