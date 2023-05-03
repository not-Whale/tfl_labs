from consts import *


def print_states(states_list):
    for current_state in states_list:
        tmp_label = ''
        for current_rule in current_state.rules:
            tmp_label += str(current_rule) + '\n'
        print(
            str(current_state.id) +
            ' [shape = "rectangle"' +
            (' peripheries = 2' if current_state.id == 2 else '') +
            ' label = "' +
            tmp_label[:-1] + '"]'
        )


def print_conflicts(conflicts_list):
    for current_conflict in conflicts_list:
        for current_side in current_conflict.sides:
            print(str(current_side))
        print("--------------")


def print_follow(follow):
    print(follow.head)
    print(follow.bodies)


def print_SLR(states_list, shifts_list):
    print('digraph {')
    for current_state in states_list:
        label = ''
        for current_rule in current_state.rules:
            label += str(current_rule) + '\n'
        print(
            str(current_state.id) +
            ' [shape = "rectangle"' +
            (' peripheries = 2' if current_state.id == 2 else '') +
            ' label = "' + label[:-1] +
            '"]'
        )
    for current_shift in shifts_list:
        print(
            str(current_shift.fr) +
            FULL_ARROW_TOKEN_WITH_SPACES +
            str(current_shift.to) +
            ' [label = "' +
            current_shift.value +
            '"]'
        )
    print('}')
