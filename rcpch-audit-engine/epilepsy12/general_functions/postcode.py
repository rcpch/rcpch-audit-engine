import re

def valid_postcode(pc)->bool:
    """
    Validation method for UK postcodes
    ACKNOWLEDGEMENT: with thanks to https://kodey.co.uk/2020/09/03/a-uk-postcode-validation-script-in-python/
    """
    pattern = 'not matched'
    #e.g. W27XX
    if len(pc.replace(" ", "")) == 5:
        pattern = re.compile("^[a-zA-Z]{1}[0-9]{2}[a-zA-Z]{2}")
    #e.g. TW27XX
    elif len(pc.replace(" ", "")) == 6:
        pattern = re.compile("^[a-zA-Z]{2}[0-9]{2}[a-zA-Z]{2}")
    #e.g. TW218FF
    elif len(pc.replace(" ", "")) == 7:
        pattern = re.compile("^[a-zA-Z]{2}[0-9]{3}[a-zA-Z]{2}")

    # if pattern != 'not matched':
    #     if pattern.match(pc):
    #         return False
    # else:
    #     return True

    return pattern

def validate_postcode(postcode:str)->bool:
    if(postcode.match('not matched')):
        return False
    else: 
        return True