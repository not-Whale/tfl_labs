from trs_parser import *
from polynomial_parser import *
from reader import *

from numpy.polynomial import polynomial as P


def create_function_aliases_power_list(aliases):
    power_lists = {}

    for k, v in aliases.items():
        if v is not None:
            power_lists[k] = v.to_power_list()

    return power_lists


def function_compose(composition_list, function_aliases_power_lists):
    # текущая и предыдущая оценка
    previous_function = composition_list.pop().constructor
    previous_polynomial = function_aliases_power_lists[previous_function].copy()

    while len(composition_list) != 0:
        current_function = composition_list.pop().constructor
        current_polynomial = function_aliases_power_lists[current_function].copy()

        tmp_power_stack = []
        for i in range(len(current_polynomial)):
            if current_polynomial[i] != 0:
                current_power = P.polypow(previous_polynomial, i)
                current_power = list(map(lambda a: a * current_polynomial[i], current_power))
                tmp_power_stack.append(current_power)

        previous_polynomial.clear()

        for power_item in tmp_power_stack:
            for i in range(len(previous_polynomial), len(power_item)):
                previous_polynomial.append(0)

            for i in range(len(power_item)):
                previous_polynomial[i] += int(power_item[i])

    return previous_polynomial


def is_compose_positive(compose):
    i = len(compose) - 1
    while i >= 0 and compose[i] == 0:
        i -= 1

    if i >= 0 and compose[i] > 0:
        return True

    return False


def print_rule(rule):
    left_deq = rule.left
    right_deq = rule.right

    result = get_rule_side_string(left_deq)
    result += ' = '
    result += get_rule_side_string(right_deq)

    print(result)


def get_rule_side_string(rule_side):
    result = ''
    paren_counter = 0
    while len(rule_side) != 0:
        result += rule_side.popleft().constructor
        if len(rule_side) != 0:
            result += '('
            paren_counter += 1
    result += paren_counter * ')'
    return result


# читаем пути
trs_file_path = input('Введите путь до файла с TRS:')
polynomial_file_path = input('Введите путь до файла с полиномиальной оценкой:')

# парсим входные данные
if trs_file_path != '' and polynomial_file_path != '':
    reader = Reader(trs_file_path, polynomial_file_path)
else:
    reader = Reader()
reader.parse()

# парсим TRS
trs_parser = TRSParser(reader.get_trs())
trs_parser.parse()
# генерируем список правил переписывания и словарь для связи оценок и конструкторов
rules = trs_parser.get_rules()
function_aliases = trs_parser.get_function_aliases()

# парсим полиномиальные оценки
aliases_parser = AliasesParser(reader.get_polynomial(), function_aliases)
aliases_parser.parse()
function_aliases = aliases_parser.get_function_aliases()

# создаем вырожденную оценку { 'x': Monomial('1*x^1) } и добавляем в словарь
x = Monomial()
x.expr = VARIABLE_ALIAS
x.calculate_parameters()
x_p = Polynomial()
x_p.monomial_list = [x]
function_aliases[VARIABLE_TOKEN] = x_p

# переводим словарь оценок к виду, читаемому numpy
function_aliases_power_lists = create_function_aliases_power_list(function_aliases)

# проверяем систему переписывания термов на завершаемость
is_ok = True
for rule in rules:
    # выделяем левую и правую часть выражения
    left_side = rule.left.copy()
    right_side = rule.right.copy()

    # считаем композицию левой части
    left_side_compose = function_compose(left_side, function_aliases_power_lists)

    # считаем композицию правой части
    right_side_compose = function_compose(right_side, function_aliases_power_lists)

    # считаем разность оценок слева и справа
    result_compose = left_side_compose.copy()

    for i in range(len(right_side_compose)):
        if i > len(result_compose):
            result_compose.append((-1) * right_side_compose[i])
        else:
            result_compose[i] -= right_side_compose[i]

    answer = is_compose_positive(result_compose)

    if not answer:
        print('Убывание нарушается на правиле переписывания:')
        print_rule(rule)
        is_ok = False

if is_ok:
    print('TRS завершается!')
