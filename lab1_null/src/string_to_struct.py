from polynomial_parser import delete_double_signs


class Monomial:
    def __init__(self, expr):
        self.expr = expr
        self.k = 0
        self.power = 0
        self.sign = True

    def __str__(self):
        if self.sign:
            return str(self.k) + '*x^' + str(self.power)
        else:
            return '-' + str(self.k) + '*x^' + str(self.power)


class PolynomialStringParser:
    def __init__(self, expr_list):
        self.expr_list = expr_list
        self.current_expr = None
        self.polynomial_list = []

    def parse(self):
        for expr in self.expr_list:
            self.current_expr = expr
            self.parse_expr()

    def parse_expr(self):
        polynomial = []
        for mono in self.current_expr:
            current_mono = Monomial(mono)
            if '*' in mono:
                current_mono.k = int(delete_double_signs(mono.split('*')[0]))
            elif '-' in mono:
                current_mono.k = -1
            else:
                current_mono.k = 1
            current_mono.power = int(mono.split('^')[1])
            polynomial.append(current_mono)
        self.polynomial_list.append(calculate_reps(polynomial))


def calculate_reps(polynomial):
    for i in range(len(polynomial)):
        for j in range(i + 1, len(polynomial)):
            if polynomial[i].power == polynomial[j].power:
                polynomial[i].k += polynomial[j].k
                polynomial.pop(j)
            else:
                break
    return polynomial
