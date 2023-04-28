def match_in_choice_key(choice, match):
    for k, v in choice:
        if k == match:
            return True
    return False
