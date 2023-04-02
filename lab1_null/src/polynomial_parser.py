from trs_parser import delete_spaces, function_aliases, CONSTRUCTOR_TOKEN
import re


class Polynomial:
    def __init__(self):
        self.expr = ''
        self.func = 0


class PolynomialParser:
    def __init__(self, polynomials_list):
        self.polynomials_list = polynomials_list
        self.tokens = []
        self.token_index = 0
        self.parsed_polynomials = []

    def parse(self):
        print('parse')
        for polynomial in self.polynomials_list:
            self.tokens = list(delete_spaces(polynomial))
            self.token_index = 0
            self.parsed_polynomials.append(self.interpretation())

    def interpretation(self):
        print('interpr')
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

        current_polynomial.expr = self.polynomial()
        function_aliases[polynomial_constructor] = current_polynomial

        return current_polynomial

    def constructor(self):
        print('const')
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
        print('poly')
        monomial_list = [self.monomial()]

        if self.tokens[self.token_index] == '+' or self.tokens[self.token_index] == '-':
            tmp_token = self.tokens[self.token_index]
            self.token_index += 1
            next_monomial_list = self.polynomial()
            next_monomial_list[0] = tmp_token + next_monomial_list[0]
            monomial_list.extend(next_monomial_list)

        return monomial_list

    def monomial(self):
        print('mono')
        current_monomial = ''

        if self.tokens[self.token_index] == '-':
            current_monomial += '-'
            self.token_index += 1
        elif self.is_number_token():
            current_monomial += self.number()
            if self.tokens[self.token_index] == '*':
                current_monomial += '*'
                self.token_index += 1
                if self.tokens[self.token_index] == 'x':
                    current_monomial += 'x'
                    self.token_index += 1
                    if self.tokens[self.token_index] == '^':
                        current_monomial += '^'
                        self.token_index += 1
                        current_monomial += self.number()
                else:
                    raise SyntaxError(
                        'В правиле monomial ожидалось найти токен "x", однако найдено "' +
                        self.tokens[self.token_index] +
                        '"'
                    )
            else:
                raise SyntaxError(
                    'В правиле monomial ожидалось найти токен "*", однако найдено "' +
                    self.tokens[self.token_index] +
                    '"'
                )
        elif self.tokens[self.token_index] == 'x':
            current_monomial += 'x'
            self.token_index += 1
            if self.tokens[self.token_index] == '^':
                current_monomial += '^'
                self.token_index += 1
                current_monomial += self.number()
        else:
            raise SyntaxError(
                'В правиле monomial ожидалось найти токен "-" или "[1-9][0-9]*" или "x", однако найдено "' +
                self.tokens[self.token_index] +
                '"'
            )

        return current_monomial

    def is_number_token(self):
        return re.match(r"[1-9]", self.tokens[self.token_index])

    def number(self):
        print('number')
        current_number = ''

        if re.match(r"[1-9]", self.tokens[self.token_index]):
            current_number += self.tokens[self.token_index]
            self.token_index += 1

            while re.match(r"[0-9]", self.tokens[self.token_index]):
                current_number += self.tokens[self.token_index]
                self.token_index += 1

        else:
            raise SyntaxError(
                'В правиле number ожидалось найти токен "[1-9]" или "[1-9][0-9]*" или "x", однако найдено "' +
                self.tokens[self.token_index] +
                '"'
            )

        return current_number
