from consts import *
from containers import *


class RuleBody:
    def __init__(self, left, right):
        self.left_side = left
        self.right_side = right


class Rule:
    def __init__(self, head, bodies):
        self.head = head
        self.bodies = bodies

    def __str__(self):
        rule_string = LEFT_SQUARE_BRACKET_TOKEN \
                      + self.head \
                      + RIGHT_SQUARE_BRACKET_TOKEN \
                      + FULL_ARROW_TOKEN_WITH_SPACES
        for body in self.bodies:
            rule_string += body.left_side \
                           + body.right_side[:-1] \
                           + OR_TOKEN_WITH_SPACES
        rule_string = rule_string[:-3]
        return rule_string


class Conflict:
    def __init__(self, sides):
        self.sides = sides
        self.resolved = -1
        self.done = False


class State:
    def __init__(self, index, roots):
        self.id = index
        self.roots = roots
        self.rules = []

    def __str__(self):
        state_string = '------------------------\n'

        for current_root in self.roots:
            state_string += str(current_root) + '\n'

        state_string += '++++++++++++++++++++++++\n'

        for current_rule in self.rules:
            state_string += str(current_rule) + '\n'

        state_string += '------------------------\n\n'

        return state_string


class Shift:
    def __init__(self, value, fr, to):
        self.value = value
        self.fr = fr
        self.to = to


class Follow:
    def __init__(self, head):
        self.head = head
        self.bodies = []


def parse_rules(rules_list):
    output = []
    for current_rule in rules_list:
        if current_rule[0] != LEFT_SQUARE_BRACKET_TOKEN:
            print('Синтаксическая ошибка: начальный нетерминал не найден: ', current_rule)
            exit()
        i = 1
        new_head = ''
        while i < len(current_rule) and current_rule[i] != RIGHT_SQUARE_BRACKET_TOKEN:
            new_head += current_rule[i]
            i += 1
        if i == len(current_rule):
            print('Синтаксическая ошибка: начальный нетерминал не закрыт: ', current_rule)
            exit()
        i += 1
        if current_rule[i] != MINUS_TOKEN or current_rule[i + 1] != ARROW_TOKEN:
            print('Синтаксическая ошибка: не найден разделитель в правиле: ', current_rule)
            exit()
        i += 2
        bodies = []
        new_body = ''
        while i < len(current_rule):
            if current_rule[i] == OR_TOKEN:
                bodies.append(new_body)
                new_body = ''
                if i == len(current_rule) - 1:
                    print('Синтаксическая ошибка: после знака | нет выражения: ', current_rule)
                    exit()
                i += 1
                continue
            if current_rule[i] == LEFT_SQUARE_BRACKET_TOKEN:
                while i < len(current_rule) and current_rule[i] != RIGHT_SQUARE_BRACKET_TOKEN:
                    new_body += current_rule[i]
                    i += 1
                if i == len(current_rule):
                    print('Синтаксическая ошибка: нетерминал не закрыт: ', current_rule)
                    exit()
                new_body += RIGHT_SQUARE_BRACKET_TOKEN
                i += 1
                continue
            if not current_rule[i].isalpha() \
                    and not current_rule[i].isnumeric() \
                    and current_rule[i] != LEFT_PAREN_TOKEN \
                    and current_rule[i] != RIGHT_PAREN_TOKEN \
                    and current_rule[i] != MULTIPLY_TOKEN \
                    and current_rule[i] != PLUS_TOKEN \
                    and current_rule[i] != MINUS_TOKEN:
                print('Синтаксическая ошибка: неопознанный символ: ', current_rule)
                exit()
            new_body += current_rule[i]
            i += 1
        bodies.append(new_body)
        new_bodies = []
        for body in bodies:
            new_bodies.append(RuleBody('', DOT_TOKEN + body + DOLLAR_TOKEN))
        output = append_rule_to_rules_list(output, new_head, new_bodies)
    return output


def append_rule_to_rules_list(rules_list, head, bodies):
    for current_rule in rules_list:
        if current_rule.head == head:
            for body in bodies:
                current_rule.bodies.append(body)
            return rules_list
    rules_list.append(Rule(head, bodies))
    return rules_list


def collapse_rules(rules_list):
    collapse_rules_list = []
    for current_rule in rules_list:
        collapse_rules_list = append_rule_to_rules_list(
            collapse_rules_list,
            current_rule.head,
            current_rule.bodies
        )
    return collapse_rules_list


def collapse_roots(roots):
    collapse_roots_list = []
    for current_root in roots:
        head = current_root.head
        done = False
        for current_collapse_root in collapse_roots_list:
            if current_collapse_root.head == head:
                done = True
                for current_body in current_root.bodies:
                    if not if_body_contained(current_body, current_collapse_root.bodies):
                        current_collapse_root.bodies.append(current_body)
        if not done:
            collapse_roots_list.append(Rule(head, current_root.bodies))
    return collapse_roots_list


def if_roots_same_to_states(roots_list, states_list):
    for i in range(0, len(roots_list)):
        for j in range(0, len(roots_list)):
            if str(roots_list[i]) != str(states_list[i]):
                return False
    return True


def get_rule_by_head(rules_list, head):
    for current_rule in rules_list:
        if current_rule.head == head:
            return current_rule


def build_LR(rules_list, roots_list, states_list, shifts_list, index):
    state_rules = []
    exits = []

    for current_root in roots_list:
        for current_body in current_root.bodies:
            term = ''
            if current_body.right_side[1] != DOLLAR_TOKEN:
                if current_body.right_side[1] == LEFT_SQUARE_BRACKET_TOKEN:
                    i = 2
                    while current_body.right_side[i] != RIGHT_SQUARE_BRACKET_TOKEN:
                        term += current_body.right_side[i]
                        i += 1
                else:
                    term += current_body.right_side[1]
                if not if_element_contained(term, exits):
                    exits.append(term)

    j = 0
    while j < len(rules_list):
        if if_element_contained(rules_list[j].head, exits) and not if_head_contained(rules_list[j].head, state_rules):
            state_rules.append(rules_list[j])
            reset = False
            for current_body in rules_list[j].bodies:
                term = ''
                if current_body.right_side[1] != DOLLAR_TOKEN:
                    if current_body.right_side[1] == LEFT_SQUARE_BRACKET_TOKEN:
                        i = 2
                        while current_body.right_side[i] != RIGHT_SQUARE_BRACKET_TOKEN:
                            term += current_body.right_side[i]
                            i += 1
                    else:
                        term += current_body.right_side[1]
                    if not if_element_contained(term, exits):
                        exits.append(term)
                        j = 0
                        state_rules = []
                        reset = True
                        break
            if reset:
                continue
        j += 1

    state_rules = roots_list + state_rules
    new_state = State(index, roots_list)
    index += 1
    new_state.rules = state_rules
    states_list.append(new_state)

    for current_exit in exits:
        new_roots = []
        for current_rule in state_rules:
            for current_body in current_rule.bodies:
                if current_body.right_side[1] != DOLLAR_TOKEN:
                    affected = True
                    if current_body.right_side[1] == LEFT_SQUARE_BRACKET_TOKEN:
                        i = 2
                        cur_ex = ''
                        while current_body.right_side[i] != RIGHT_SQUARE_BRACKET_TOKEN:
                            cur_ex += current_body.right_side[i]
                            i += 1
                        if current_exit != cur_ex:
                            affected = False
                    else:
                        if current_body.right_side[1] != current_exit:
                            affected = False
                    if affected:
                        if current_body.right_side[1] == LEFT_SQUARE_BRACKET_TOKEN:
                            j = 1
                            while current_body.right_side[j - 1] != RIGHT_SQUARE_BRACKET_TOKEN:
                                j += 1
                            new_roots.append(
                                Rule(
                                    current_rule.head,
                                    [
                                        RuleBody(
                                            current_body.left_side + current_body.right_side[1: j],
                                            '.' + current_body.right_side[j:]
                                        )
                                    ]
                                )
                            )
                        else:
                            new_roots.append(
                                Rule(
                                    current_rule.head,
                                    [
                                        RuleBody(
                                            current_body.left_side + current_body.right_side[1],
                                            '.' + current_body.right_side[2:]
                                        )
                                    ]
                                )
                            )

        new_to = index
        loop = False
        new_roots = collapse_rules(new_roots)

        for current_state in states_list:
            if if_roots_same_to_states(new_roots, current_state.roots):
                new_to = current_state.id
                loop = True
                break

        if not loop:
            new_roots = collapse_rules(new_roots)
            new_shift = Shift(current_exit, new_state.id, index)
            shifts_list.append(new_shift)
            states_list, shifts_list, index = build_LR(
                rules_list,
                collapse_roots(new_roots),
                states_list,
                shifts_list,
                index
            )
            continue
        else:
            new_shift = Shift(current_exit, new_state.id, new_to)
            shifts_list.append(new_shift)
            continue

    return states_list, shifts_list, index


def get_first_k(rules_list, rule, k, have1, cycle):
    first_k = []
    r_bodies = []

    for body in rule.bodies:
        r_bodies.append(RuleBody(body.left_side, body.right_side))
    rule1 = Rule(rule.head, r_bodies)

    for body in rule1.bodies:
        i = 1
        danger = 0
        n_char = ''
        have = have1
        terminal = True

        while body.right_side[i] != DOLLAR_TOKEN and i - 1 < k:
            if body.right_side[i] == LEFT_SQUARE_BRACKET_TOKEN:
                if i == 1:
                    danger = 1
                terminal = False
                i += 1

                char = ''
                while body.right_side[i] != RIGHT_SQUARE_BRACKET_TOKEN:
                    char += body.right_side[i]
                    i += 1
                i += 1

                new_rule = get_rule_by_head(rules_list, char)

                if new_rule.head == rule1.head and danger == 1:
                    danger = 2
                    cycle += 1

                if (new_rule.head != rule1.head or have <= k) and (danger != 2 or cycle <= k):
                    pref = get_first_k(rules_list, new_rule, k, have, cycle)
                    for p in pref:
                        rule1.bodies.append(RuleBody(body.left_side, '.' + n_char + p + body.right_side[i:]))
                    break
            else:
                n_char += body.right_side[i]
                have += 1
                i += 1

        if terminal:
            if not if_element_contained(n_char, first_k):
                first_k.append(n_char)

    return first_k


def append_follow(head, follows_list, out):
    for p in out:
        if p.head == head:
            for current_follow in follows_list:
                if not if_element_contained(current_follow, p.bodies):
                    p.bodies.append(current_follow)
            return out

    new_follow = Follow(head)
    new_follow.bodies = follows_list
    out.append(new_follow)
    return out


def append_follows(to_head, from_head, out, k):
    for p in out:
        if p.head == to_head:
            for p1 in out:
                if p1.head == from_head:
                    new_bodies = []
                    for b in p.bodies:
                        for b1 in p1.bodies:
                            new_body = ''
                            i = 0
                            while i < k and i < len(b):
                                new_body += b[i]
                                i += 1
                            j = 0
                            while i + j < k and j < len(b1):
                                new_body += b1[j]
                                j += 1
                            new_body += DOLLAR_TOKEN
                            if not if_element_contained(new_body, new_bodies):
                                new_bodies.append(new_body)
                    p.bodies = new_bodies
                    break
    return out


def full(out, head, k):
    for o in out:
        if o.head == head:
            for body in o.bodies:
                if len(body) < k:
                    passed = False
                    i = 0
                    while i < len(body):
                        if body[i] == DOLLAR_TOKEN:
                            passed = True
                        i += 1
                    if not passed:
                        return False
    return True


def follow_k(rules_list, k):
    out = []
    start_token_follow = Follow(START_TOKEN)
    start_token_follow.bodies.append(DOLLAR_TOKEN)
    out.append(start_token_follow)

    for _ in rules_list:
        for current_rule in rules_list:
            for body in current_rule.bodies:
                i = 1
                while body.right_side[i] != DOLLAR_TOKEN:
                    danger = 0
                    if body.right_side[i] == LEFT_SQUARE_BRACKET_TOKEN:
                        danger = i
                        new_head = ''
                        i += 1
                        while body.right_side[i] != RIGHT_SQUARE_BRACKET_TOKEN:
                            new_head += body.right_side[i]
                            i += 1
                        out = append_follow(
                            new_head,
                            get_first_k(
                                rules_list,
                                Rule(current_rule.head, [RuleBody('', body.right_side[i:])]),
                                k,
                                0,
                                0
                            ),
                            out
                        )
                        continue
                    i += 1

    for current_rule in rules_list:
        for body in current_rule.bodies:
            i = 1
            while body.right_side[i] != DOLLAR_TOKEN:
                if body.right_side[i] == LEFT_SQUARE_BRACKET_TOKEN:
                    new_head = ''
                    i += 1
                    while body.right_side[i] != RIGHT_SQUARE_BRACKET_TOKEN:
                        new_head += body.right_side[i]
                        i += 1
                    i += 1
                    if current_rule.head != new_head or not full(out, current_rule.head, k):
                        out = append_follows(new_head, current_rule.head, out, k)
                    continue
                i += 1
    return out


def filter_list(follows_list, k):
    new_follows = []

    for current_follow in follows_list:
        if current_follow.head == START_TOKEN:
            new_follows.append(current_follow)
            continue

        new_follow = Follow(current_follow.head)
        new_bodies = []

        for body in current_follow.bodies:
            i = 0
            new_body = ''
            while i < k and body[i] != DOLLAR_TOKEN:
                new_body += body[i]
                i += 1
            new_body += DOLLAR_TOKEN
            if not if_element_contained(new_body, new_bodies):
                new_bodies.append(new_body)

        new_follow.bodies = new_bodies
        new_follows.append(new_follow)

    return new_follows


def collect_roots(state):
    roots_list = []
    for current_root in state.roots:
        for current_body in current_root.bodies:
            roots_list.append(Rule(current_root.head, [current_body]))
    return roots_list


def get_conflicts(states_list):
    conflict = []
    for current_state in states_list:
        if len(current_state.roots) > 1 or len(current_state.roots[0].bodies) > 1:
            for current_root in current_state.roots:
                for current_body in current_root.bodies:
                    if current_body.right_side[1] == DOLLAR_TOKEN:
                        new_conflict = collect_roots(current_state)
                        conflict.append(Conflict(new_conflict))
    return conflict


def get_follows_bodies_by_head(follows_list, head):
    for current_follow in follows_list:
        if current_follow.head == head:
            return current_follow.bodies


def filter_strings(strings_list, max_len):
    filtered_stings_list = []
    for element in strings_list:
        current_string = ''
        i = 0
        while i < max_len and element[i] != DOLLAR_TOKEN:
            current_string += element[i]
            i += 1
        filtered_stings_list.append(current_string)
    return filtered_stings_list


def equal(f1, f2):
    for f1_element in f1:
        danger = True
        for f2_element in f2:
            if f1_element == f2_element:
                danger = False
        if danger:
            return 0

    for f2_element in f2:
        danger = True
        for f1_element in f1:
            if f2_element == f1_element:
                danger = False
        if danger:
            return 0

    return 1


def intersect(f1, f2):
    for f1_element in f1:
        for f2_element in f2:
            if f1_element == f2_element:
                return 1
    return 0


def resolve(rules_list, follows_list, conflicts_list, k):
    ok = True

    for current_conflict in conflicts_list:
        comp = []
        for current_side in current_conflict.sides:
            head = current_side.head
            for current_body in current_side.bodies:
                if current_body.right_side[1] == DOLLAR_TOKEN:
                    candidates = []
                    for f1 in get_follows_bodies_by_head(follows_list, head):
                        if not if_element_contained(f1, candidates):
                            candidates.append(f1)
                    candidates = filter_strings(candidates, k)
                    comp.append(candidates)
                else:
                    firsts = get_first_k(rules_list, current_side, k, 0, 0)
                    candidates = []
                    for f in firsts:
                        for f1 in get_follows_bodies_by_head(follows_list, head):
                            if not if_element_contained(f + f1, candidates):
                                candidates.append(f + f1)
                    candidates = filter_strings(candidates, k)
                    comp.append(candidates)

        equality = 0
        intersection = 0

        for i in range(0, len(comp)):
            for j in range(i + 1, len(comp)):
                equality += equal(comp[i], comp[j])
                intersection += intersect(comp[i], comp[j])

        if intersection == 0:
            if not current_conflict.done:
                current_conflict.resolved = k
            current_conflict.done = True
            continue
        elif equality == len(comp):
            current_conflict.resolved = k
            ok = False
            continue
        else:
            current_conflict.resolved = -1
            current_conflict.done = False
            ok = False

    return conflicts_list, ok
