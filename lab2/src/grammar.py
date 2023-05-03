class Grammar:
    def __init__(self, nts, ts, rs, stS):
        self.nonterminals = nts
        self.terminals = ts
        self.rules = rs
        self.startingSymbol = stS

    def __init__(self):
        self.nonterminals = arraylist()
        self.terminals = arraylist()
        self.rules = arraylist()
        self.startingSymbol = None

    @staticmethod
    def getString(g):
        s = "Grammar{nonterminals="
        for nt in g.nonterminals:
            s += nt.name + " "
        s += ", terminals="
        for t in g.terminals:
            s += t.name + " "
        s += "\nrules="
        for rl in g.rules:
            s += "("
            s += rl.leftPart.name
            s += " -> "
            for rp in rl.rightPart:
                s += rp.name + " "
            s += ")"
        s += "\nstartingSymbol="
        s += g.startingSymbol.name + "}"
        return s