import collections
import re
from consts import *


class Rule:
    def __init__(self):
        self.left = collections.deque()
        self.right = collections.deque()

    def get_left_part(self):
        return self.left

    def get_right_part(self):
        return self.right


class Term:
    def __init__(self):
        self.constructor = ''
        self.is_x = False

    def is_x(self):
        return self.is_x

    def get_constructor_string(self):
        return self.constructor

    def __str__(self):
        return self.constructor


class TRSParser:
    def __init__(self, rules_list):
        # список оценок функций
        self.function_aliases = {}
        # список правил переписывания
        self.rules_list = rules_list
        # список токенов одного правила и текущее положение в списке
        self.tokens = []
        self.token_index = 0
        # итоговый список распаршенных правил
        self.parsed_rules = []

    def get_rules(self):
        return self.parsed_rules

    def get_function_aliases(self):
        return self.function_aliases

    def parse(self):
        # print('parse')
        for rule in self.rules_list:
            self.tokens = list(delete_spaces(rule))
            self.token_index = 0
            self.parsed_rules.append(self.rule())

    def rule(self):
        # print('rule')
        current_rule = Rule()

        current_rule.left.extend(self.term())
        if self.tokens[self.token_index] == EQUAL_TOKEN:
            self.token_index += 1
        else:
            raise SyntaxError(
                'В правиле rule ожидалось найти токен "=", однако найдено "'
                + self.tokens[self.token_index] +
                '"'
            )
        current_rule.right.extend(self.term())

        return current_rule

    def term(self):
        # print('term')
        terms_list = []
        current_term = Term()

        if self.tokens[self.token_index] == VARIABLE_TOKEN:
            current_term.is_x = True
            current_term.arg = None
            current_term.constructor = VARIABLE_TOKEN
            terms_list.append(current_term)
            self.token_index += 1
        else:
            current_term.is_x = False
            current_term.constructor = self.constructor()

            if self.function_aliases.get(current_term.constructor) is None:
                self.function_aliases[current_term.constructor] = None

            terms_list.append(current_term)

            if self.tokens[self.token_index] == LEFT_PAREN_TOKEN:
                self.token_index += 1
            else:
                raise SyntaxError(
                    'В правиле term ожидалось найти токен "(", однако найдено "' +
                    self.tokens[self.token_index] +
                    '"'
                )

            terms_list.extend(self.term())

            if self.tokens[self.token_index] == RIGHT_PAREN_TOKEN:
                self.token_index += 1
            else:
                raise SyntaxError(
                    'В правиле term ожидалось найти токен ")", однако найдено "' +
                    self.tokens[self.token_index] +
                    '"'
                )

        return terms_list

    def constructor(self):
        # print('constructor')
        if re.match(CONSTRUCTOR_TOKEN, self.tokens[self.token_index]):
            self.token_index += 1
        else:
            raise SyntaxError(
                'В правиле constructor ожидалось найти токен "[a-z]", однако найдено "' +
                self.tokens[self.token_index] +
                '"'
            )
        return self.tokens[self.token_index - 1]


def delete_spaces(input_string):
    return input_string.replace(' ', '').replace('\n', '').replace('\t', '').replace('\r', '')
