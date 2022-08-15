def value_from_key(choices, key):
    for choice in choices:
        print(choice)
        if choice[0] == key:
            return choice[1]
