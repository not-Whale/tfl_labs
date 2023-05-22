def if_head_contained(head, heads):
    for current_head in heads:
        if current_head == head:
            return True
    return False


def if_body_contained(body, bodies):
    for current_body in bodies:
        if current_body == body:
            return True
    return False


def if_element_contained(element, elements_list):
    for current_element in elements_list:
        if element == current_element:
            return True
    return False
