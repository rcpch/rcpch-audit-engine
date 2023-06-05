from random import randint


def validate_nhs_number(number_to_validate):
    """
    The NHS number must:
    1. be 10 digits long
    2. The 10th digit is a check digit to confirm validity using the modulus 11 method
    Excellent explainer on how to do this here: https://www.datadictionary.nhs.uk/attributes/nhs_number.html
    Excellent implementation used to check this function here: http://danielbayley.uk/nhs-number/
    """

    # convert to string and strip any spaces
    cleaned_number_as_string = str(number_to_validate).replace(" ", "")

    # check if the number is not exactly 10 digits
    if len(cleaned_number_as_string) != 10:
        return {
            "valid": False,
            "message": "The NHS Number must be exactly 10 digits long.",
        }
    else:
        # remove final digit
        checksum = int(cleaned_number_as_string[-1])
        modulus_eleven = 0
        for i in range(1, 10):
            # loop through the digits and apply multiplier which counts backwards from 11
            # then sum all the products
            multiplier = 11 - i
            # selects next digit in the number
            digit = int(cleaned_number_as_string[i - 1])
            modulus_eleven += digit * multiplier
        # divide the product by 11 and take the remainder
        remainder = modulus_eleven % 11
        # subtract remaind from 11 to get final checksum
        final_check_digit = 11 - remainder
        # if final_check_digit is 11, return 0. If 10, invalid
        if final_check_digit == 11:
            final_check_digit = 0
        elif final_check_digit == 10:
            return {
                "valid": False,
                "message": f"{number_to_validate} is an invalid NHS Number.",
            }

        if final_check_digit == checksum:
            return {"valid": True, "message": "Valid NHS number"}
        else:
            return {
                "valid": False,
                "message": f"{number_to_validate} is an invalid NHS Number.",
            }


def generate_nine_digits():
    """
    Generates a random 9 digit number and the remainder using the modulus 11 method
    """
    modulus_eleven = 0
    digit_string = ""
    for i in range(1, 10):
        # loop through the digits and apply multiplier which counts backwards from 11
        # then sum all the products
        multiplier = 11 - i
        # selects next digit in the number
        digit = randint(1, 9)  # int(f'{nine_digit_number}'[i - 1])
        modulus_eleven += digit * multiplier
        # divide the product by 11 and take the remainder
        digit_string += f"{digit}"
    remainder = modulus_eleven % 11
    return int(digit_string), remainder


def calculate_checksum(remainder):
    """
    Calculates the checksum from the remainder
    """
    # subtract remaind from 11 to get final checksum
    final_check_digit = 11 - remainder
    # if final_check_digit is 11, return 0. If 10, invalid
    if final_check_digit == 11:
        final_check_digit = 0
    elif final_check_digit == 10:
        return None

    return final_check_digit


def generate_nhs_number():
    """
    Generates a valid NHS number
    """
    final_check_digit = None

    while final_check_digit is None:
        # create a base 9 digit number, whose first digit cannot be < 1
        nine_digits, remainder = generate_nine_digits()
        # generate a checksum for that number - if None returned, number invalid, repeat
        final_check_digit = calculate_checksum(remainder)

    return int(f"{nine_digits}{final_check_digit}")


def generate_nhs_numbers(requested_number: int) -> list:
    """
    Returns a list of unique valid NHS numbers
    param: requested_number defines requested list length
    """
    number_set = set()

    while len(number_set) < requested_number:
        random_valid_nhs_number = generate_nhs_number()
        number_set.add(random_valid_nhs_number)

    return list(number_set)
