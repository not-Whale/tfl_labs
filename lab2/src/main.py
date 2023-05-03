from parser import *
from helpers import *


input_file_path = delete_spaces(input('Введите путь до файла с грамматикой...'))
CFG, RG = Parser.parse_grammars(input_file_path)
automaton = NFA.RGtoAutomaton(RG)
ChomNF = CNF(CFG)
intersection = Intersection(ChomNF, automaton)

def main():
    # CFGandRG = Parser.ParseGrammars(testInput, debug)
    # CFGrammar = CFGandRG[0]
    # regularGrammar = CFGandRG[1]
    # automaton = NFA.RGtoAutomaton(regularGrammar, debug)
    # ChomNF = CNF(CFGrammar, debug)
    # intersection = Intersection(ChomNF, automaton, debug)


def read_input_from_file(file):
    with open(file, 'r') as f:
        return f.read()


def debug_print(text):
    global debug
    if debug:
        print(text)


if __name__ == "__main__":
    main()
