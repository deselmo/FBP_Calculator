class _fbs_iterate_item():
    def __init__(self, formula, parent, step, inv_nf):
        self.formula = formula
        self.parent = parent
        self.step = step
        self.inv_nf = inv_nf
        self.remained = 1
        self.childs = []