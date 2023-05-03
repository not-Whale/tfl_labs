class Parser:
    def __init__(self):
        pass

    def parse_grammars1(self, testInput, debug):
        grammars = []
        testInput = testInput.replace("\\s", "")

        if not testInput.startswith("Context-freegrammar:"):
            print("Incorrect test file format: no CFG denomination found!")
            exit(4)

        testInput = testInput.replaceFirst("Context-freegrammar:", "")

        if "Regulargrammar:" not in testInput:
            print("Incorrect test file format: no Regular Grammar denomination found!")
            exit(4)

        delimeter = testInput.indexOf("Regulargrammar:")
        CFGinput = testInput[0:delimeter]
        RGinput = testInput[delimeter + 15:]

        if CFGinput.isBlank():
            print("No CFG input in test after denomination!")
            exit(4)

        if RGinput.isBlank():
            print("No Regular Grammar input in test after denomination!")
            exit(4)

        CFGtokens = Tokenize(CFGinput, debug)
        RGtokens = Tokenize(RGinput, debug)

        CFG = ParseGrammar(CFGtokens, debug)
        RG = ParseGrammar(RGtokens, debug)

        grammars[0] = CFG
        grammars[1] = RG
        return grammars

    def Tokenize(self, str, debug):
        separatedStrings = []
        newStr = str
        buf = ""
        insideNonterm = False
        while newStr != "":
            s = newStr[0]
            if s == "[":
                nontermFinish = newStr.indexOf("]")
                if nontermFinish == -1:
                    print("Nonterminal parentheses do not close in " + newStr)
                    exit(5)
                else:
                    buf += newStr[0:nontermFinish + 1]
                    separatedStrings.append(buf)
                    buf = ""
                    newStr = newStr[nontermFinish + 1:]
            elif s == "|":
                separatedStrings.append("|")
                newStr = newStr[1:]
            elif s == "-" and newStr[1] == ">":
                separatedStrings.append("->")
                newStr = newStr[2:]
            elif s == "ε":
                separatedStrings.append("ε")
                newStr = newStr[1:]
            elif s >= "a" and s <= "z":
                separatedStrings.append(str(s))
                newStr = newStr[1:]
            else:
                print("Got incorrect symbol during tokenization: " + s + " leftover string: " + newStr)
                exit(5)
        symbols = []
        DebugPrint("Received separated strings:", debug)
        DebugPrint("\n", debug)
        for x in separatedStrings:
            DebugPrint(x, debug)
        DebugPrint("\n", debug)
        for x in separatedStrings:
            symbols.append(Symbol(x))
        DebugPrint("Made Array of symbols:", debug)
        DebugPrint("\n", debug)
        for x in symbols:
            DebugPrint(x.name + " type: " + x.type + ";", debug)
        DebugPrint("\n", debug)
        return symbols


    def ParseGrammar(self, tokens: List[Symbol], debug: bool) -> Grammar:
        nonterminals = []
        terminals = []
        rules = []
        startingSymbol = None

        currLeftPart = None
        lastSymbol = None
        sBuf = []
        first_iter = True
        while tokens:
            token = tokens[0]
            if token.type == "arrow":
                if lastSymbol is None:
                    print("Arrow found with no preceding nonterminal")
                    exit(7)
                if currLeftPart is not None:
                    if not sBuf:
                        DebugPrint("Trying to make a rule with no right part; first-arrow guaranteed", debug)
                        if not first_iter:
                            exit(7)
                        first_iter = False
                    if not currLeftPart.type == "nonterm":
                        print("Trying to make a rule with not a nonterm as a left part: " + currLeftPart)
                        exit(7)
                    rules.append(Rule(currLeftPart, sBuf))
                currLeftPart = lastSymbol
                sBuf = []
                lastSymbol = token
                tokens.pop(0)
                continue
            if token.type == "alternative":
                if lastSymbol is None:
                    print("Alternative found with no preceding nonterminal")
                    exit(7)
                if lastSymbol.type == "nonterm" or lastSymbol.type == "term" or lastSymbol.type == "empty":
                    sBuf.append(lastSymbol)
                if currLeftPart is not None:
                    if not sBuf:
                        print("Trying to make a rule with no right part")
                        DebugPrint("CurrleftPart: " + currLeftPart.name, debug)
                        exit(7)
                    rules.append(Rule(currLeftPart, sBuf))
                if not currLeftPart.type == "nonterm":
                    print("Trying to make a rule with not a nonterm as a left part: " + currLeftPart)
                    exit(7)
                sBuf = []
                lastSymbol = token
                tokens.pop(0)
                continue
            if token.type == "term":
                contained = False
                for term in terminals:
                    if term.name == token.name:
                        contained = True
                        break
                if not contained:
                    terminals.append(token)
                if currLeftPart is None:
                    print(
                        "Encountered a terminal before any nonterminal could be used as a left part: " + token.name)
                    exit(7)
                if lastSymbol is not None and (
                        lastSymbol.type == "nonterm" or lastSymbol.type == "term" or lastSymbol.type == "empty"):
                    sBuf.append(lastSymbol)
                lastSymbol = token
                tokens.pop(0)
            if token.type == "nonterm":
                contained = False
                for nterm in nonterminals:
                    if nterm.name == token.name:
                        contained = True
                        break
                if not contained:
                    nonterminals.append(token)
                if lastSymbol is not None and (
                        lastSymbol.type == "nonterm" or lastSymbol.type == "term" or lastSymbol.type == "empty"):
                    sBuf.append(lastSymbol)
                lastSymbol = token
                tokens.pop(0)
            if token.type == "empty":
                if lastSymbol is not None and (
                        lastSymbol.type == "nonterm" or lastSymbol.type == "term" or lastSymbol.type == "empty"):
                    sBuf.append(lastSymbol)
                lastSymbol = token
                tokens.pop(0)
            if lastSymbol.type == "nonterm" or lastSymbol.type == "term" or lastSymbol.type == "empty":
                sBuf.append(lastSymbol)
            if sBuf:
                rules.append(Rule(currLeftPart, sBuf))
            for s in nonterminals:
                if s.name == "[S]":
                    startingSymbol = s
                    break
            if startingSymbol is None:
                print("Found no starting symbol [S] in Right Linear Grammar")
                exit(6)
            grammar = Grammar(nonterminals, terminals, rules, startingSymbol)
            DebugPrint("Parsed Grammar:\n" + Grammar.getString(grammar) + "\n", debug)
            return Grammar(nonterminals, terminals, rules, startingSymbol)


    def Tokenize(self, str: str, debug: bool) -> List[Symbol]:
        separatedStrings = []
        newStr = str
        buf = ""
        insideNonterm = False
        while newStr:
            s = newStr[0]
            if s == '[':
                nontermFinish = newStr.find("]")
                if nontermFinish == -1:
                    print("Nonterminal parentheses do not close in " + newStr)
                    exit(5)
                else:
                    buf += newStr[:nontermFinish + 1]
                    separatedStrings.append(buf)
                    buf = ""
                    newStr = newStr[nontermFinish + 1:]
            elif s == '|':
                separatedStrings.append("|")
                newStr = newStr[1:]
            elif s == '-' and newStr[1] == '>':
                separatedStrings.append("->")
                newStr = newStr[2:]
            elif s == 'ε':
                separatedStrings.append("ε")
                newStr = newStr[1:]
            elif s.isalpha():
                separatedStrings.append(s)
                newStr = newStr[1:]
            else:
                print("Got incorrect symbol during tokenization: " + s + " leftover string: " + newStr)
                exit(5)
        symbols = []
        Parser.debug_print("Received separated strings:", debug)
        Parser.debug_print("\n", debug)
        for x in separatedStrings:
            Parser.debug_print(x, debug)
        Parser.debug_print("\n", debug)
        for x in separatedStrings:
            symbols.append(Symbol(x))
        Parser.debug_print("Made Array of symbols:", debug)
        Parser.debug_print("\n", debug)
        for x in symbols:
            Parser.debug_print(x.name + " type: " + x.type + ";", debug)
        Parser.debug_print("\n", debug)
        return symbols


    def DebugPrint(self, str: str, debug: bool):
        if debug:
            print(str, end=" ")
