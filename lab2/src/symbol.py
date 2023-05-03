class Symbol:
    def __init__(self, name, type=None):
        self.name = name
        if len(name) < 1:
            print("Trying to make symbol out of empty string!")
            exit(2)
        if len(name) == 1:
            if name.islower():
                self.type = "term"
            elif name == "ε":
                self.type = "empty"
            elif name == "|":
                self.type = "alternative"
            else:
                print("Found 1-letter symbol which is not term, alternative or empty: " + name)
                exit(2)
        else:
            if name.startswith("[") and name.endswith("]") and name[1:-1].isalpha():
                self.type = "nonterm"
            elif name == "->":
                self.type = "arrow"
            else:
                print("Found >1-letter symbol which is not nonterm or arrow: " + name)
                exit(2)

    def __str__(self):
        return self.name