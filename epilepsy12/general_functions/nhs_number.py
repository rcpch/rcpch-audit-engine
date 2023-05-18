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

    # guard clause - return invalid if the number is not exactly 10 digits
    if len(cleaned_number_as_string) != 10:
        return {
            'valid': False,
            'message': 'The NHS Number must be exactly 10 digits long.'
        }
        
    # turn nhs number into list of ints
    nhs_nums = [int(digit) for digit in cleaned_number_as_string]
    
    # sum the first 9 digits using the weighted multiplication rule
    first_nine_digits_weighted_sum = 0
    for i, digit in enumerate(nhs_nums[:-1]):
        first_nine_digits_weighted_sum += digit * (10-i)
    
    # calculate the check_sum_val using mod 11 rule -> result ranges betwee 0-11
    check_sum_val = 11 - (first_nine_digits_weighted_sum % 11)
    
    # "If the result is 11 then a check digit of 0 is used."
    if check_sum_val == 11:
        check_sum_val = 0
    
    # nhs number valid only if check_sum_val == last digit. NOTE: they also specify an additional check to see whether check_sum_val == 10, which is invalid. However, directly checking whether check_sum_val == last digit inherently confirms check_sum_val is NOT 10.
    if check_sum_val == nhs_nums[-1]:
        return {
            'valid': True,
            'message': 'Valid NHS number'
        }
    else:
        return {
            'valid': False,
            'message': f'{number_to_validate} is an invalid NHS Number.'
        }
    
