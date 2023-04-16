def validate_nhs_number(number_to_validate):
    """
    The NHS number must:
    1. be 10 digits long
    2. The 10th digit is a check digit to confirm validity using the modulus 11 method
    Excellent explainer on how to do this here: https://www.datadictionary.nhs.uk/attributes/nhs_number.html
    Excellent implementation used to check this function here: http://danielbayley.uk/nhs-number/
    """

    # convert to string and strip any spaces
    cleaned_number_as_string = str(number_to_validate).replace(' ', '')

    # check if the number is not exactly 10 digits
    if len(cleaned_number_as_string) != 10:
        return {
            'valid': False,
            'message': 'The NHS Number must be exactly 10 digits long.'
        }
    else:
        # remove final digit
        checksum = int(cleaned_number_as_string[-1])
        modulus_eleven = 0
        for i in range(1, 10):
            # loop through the digits and apply multiplier which counts backwards from 11
            # then sum all the products
            multiplier = 11-i
            # selects next digit in the number
            digit = int(cleaned_number_as_string[i-1])
            modulus_eleven += digit * multiplier
        # divide the product by 11 and take the remainder
        remainder = modulus_eleven % 11
        # subtract remaind from 11 to get final checksum
        final_check_digit = 11-remainder
        # if final_check_digit is 11, return 0. If 10, invalid
        if final_check_digit == 11:
            final_check_digit = 0
        elif final_check_digit == 10:
            return {
                'valid': False,
                'message': f'{number_to_validate} is an invalid NHS Number.'
            }

        if final_check_digit == checksum:
            return {
                'valid': True,
                'message': 'Valid NHS number'
            }
        else:
            return {
                'valid': False,
                'message': f'{number_to_validate} is an invalid NHS Number.'
            }
