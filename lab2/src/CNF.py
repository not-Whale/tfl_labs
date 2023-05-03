import java.util.ArrayList


def debug_print(str, debug):
    if debug:
        print(str)


class CNF(Grammar):
    def __init__(self, CFG, debug):
        super().__init__(CFG.nonterminals, CFG.terminals, CFG.rules, CFG.startingSymbol)
        self.convert_to_CNF(debug)

    def convert_to_CNF(self, debug):
        if self.is_CNF(debug):
            debug_print(CNF.getString(self), debug)
        else:
            self.remove_epsilons(debug)
            self.remove_chain_rules(debug)
            self.add_guard_N_terms(debug)
            self.break_rules_by_2N_terms(debug)

    def is_CNF(self, debug):
        debug_print("Checking input for being CNF", debug)
        for r in rules:
            if not (Rule.isToNtermNterm(r) or Rule.isToTerm(r) or (Rule.isToEmpty(r) and r.leftPart == startingSymbol)):
                debug_print(r.toString() + " does not fit CNF definition! Starting conversion", debug)
                return False
        debug_print("Inputted CFG is indeed in CNF", debug)
        return True

    def remove_epsilons(self, debug):
        nullable = []
        for r in self.rules:
            if Rule.isToEmpty(r) and r.leftPart.name not in nullable:
                debug_print("Inserting nonterminal " + r.leftPart + " into nullable", debug)
                nullable.append(r.leftPart.name)
        count = 0
        rulesSubset = self.rules.copy()
        rulesSubset = list(filter(lambda r: not Rule.isToEmpty(r), rulesSubset))
        while len(nullable) != count:
            count = len(nullable)
            for r in rulesSubset.copy():
                if r.leftPart.name not in nullable and all(nt.name in nullable for nt in r.rightPart):
                    debug_print("Inserting nonterminal " + r.leftPart + " into nullable", debug)
                    nullable.append(r.leftPart.name)
                    rulesSubset.remove(r)
        if self.startingSymbol.name in nullable:
            newStart = Symbol(self.startingSymbol.name.replace("]", "_0]"), self.startingSymbol.type)
            rightPart = [self.startingSymbol]
            self.rules.insert(0, Rule(newStart, rightPart))
            rightPart = [Symbol("ε")]
            self.rules.insert(1, Rule(newStart, rightPart))
            self.startingSymbol = newStart
            debug_print("Added new starting symbol to CFG", debug)
        rulesContainer = self.rules.copy()
        for r in self.rules:
            if len(r.rightPart) > 1 and any(nt.name in nullable for nt in r.rightPart):
                debug_print("Adding omitting rules for rule " + r.toString(), debug)
                currentNullables = [s for s in r.rightPart if s.name in nullable]
                nullablesInRule = len(currentNullables)
                ruleVariatons = nullablesInRule * nullablesInRule
                newRules = [r]
                rulesContainer.remove(r)
                for i in range(ruleVariatons - 2, -1, -1):
                    left = r.leftPart
                    right = []
                    pos = 0
                    for s in r.rightPart:
                        if s.type != "nonterm" or s.name not in nullable:
                            right.append(s)
                        else:
                            if i & (2 ** pos) != 0:
                                right.append(s)
                            pos += 1
                    if not right:
                        right.append(Symbol("ε"))
                    newRule = Rule(left, right)
                    equal = False
                    for nr in newRules:
                        if len(nr.rightPart) != len(newRule.rightPart):
                            continue
                        stillEqual = True
                        for j in range(len(nr.rightPart)):
                            if nr.rightPart[j].name != newRule.rightPart[j].name:
                                stillEqual = False
                                break
                        if stillEqual:
                            equal = True
                            break
                    if not equal:
                        debug_print("Adding " + newRule + ", index of " + bin(i)[2:], debug)
                        newRules.append(newRule)
                rulesContainer.extend(newRules)
        noEmptyRules = self.rules.copy()
        noEmptyRules = list(filter(lambda r: not Rule.isToEmpty(r) or r.leftPart == self.startingSymbol, noEmptyRules))
        self.rules = noEmptyRules
        for i in range(len(self.rules)):
            for j in range(i + 1, len(self.rules)):
                r1 = self.rules[i]
                r2 = self.rules[j]
                if r1.leftPart.name == r2.leftPart.name and len(r1.rightPart) == len(r2.rightPart):
                    for k in range(len(r1.rightPart)):
                        if r1.rightPart[k].name != r2.rightPart[k].name:
                            break
                    else:
                        self.rules.remove(j)
        debug_print(CNF.getString(self), debug)

    def remove_chain_rules(self, debug: bool):
        chainRules = [r for r in self.rules if len(r.rightPart) == 1 and r.rightPart[0].type == "nonterm"]
        debug_print("Chain rules: " + str(chainRules), debug)
        for chr in chainRules:
            remover = chr.leftPart
            toRemove = chr.rightPart[0]
            self.nonterminals = [nt for nt in self.nonterminals if nt.name != toRemove.name]
            debug_print("Removed nonterm " + str(toRemove) + " from nonterminals", debug)
            for r in self.rules.copy():
                if r.leftPart.name == toRemove.name:
                    r.leftPart = remover
                    debug_print(str(toRemove) + " to " + str(remover) + " rewrote rule as " + str(r), debug)
                if r == chr:
                    self.rules.remove(chr)
                    debug_print("Removing " + str(chr), debug)
        debug_print(CNF.getString(self), debug)

    def add_guard_N_terms(self, debug):
        rulesWithNotSingleTerm = [r for r in self.rules if Rule.hasTermAndNotToTerm(r)]
        debug_print("Rules that need guarding nonterminals: " + str(rulesWithNotSingleTerm), debug)
        guardedAlphabet = []
        for gr in rulesWithNotSingleTerm:
            for s in gr.rightPart:
                if s.type == "term" and s.name not in guardedAlphabet:
                    guardedAlphabet.append(s.name)
        debug_print("List of terminals that need guarding: " + str(guardedAlphabet), debug)
        for name in guardedAlphabet:
            symName = "[G_" + name + "]"
            nameCollision = False
            for nt in self.nonterminals:
                if nt.name == symName:
                    nameCollision = True
                    break
            quit = False
            for r in self.rules:
                if r.rightPart.size() == 1 and r.rightPart[0].name == name and all(
                        rule.leftPart.name != r.leftPart.name or rule.rightPart.size() != 1 or rule.rightPart[
                            0].name != name for rule in self.rules):
                    debug_print(
                        "No need to guard terminal " + name + " cause he already has a guarding nonterminal " + r.leftPart.name,
                        debug)
                    symName = r.leftPart.name
                    for r2 in self.rules:
                        if r != r2 and Rule.hasTermAndNotToTerm(r2) and name in Rule.getTerminalNames(r2):
                            newRP = []
                            for s in r2.rightPart:
                                if s.type == "term" and s.name == name:
                                    newRP.append(Symbol(symName))
                                else:
                                    newRP.append(s)
                            r2.rightPart = newRP
                    quit = True
                    break
            if quit:
                continue
            while nameCollision:
                symName = symName[:-1] + "_" + name + "]"
                nameCollision = False
                for nt in self.nonterminals:
                    if nt.name == symName:
                        nameCollision = True
                        break
            left = Symbol(symName)
            right = Symbol(name)
            rightPart = [right]
            newRule = Rule(left, rightPart)
            debug_print("Made new guarding " + str(newRule), debug)
            guarded = Symbol(symName)
            self.nonterminals.append(guarded)
            for r in self.rules:
                if r in rulesWithNotSingleTerm:
                    newRP = []
                    for s in r.rightPart:
                        if s.name != name:
                            newRP.append(s)
                        else:
                            newRP.append(guarded)
                    r.rightPart = newRP
            self.rules.append(newRule)
        debug_print(CNF.getString(self), debug)

    def break_rules_by_2N_terms(self, debug):
        breakableRules = list(self.rules)
        breakableRules = [r for r in breakableRules if Rule.isToNterms(r)]
        self.rules = [r for r in self.rules if not Rule.isToNterms(r)]
        brokenRules = []
        for breakingBarriers in list(breakableRules):
            while not breakingBarriers.rightPart:
                divideRules(breakingBarriers, brokenRules, debug)
        debug_print("New rules:" + brokenRules, debug)
        self.rules.extend(brokenRules)
        debug_print(CNF.getString(self), debug)

    def divide_rules(self, r, brb, debug):
        if len(r.rightPart) == 2:
            debug_print("Got to final partition of " + r, debug)
            rules.add(Rule(r.leftPart, r.rightPart))
            r.rightPart = []
        else:
            left = r.leftPart
            r1 = r.rightPart[0]
            r2Name = r1.name[:-1] + "f]"
            nameCollision = False
            for nt in nonterminals:
                if nt.name == r2Name:
                    nameCollision = True
                    r2Name = r2Name[:-1] + "f]"
                    break
            while nameCollision:
                nameCollision = False
                for nt in nonterminals:
                    if nt.name == r2Name:
                        nameCollision = True
                        r2Name = r2Name[:-1] + "f]"
                        break
            newRP = []
            newRP.append(r1)
            r2 = Symbol(r2Name)
            nonterminals.append(r2)
            newRP.append(r2)
            newRule = Rule(left, newRP)
            brb.append(newRule)
            debug_print("Made new " + newRule, debug)
            r.rightPart.pop(0)
            r.leftPart = r2

    def __str__(self):
        return super().__str__()
