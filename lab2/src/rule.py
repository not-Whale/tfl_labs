class Rule:
    def __init__(self, left, right):
        self.leftPart = left
        if len(right) < 1:
            print("Trying to make a rule with no right part!")
            exit(3)
        else:
            self.rightPart = right

    def __init__(self, right):
        self.rightPart = right

    def __init__(self):
        self.leftPart = None
        self.rightPart = None

    def __str__(self):
        return "Rule: {" + self.leftPart.name + " -> " + " ".join([s.name for s in self.rightPart]) + "]}"

    @staticmethod
    def isToEmpty(r):
        return ((len(r.rightPart) == 1) and (r.rightPart[0].type == "empty"))

    @staticmethod
    def isToTerm(r):
        return ((len(r.rightPart) == 1) and (r.rightPart[0].type == "term"))

    @staticmethod
    def isToTermNterm(r):
        return ((len(r.rightPart) == 2) and (r.rightPart[0].type == "term") and (r.rightPart[1].type == "nonterm"))

    @staticmethod
    def isToNtermNterm(r):
        return ((len(r.rightPart) == 2) and (r.rightPart[0].type == "nonterm") and (r.rightPart[1].type == "nonterm"))

    @staticmethod
    def hasTermAndNotToTerm(r):
        return ((len(r.rightPart) > 1) and any(rp.type == "term" for rp in r.rightPart))

    @staticmethod
    def isToNterms(r):
        return ((len(r.rightPart) > 1) and all(s.type == "nonterm" for s in r.rightPart))

    @staticmethod
    def getTerminalNames(r):
        names = []
        for s in r.rightPart:
            if ((s.type == "term") and (s.name not in names)):
                names.append(s.name)
        return names

    @staticmethod
    def DebugPrint(str, debug):
        if debug:
            print(str)
