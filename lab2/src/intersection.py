class Intersection(Grammar):
    def __init__(self, cnf, auto, debug):
        super().__init__()
        self.nonterminals = []
        self.terminalRules = []
        self.rules = []
        self.terminals = []
        self.startingSymbol = None
        self.buildIntersection(cnf, auto, debug)

    def buildIntersection(self, cnf: CNF, auto: NFA, debug: bool):
        states: List[NFA.State] = auto.states.copy()
        finalStates: List[NFA.State] = auto.finalStates.copy()
        if len(finalStates) != 1:
            DebugPrint("Automaton has <> 1 final state!", debug)
            System.exit(10)
        finalState: NFA.State = finalStates[0]
        nonterminalsCNF: List[Symbol] = cnf.nonterminals.copy()
        CNFRules: List[Rule] = cnf.rules.copy()
        autoTransitions: List[NFA.Transition] = auto.transitions.copy()
        self.nonterminals = []
        self.startingSymbol = Three(Symbol(auto.startState.symbol.name), Symbol(cnf.startingSymbol), Symbol(finalState.symbol))
        nonterminals.append(startingSymbol)
        DebugPrint("New starting nonterminal:" + str(startingSymbol), debug)
        self.buildTerminalRules(CNFRules, autoTransitions, debug)
        DebugPrint(str(self), debug)
        self.buildNonTerminalRules(CNFRules, autoTransitions, states, debug)
        DebugPrint(str(self), debug)
        DebugPrint("Number of rules: " + str(len(rules)), debug)
        oldRuleSize: int = len(rules)
        while not (len(rules) == oldRuleSize):
            oldRuleSize = len(rules)
            self.RemoveUnreachableNonterminals(debug)
            DebugPrint(str(self), debug)
            self.removeUnproducingNonterminals(debug)
            DebugPrint(str(self), debug)
            newRuleSize: int = len(rules)
            if oldRuleSize != newRuleSize:
                self.RemoveUnreachableNonterminals(debug)
                DebugPrint(str(self), debug)
                newNewRuleSize: int = len(nonterminals)
                if newNewRuleSize != newRuleSize:
                    self.removeUnproducingNonterminals(debug)
                    DebugPrint(str(self), debug)
        print("Number of rules: " + str(len(rules)))
        print(str(self))

    def buildTerminalRules(self, CNFRules, autoTransitions, debug):
        DebugPrint("Adding terminal rules", debug)
        for r in CNFRules:
            if Rule.isToTerm(r):
                term = Symbol(r.rightPart[0])
                if not any(t.name == term.name for t in self.terminals):
                    self.terminals.append(term)
                nonterm = Symbol(r.leftPart.name)
                for tr in autoTransitions:
                    if tr.alphabetic.name == term.name:
                        newNonterm = Three(Symbol(tr.left.symbol.name), nonterm, Symbol(tr.right.symbol.name))
                        rightPart = [term]
                        RP = [Three(Symbol(), Symbol(s), Symbol()) for s in rightPart]
                        newRule = IntersectedRule(newNonterm, RP, debug)
                        DebugPrint("Made new rule " + str(newRule), debug)
                        self.rules.append(newRule)
                        self.terminalRules.append(newRule)
                        if not any(
                                nt.start.name == newNonterm.start.name and nt.end.name == newNonterm.end.name and nt.nonterm.name == newNonterm.nonterm.name
                                for nt in self.nonterminals):
                            self.nonterminals.append(newNonterm)

    def buildNonTerminalRules(self, CNFRules, autoTransitions, states, debug):
        DebugPrint("Adding nonterminal rules", debug)
        DebugPrint("Transitions: " + autoTransitions.stream().map((s) -> s.toString()).collect(Collectors.joining(", ")), debug)
        for r in CNFRules:
            if Rule.isToNtermNterm(r):
                right1 = r.rightPart[0]
                right2 = r.rightPart[1]
                DebugPrint("Starting to build nonterminal rules for " + r, debug)
                for p in states:
                    for q in states:
                        left = Three(Symbol(p.symbol), Symbol(r.leftPart), Symbol(q.symbol))
                        DebugPrint("Checking for producing of leftpart Three" + left, debug)
                        if CheckForProducing(left, CNFRules, debug):
                            for qi in states:
                                RPleft = Three(Symbol(p.symbol), Symbol(right1), Symbol(qi.symbol))
                                DebugPrint("Checking for producing of left Three " + RPleft, debug)
                                if CheckForProducing(RPleft, CNFRules, debug):
                                    if not any(nt.start.name == RPleft.start.name and nt.end.name == RPleft.end.name and nt.nonterm.name == RPleft.nonterm.name for nt in self.nonterminals):
                                        self.nonterminals.append(RPleft)
                                    RPright = Three(Symbol(qi.symbol), Symbol(right2), Symbol(q.symbol))
                                    DebugPrint("Checking for producing of right Three " + RPright, debug)
                                    if CheckForProducing(RPright, CNFRules, debug):
                                        if not any(nt.start.name == RPright.start.name and nt.end.name == RPright.end.name and nt.nonterm.name == RPright.nonterm.name for nt in self.nonterminals):
                                            self.nonterminals.append(RPright)
                                        if RPleft.name == left.name and not any(tr.leftPart.name == left.name for tr in terminalRules):
                                            DebugPrint("Got self-recursive nonterminal " + RPleft.name, debug)
                                            continue
                                        if RPright.name == left.name and not any(tr.leftPart.name == left.name for tr in terminalRules):
                                            DebugPrint("Got self-recursive nonterminal " + RPright.name, debug)
                                            continue
                                        RP = []
                                        RP.append(RPleft)
                                        RP.append(RPright)
                                        newRule = IntersectedRule(left, RP, debug)
                                        DebugPrint("Got new Rule: " + newRule, debug)
                                        rules.append(newRule)

    def CheckForProducing(self, left, CNFRules, debug):
        isNotOnlyToTerm = False
        isNotProducing = True
        for r2 in CNFRules:
            if r2.leftPart.name == left.nonterm.name and not (Rule.isToTerm(r2) or Rule.isToEmpty(r2)):
                isNotOnlyToTerm = True
                isNotProducing = False
                DebugPrint("For " + left + " nonterm " + r2.leftPart.name + " rewrites not only to term: " + r2.toString(), debug)
                break
        if not isNotOnlyToTerm:
            for termR in self.terminalRules:
                DebugPrint(termR.leftPart.name + " !=? " + left.name, debug)
                if termR.leftPart.name == left.name:
                    DebugPrint("Nonterm " + left.nonterm.name + " rewrites only to terms, but has a terminal rule for " + left, debug)
                    isNotProducing = False
                    break
        if not isNotProducing:
            return True
        else:
            DebugPrint("Rule with nonterminal " + left + " omitted because it isn't producing", debug)
            return False


    def RemoveUnreachableNonterminals(self, debug):
        for nt in self.nonterminals:
            nt.reachable = False
        countReachable = 1
        countToCompare = 1
        self.startingSymbol.reachable = True
        countReachable += self.markReachables(self.startingSymbol)
        DebugPrint("CountR: " + str(countReachable) + ", CountTC: " + str(countToCompare) + "\n", debug)
        while countReachable != countToCompare:
            countToCompare = countReachable
            countReachable += self.markReachables(self.startingSymbol)
        DebugPrint("Current nonterminals: " + ", ".join([s.name + " reach:" + str(s.reachable) for s in self.nonterminals]), debug)
        for r in self.rules[:]:
            if r in self.terminalRules:
                for nt in self.nonterminals:
                    if nt.name == r.leftPart.name and not nt.reachable:
                        self.rules.remove(r)
                        self.terminalRules.remove(r)
                        break
            else:
                for rpt in r.rightPart:
                    if not any(nt.name == rpt.name for nt in self.nonterminals):
                        self.rules.remove(r)
                for nt in self.nonterminals:
                    if nt.name == r.leftPart.name and not nt.reachable:
                        self.rules.remove(r)
        self.nonterminals = [nt for nt in self.nonterminals if nt.reachable]

        def removeUnproducingNonterminals(self, debug):
            for nt in self.nonterminals:
                nt.producing = False
            countProducing = 0
            countToCompare = 0
            for r in self.rules:
                DebugPrint("Checking rule " + r, debug)
                if (len(r.rightPart) == 1):
                    DebugPrint("Marking producing of " + r, debug)
                    for nt in self.nonterminals:
                        if (nt.name == r.leftPart.name):
                            nt.producing = True
                            countProducing += 1
                            break
            countProducing += markProducing()
            DebugPrint("CountP: " + countProducing + ", CountTC: " + countToCompare + "
                                                                                      ", debug)
            while (countProducing != countToCompare):
                countToCompare = countProducing
                countProducing += markProducing()
            DebugPrint(
                "Current nonterminals: " + ", ".join([s.name + " prod:" + str(s.producing) for s in self.nonterminals]),
                debug)
            for r in list(self.rules):
                for nt in self.nonterminals:
                    if (nt.name == r.leftPart.name and not nt.producing):
                        self.rules.remove(r)
            self.nonterminals = [nt for nt in self.nonterminals if nt.producing]


    def markReachables(self, s: Three) -> int:
        added = 0
        for ir in self.rules:
            if ir.leftPart.name == s.name:
                for rpt in ir.rightPart:
                    for nt in self.nonterminals:
                        if nt.name == rpt.name and not nt.reachable:
                            added += 1
                            nt.reachable = True
                            added += self.markReachables(nt)
                            break
        return added

    def markProducing(self):
        added = 0
        for ir in self.rules:
            for nt in self.nonterminals:
                if nt.name == ir.leftPart.name:
                    if not nt.producing:
                        prod = True
                        for rpt in ir.rightPart:
                            for nt2 in self.nonterminals:
                                if rpt.name == nt2.name and not nt2.producing:
                                    prod = False
                                    break
                        if prod:
                            added += 1
                            nt.producing = True
        return added

    def __str__(self):
        return "Intersection{" + \
                "startingSymbol=" + str(self.startingSymbol) + \
                "nonterminals=" + str(self.nonterminals) + \
                "rules=" + str(self.rules) + \
                "terminals=" + str(self.terminals) + \
                '}'



    class Three:
        def __init__(self, start, nonterm, end):
            self.start = start
            self.nonterm = nonterm
            self.end = end
            if ((start.name == None) or (end.name == None)):
                self.name = nonterm.name
            else:
                self.name = "<" + start.name + ", " + nonterm.name + ", " + end.name + ">"

        def equals(self, t):
            return (self.start.name == t.start.name) and (self.nonterm.name == t.nonterm.name) and (self.end.name == t.end.name)

        def __str__(self):
            if ((self.start == None) or (self.end == None)):
                return self.nonterm.name
            else:
                return "<" + self.start.name + "," + self.nonterm.name + "," + self.end.name + ">"

    class IntersectedRule(Rule):
        def __init__(self, left, right, debug):
            super().__init__()
            self.leftPart = left
            self.rightPart = right

        def __str__(self):
            return "{" + str(self.leftPart) + " -> " + ", ".join([s.name for s in self.rightPart]) + "}"

    @staticmethod
    def DebugPrint(str, debug):
        if debug:
            print(str)
