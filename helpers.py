import re
import dal


def is_valid_html_date_param(date_str):
    """
    Using regex to validate if the input is a YYYY-MM-DD date string

    :param date_str: a date string
    :return: True if it's a YYYY-MM-DD date string, else False
    """
    return True if re.match(r'(19\d\d|20\d\d)-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])', date_str) else False


def is_valid_name(name_str):
    return True if re.match(r'\w{1,40}', name_str) else False


def is_valid_phone(phone):
    return True if re.match(r'^\+?\d{6,11}$', phone) else False


def is_valid_email(email):
    return True if re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', email) else False
