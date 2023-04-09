import functools
from consts import *
from trs_parser import delete_spaces, CONSTRUCTOR_TOKEN
import re


class Polynomial:
    def __init__(self):
        self.monomial_list = []
        self.func = 0

    def get_function(self):
        return self.func

    def to_power_list(self):
        monomial_list = self.monomial_list[::-1]
        last_power = monomial_list[len(monomial_list) - 1].power
        power_list = [0 for _ in range(last_power + 1)]

        for monomial in monomial_list:
            power_list[monomial.power] = monomial.k

        return power_list

    def __str__(self):
        res = '['
        for mono in self.monomial_list:
            res += str(mono)
            res += ', '
        res += ']'
        return res


class Monomial:
    def __init__(self):
        self.expr = ''
        self.k = 0
        self.power = 0

    def calculate_parameters(self):
        self.expr = delete_double_signs(self.expr)

        if MULTIPLY_TOKEN in self.expr:
            self.k = int(self.expr.split(MULTIPLY_TOKEN)[0])
        elif MINUS_TOKEN in self.expr:
            self.k = -1
        else:
            self.k = 1

        if POWER_TOKEN in self.expr:
            self.power = int(self.expr.split(POWER_TOKEN)[1])

    def __str__(self):
        return str(self.k) + '*x^' + str(self.power)


class AliasesParser:
    def __init__(self, polynomials_list, function_aliases):
        # список правил переписывания
        self.polynomials_list = polynomials_list
        # список оценок функций
        self.function_aliases = function_aliases
        # список токенов одного правила и текущее положение в списке
        self.tokens = []
        self.token_index = 0
        # итоговый список распаршенных оценок
        self.parsed_polynomials = []

    def get_polynomials(self):
        # [Monomial()]
        return self.parsed_polynomials

    def get_function_aliases(self):
        # {string: [Monomial()]}
        return self.function_aliases

    def parse(self):
        # print('parse')
        for polynomial in self.polynomials_list:
            self.tokens = list(delete_spaces(polynomial))
            self.token_index = 0
            self.parsed_polynomials.append(self.interpretation())

    def interpretation(self):
        # print('interpretation')
        current_polynomial = Polynomial()
        polynomial_constructor = self.constructor()

        if self.tokens[self.token_index] == '-':
            self.token_index += 1
            if self.tokens[self.token_index] == '>':
                self.token_index += 1
            else:
                raise SyntaxError(
                    'В правиле interpretation ожидалось найти токен ">", однако найдено' +
                    self.tokens[self.token_index] +
                    '"'
                )
        else:
            raise SyntaxError(
                'В правиле interpretation ожидалось найти токен "-", однако найдено' +
                self.tokens[self.token_index] +
                '"'
            )

        monomial_list = self.polynomial()
        monomial_list.sort(key=functools.cmp_to_key(compare_monomials))
        monomial_list = calculate_reps(monomial_list)

        current_polynomial.monomial_list = monomial_list
        self.function_aliases[polynomial_constructor] = current_polynomial

        # [Monomial()]
        return monomial_list

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

    def polynomial(self):
        # print('polynomial')
        monomial_list = [self.monomial()]
        monomial_list[0].calculate_parameters()

        if self.token_index < len(self.tokens) and \
                (self.tokens[self.token_index] == PLUS_TOKEN or self.tokens[self.token_index] == MINUS_TOKEN):
            # запомнили знак между мономами
            sign_token = self.tokens[self.token_index]
            self.token_index += 1
            # взяли список следующих мономов
            next_monomial_list = self.polynomial()
            # к первому из мономов добавили в начало знак между мономами
            next_monomial_list[0].expr = sign_token + next_monomial_list[0].expr
            # пересчитали параметры
            next_monomial_list[0].calculate_parameters()
            # закинули мономы в общий список
            monomial_list.extend(next_monomial_list)

        # [Monomial()]
        return monomial_list

    def monomial(self):
        # print('monomial')
        current_monomial = Monomial()

        if self.token_index < len(self.tokens) and self.tokens[self.token_index] == MINUS_TOKEN:
            current_monomial.expr += MINUS_TOKEN
            self.token_index += 1
            current_monomial.expr += self.monomial().expr
        elif self.is_number_token():
            current_monomial.expr += self.number()
            if self.token_index < len(self.tokens) and self.tokens[self.token_index] == MULTIPLY_TOKEN:
                current_monomial.expr += MULTIPLY_TOKEN
                self.token_index += 1
                current_monomial.expr += self.monomial().expr
            else:
                raise SyntaxError(
                    'В правиле monomial ожидалось найти токен "*", однако найдено "' +
                    self.tokens[self.token_index] +
                    '"'
                )
        elif self.token_index < len(self.tokens) and self.tokens[self.token_index] == VARIABLE_TOKEN:
            current_monomial.expr += VARIABLE_TOKEN
            self.token_index += 1
            if self.token_index < len(self.tokens) and self.tokens[self.token_index] == POWER_TOKEN:
                current_monomial.expr += POWER_TOKEN
                self.token_index += 1
                current_monomial.expr += self.number()
            else:
                current_monomial.expr += '^1'
        else:
            raise SyntaxError(
                'В правиле monomial ожидалось найти токен "-" или "[1-9][0-9]*" или "x", однако найдено "' +
                self.tokens[self.token_index] +
                '"'
            )

        current_monomial.calculate_parameters()
        # Monomial()
        return current_monomial

    def is_number_token(self):
        return re.match(NUMBER_TOKEN, self.tokens[self.token_index])

    def number(self):
        # print('number')
        current_number = ''

        if re.match(NUMBER_TOKEN, self.tokens[self.token_index]):
            current_number += self.tokens[self.token_index]
            self.token_index += 1

            while self.token_index < len(self.tokens) and re.match(DIGIT_TOKEN, self.tokens[self.token_index]):
                current_number += self.tokens[self.token_index]
                self.token_index += 1

        else:
            raise SyntaxError(
                'В правиле number ожидалось найти токен "[1-9][0-9]*", однако найдено "' +
                self.tokens[self.token_index] +
                '"'
            )

        # string
        return current_number


def calculate_reps(polynomial):
    i = 0
    while i < len(polynomial):
        j = i + 1
        stop = len(polynomial)
        while j < stop:
            if polynomial[i].power == polynomial[j].power:
                polynomial[i].k += polynomial[j].k
                if polynomial[i].k != 0:
                    polynomial[i].expr = str(polynomial[i].k) + '*x' + str(polynomial[i].power)
                else:
                    polynomial.pop(i)
                    stop -= 1
                polynomial.pop(j)
                stop -= 1
            else:
                break
            j += 1
        i += 1

    return polynomial


def delete_double_signs(input_string):
    return input_string.replace('+-', '-')


def compare_monomials(m1, m2):
    return int(m2.power) - int(m1.power)
