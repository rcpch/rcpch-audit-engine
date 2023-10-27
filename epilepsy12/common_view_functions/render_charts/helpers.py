import re


def format_icb(label):
    if label is None:
        return "Unclassified"
    else:
        nhs_icb_string = re.search(r"(NHS\s)(.+)(\sIntegrated Care Board)", label)
        if nhs_icb_string:
            # \u002D fixes hyphen render for 'Stoke-on-trent'
            return nhs_icb_string.group(2).replace(r"\u002D", "-").title()
        return label


def format_pct_text(label):
    if label is None:
        return "No data"

    return f"{label} %"


def format_subunit_name_ticktext(color, text):
    return f"<span style='color:{str(color)};'> {str(text)} </span>"
    # return "$\color{" + str(color) + "}{" + str(text) + "}$"
