class _fbs_calculated_item():
    def __init__(self, symbol, step, inv_nf):
        self.symbol = symbol
        self.step = step
        self.inv_nf = inv_nf
    
    def __hash__(self):
        return hash((self.symbol, self.step, self.inv_nf))
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return (
            self.symbol == other.symbol and 
            self.step == other.step and
            self.inv_nf == other.inv_nf)

    def __ne__(self, other):
        return not self.__eq__(other)

