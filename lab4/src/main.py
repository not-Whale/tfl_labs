from helpers import *
from parse_and_analyze import *
from printers import *


log = []
rules = []
shifts = []
states = []

# читаем правила грамматики
print('Введите правила грамматики...')
print('\033[33mДля окончания чтения правил подайте на вход пустую строку!\033[0m')
while True:
    input_rule_string = input()
    if input_rule_string == '':
        break
    rules.append(delete_spaces(input_rule_string))

print('Введите число N...')
n = int(input('N = '))

# парсим правила
rules = parse_rules(rules)

# строим и выводим SLR-автомат
states, shifts, _ = build_LR(rules, [Rule(NULL_TOKEN, [RuleBody('', '.[S]$')])], states, shifts, 1)
print_SLR(states, shifts)

# ищем и выводим конфликты, если они есть
conflicts = get_conflicts(states)

for i in range(1, 1 + n):
    follows = filter_list(follow_k(rules, i), i)
    conflicts, ok = resolve(rules, follows, conflicts, i)
    if ok:
        break
happy = 0

for conflict in conflicts:
    print("Конфликт между")
    for side in conflict.sides:
        print(str(side))
    if conflict.done:
        print("разрешился при k =", conflict.resolved)
        happy += 1
    elif conflict.resolved != -1:
        print("в подвешенном состоянии при k =", conflict.resolved)
    else:
        print("не был разрешён при k =", int(n))
if len(conflicts) == happy:
    print("Конфликтов нет (или все были разрешены)")
