import re
from rapidfuzz import fuzz, process


def scan_for_keywords(phrase: str, match_list) -> list:
    """
    Returns a list of keywords stored in the database against a string entered by the user.
    The list of keywords is exhaustive, but cannot cover the different grammatical permutations required for 
    an exact match. For this reason, the RapidFuzz library is used which leverages the Levenshtein distance
    concept, and returns a probability that the words match.
    """
    # init
    keywords_string = ""

    # prepare the keywords as regex findall string
    for index, keyword in enumerate(match_list):
        keywords_string += f"{keyword.keyword}|"
    # identify exact matches and remove the empty strings
    filtered_words = list(
        filter(None, re.findall(keywords_string, phrase.lower())))

    return_vals = []
    for word in filtered_words:
        return_vals.append(
            next(item for item in match_list if item.keyword == word))
    print(return_vals)
    return return_vals


def fuzzy_scan_for_keywords(phrase: str, match_list) -> list:

    # iterate through the keywords looking for a fuzzy match
    keywords = []
    for index, keyword in enumerate(match_list):
        match = fuzz.partial_ratio(keyword.keyword, phrase)
        if match >= 90:
            keywords.append(keyword)
    return keywords
