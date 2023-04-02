# TRS BNF (если местность любая)
# rule ::= term '=' term
# term ::= 'x' | constructor '(' termrec term ')'
# termrec ::= term ',' termrec | ε
# constructor ::= [a-z]

# TRS BNF (с местностью 1)
# rule ::= term '=' term
# term ::= 'x' | constructor '(' term ')'
# constructor ::= [a-z]

import re


class Rule:
    def __init__(self):
        self.left = None
        self.right = None


class Term:
    def __init__(self):
        self.is_x = False
        self.arg = None
        self.constructor = ''


class TRS_parser:
    def __init__(self, rules_list):
        self.rules_list = rules_list
        self.tokens = []
        self.token_index = 0
        self.parsed_rules = []

    def parse(self):
        # print('parse')
        for rule in self.rules_list:
            self.tokens = list(delete_spaces(rule))
            self.token_index = 0
            self.parsed_rules.append(self.rule())

    def rule(self):
        # print('rule')
        current_rule = Rule()

        current_rule.left = self.term()
        if self.tokens[self.token_index] == '=':
            self.token_index += 1
        else:
            raise SyntaxError('В правиле rule ожидалось найти токен "=", однако найдено "' + self.tokens[self.token_index] + '"')
        current_rule.right = self.term()

        return current_rule

    def term(self):
        # print('term')
        current_term = Term()

        if self.tokens[self.token_index] == 'x':
            current_term.is_x = True
            current_term.arg = None
            current_term.constructor = 'x'
            self.token_index += 1
        else:
            current_term.is_x = False
            current_term.constructor = self.constructor()

            if self.tokens[self.token_index] == '(':
                self.token_index += 1
            else:
                raise SyntaxError('В правиле term ожидалось найти токен "(", однако найдено "' + self.tokens[self.token_index] + '"')

            current_term.arg = self.term()

            if self.tokens[self.token_index] == ')':
                self.token_index += 1
            else:
                raise SyntaxError('В правиле term ожидалось найти токен ")", однако найдено "' + self.tokens[self.token_index] + '"')

        return current_term

    def constructor(self):
        # print('constructor')
        # print('index = ' + str(self.index))
        # print('token = ' + str(self.tokens[self.index]))
        if re.match(r"[a-z]", self.tokens[self.token_index]):
            self.token_index += 1
        else:
            raise SyntaxError('В правиле constructor ожидалось найти токен "[a-z]", однако найдено "' + self.tokens[self.token_index] + '"')
        return self.tokens[self.token_index - 1]


def delete_spaces(input_string):
    return input_string.replace(' ', '').replace('\n', '').replace('\t', '').replace('\r', '')


print('f(g(x)) = x')
print()

parser = TRS_parser(['f(g(x)) = x', 'x = x'])
parser.parse()

for rule in parser.parsed_rules:
    print('LEFT:')
    left = rule.left
    tmp = left
    id = 1
    while tmp is not None:
        print(str(id) + ': ' + tmp.constructor)
        tmp = tmp.arg
        id += 1
    print()

    print('RIGHT')
    right = rule.right
    tmp = right
    id = 1
    while tmp is not None:
        print(str(id) + ': ' + tmp.constructor)
        tmp = tmp.arg
        id += 1

    print()
    print()
