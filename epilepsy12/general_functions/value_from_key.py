def value_from_key(choices, key):
    for choice in choices:
        if choice[0] == key:
            return choice[1]
