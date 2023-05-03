class NFA:
    def __init__(self, sts, fSts, alph, stSym, tr):
        self.states = sts
        self.finalStates = fSts
        self.alphabet = alph
        self.startState = stSym
        self.transitions = tr

    class Transition:
        def __init__(self, left, alph, right):
            self.left = left
            self.alphabetic = alph
            self.right = right

        def __str__(self):
            return "{" + left.symbol.name + ", " + alphabetic.name + ", " + right.symbol.name + "}"

    class State:
        def __init__(self, name, reachable=False, producing=False):
            self.symbol = name
            self.reachable = reachable
            self.producing = producing

    @staticmethod
    def RGtoAutomaton(rg, debug):
        states = []
        for nterm in rg.nonterminals:
            states.append(State(nterm))
        finalStates = []
        alphabet = rg.terminals
        startState = getStateBySymbol(rg.startingSymbol, states)
        transitions = []

        new_final = State(Symbol("[S_final]", "nonterm"))
        states.append(new_final)
        finalStates.append(new_final)

        for r in rg.rules:
            if Rule.isToEmpty(r):
                alreadyFinal = False
                for fs in finalStates:
                    if fs.symbol.name == r.leftPart.name:
                        alreadyFinal = True
                        break
                if not alreadyFinal:
                    finalStates.append(getStateBySymbol((r.leftPart), states))
            elif Rule.isToTerm(r):
                transitions.append(Transition(getStateBySymbol((r.leftPart), states), r.rightPart[0], new_final))
            elif Rule.isToTermNterm(r):
                transitions.append(Transition(getStateBySymbol((r.leftPart), states), r.rightPart[0], getStateBySymbol((r.rightPart[1]), states)))
            else:
                print("Incorrect rule detected in conversion from RG to NFA: " + r.leftPart.name + " -> " + r.rightPart[0].name + "...")
        # удаляем недостижимые нетерминалы
        startState.reachable = True
        countReachable = 1
        countToCompare = 1
        countReachable += markReachables(startState, transitions)
        DebugPrint("CountR: " + countReachable + ", CountTC: " + countToCompare + "\n", debug)
        while countReachable != countToCompare:
            countToCompare = countReachable
            countReachable += markReachables(startState, transitions)
        states = [st for st in states if st.reachable]
        finalStates = [fSt for fSt in finalStates if fSt.reachable]
        transitions = [tr for tr in transitions if tr.right.reachable]
        dPrint = "NFA:{States:["
        if debug:
            for st in states:
                dPrint += st.symbol.name + " "
            dPrint += "]; finalStates:["
            for fst in finalStates:
                dPrint += fst.symbol.name + " "
            dPrint += "]; alphabet:["
            for al in alphabet:
                dPrint += al.name + " "
            dPrint += "]; startState: " + startState.symbol.name + "; transitions: ["
            for tr in transitions:
                dPrint += "<" + tr.left.symbol.name + "," + tr.alphabetic.name + "," + tr.right.symbol.name + ">; "
            dPrint += "]}\n"
        DebugPrint(dPrint, debug)
        # удаляем непорождающие терминалы
        reversedTransitions = []
        for tr in transitions:
            reversedTransitions.append(Transition(tr.right, tr.alphabetic, tr.left))
        newReversedReachState = State(Symbol("S_REV", "nonterm"))
        for fs in finalStates:
            reversedTransitions.append(Transition(newReversedReachState, Symbol("dummy", "term"), fs))
        newReversedReachState.producing = True
        countProducing = 1
        countToCompare = 1
        countProducing += markProducers(newReversedReachState, reversedTransitions)
        DebugPrint("CountPR: " + countProducing + ", CountTC: " + countToCompare + "\n", debug)
        while countProducing != countToCompare:
            countToCompare = countProducing
            countProducing += markProducers(newReversedReachState, reversedTransitions)
        states = [st for st in states if st.producing]
        finalStates = [fSt for fSt in finalStates if fSt.producing]
        transitions = [tran for tran in transitions if states.__contains__(tran.right)]
        alphabet = [alpha for alpha in alphabet if hasVertexWithTerminal(alpha, transitions)]
        dPrint = "NFA:{States:["
        if debug:
            for st in states:
                dPrint += st.symbol.name + " "
            dPrint += "]; finalStates:["
            for fst in finalStates:
                dPrint += fst.symbol.name + " "
            dPrint += "]; alphabet:["
            for al in alphabet:
                dPrint += al.name + " "
            dPrint += "]; startState: " + startState.symbol.name + "; transitions: ["
            for tr in transitions:
                dPrint += "<" + tr.left.symbol.name + "," + tr.alphabetic.name + "," + tr.right.symbol.name + ">; "
            dPrint += "]}\n"
        DebugPrint(dPrint, debug)
        return NFA(states, finalStates, alphabet, startState, transitions)


    @staticmethod
    def markReachables(s, transitions):
        added = 0
        for tr in transitions:
            if tr.left.symbol == s.symbol and not tr.right.reachable:
                added += 1
                tr.right.reachable = True
                added += NFA.markReachables(tr.right, transitions)
        return added

    @staticmethod
    def markProducers(s, transitions):
        added = 0
        for tr in transitions:
            if tr.left.symbol == s.symbol and not tr.right.producing:
                added += 1
                tr.right.producing = True
                added += NFA.markProducers(tr.right, transitions)
        return added


    @staticmethod
    def getStateBySymbol(s, states):
        for st in states:
            if s.name == st.symbol.name:
                return st
        print("Couldn't find the right state! " + s.name + " state not found!")
        exit(8)
        return State(Symbol("0"))

    @staticmethod
    def hasVertexWithTerminal(a, tran):
        res = False
        for tr in tran:
            if tr.alphabetic == a:
                res = True
                break
        return res

    @staticmethod
    def DebugPrint(str, debug):
        if debug:
            print(str)
