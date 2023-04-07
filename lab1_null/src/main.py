from trs_parser import *
from polynomial_parser import *

trs_parser = TRSParser(['f(g(x)) = x', 'h(x) = x'])
trs_parser.parse()
rules = trs_parser.get_rules()
function_aliases = trs_parser.get_function_aliases()

print()
print(function_aliases)
print()

for rule in rules:
    print('LEFT:')
    id = 1
    for term in rule.left:
        print(str(id) + ': ' + str(term))
        id += 1
    print()

    print('RIGHT')
    id = 1
    for term in rule.right:
        print(str(id) + ': ' + str(term))
        id += 1

    print()
    print('---')
    print()


aliases_parser = AliasesParser(['g -> 32*x^10 - x + -12*x + x^2', 'f -> x'], function_aliases)
aliases_parser.parse()
function_aliases = aliases_parser.get_function_aliases()
p = aliases_parser.get_polynomials()

print()
for poly in p:
    print('[')
    for mono in poly:
        print(mono)
    print(']')

print()
# print(p)

x = Monomial()
x.expr = '1*x^1'
x.calculate_parameters()
x_p = Polynomial()
x_p.monomial_list = [x]
function_aliases['x'] = x_p

for k, v in function_aliases.items():
    print(k + ': ' + str(v))
