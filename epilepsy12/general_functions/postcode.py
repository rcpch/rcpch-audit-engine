import re


def valid_postcode(postcode) -> bool:
    """
    Validation function for UK postcodes
    Returns either a regexp match or 'not matched'
    ACKNOWLEDGEMENT: with thanks to https://kodey.co.uk/2020/09/03/a-uk-postcode-validation-script-in-python/
    """
    pattern = 'not matched'
    #e.g. W27XX
    if len(postcode.replace(" ", "")) == 5:
        pattern = re.compile("^[a-zA-Z]{1}[0-9]{2}[a-zA-Z]{2}")
    #e.g. TW27XX
    elif len(postcode.replace(" ", "")) == 6:
        pattern = re.compile("^[a-zA-Z]{2}[0-9]{2}[a-zA-Z]{2}")
    #e.g. TW218FF
    elif len(postcode.replace(" ", "")) == 7:
        pattern = re.compile("^[a-zA-Z]{2}[0-9]{3}[a-zA-Z]{2}")

    return pattern


def validate_postcode(postcode: str) -> bool:
    valid_postcode_regex = valid_postcode(postcode=postcode)
    if(valid_postcode_regex.match('not matched')):
        return False
    else:
        return True
