from trs_parser import *
from polynomial_parser import *

parser = TRSParser(['f(g(x)) = x', 'x = x'])
parser.parse()
rules = parser.parsed_rules

print()
print(function_aliases)
print(rules)
print()

for rule in parser.parsed_rules:
    print('LEFT:')
    left = rule.left
    id = 1
    for term in left:
        print(str(id) + ': ' + term.constructor)
    print()

    print('RIGHT')
    right = rule.right
    id = 1
    for term in right:
        print(str(id) + ': ' + term.constructor)

    print()
    print('---')
    print()


parser2 = PolynomialParser(['g -> 32*x^10 - x + -12*x + x^2', 'f -> x'])
parser2.parse()
p = parser2.parsed_polynomials
print(p)

print(function_aliases)
print(function_aliases['g'])
print(function_aliases['g'].expr)
print(function_aliases['f'].expr)
