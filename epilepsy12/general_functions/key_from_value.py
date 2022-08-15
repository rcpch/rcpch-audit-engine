def key_from_value(choices, value):
    val = dict((v, k) for k, v in choices).get(value)
    return val
