"""Define a module to manipulate dates."""
import datetime

import dateparser


def check_dob(dob):
    """
    In case that a date only contains 2 digits, determine century.

    :param datetime.datetime dob: DOB
    :return: DOB with 19xx or 20xx as appropriate
    :rtype: datetime.datetime
    """

    now = datetime.datetime.now()
    if dob.year > now.year:
        dob = datetime.datetime(dob.year - 100, dob.month, dob.day)
    return dob


def clean_date_string(date, is_dob=False):
    """
    Parse the date from an unspecified format to the specified format.

    :param str date: date
    :param boolean is_dob: True if date is DOB, otherwise False
    :return: a date string in the uniform %m/%d/%Y format.
    :rtype: str
    """
    dt = parse_date(date)
    if is_dob:
        dt = check_dob(dt)
    return datetime.datetime.strftime(dt, "%m/%d/%Y")


def from_date(date):
    """
    Parse the date from a human readable format, with options for the from date.

    * If the date cannot be parsed, `datetime.datetime.min` is returned.
    * If the day of the month is not specified, the first day is used.

    :param str date: date
    :return: a date object representing the date.
    :rtype: datetime.datetime
    """

    return parse_date(date, datetime.datetime.min, settings={'PREFER_DAY_OF_MONTH': 'first'})


def to_date(date):
    """
    Parse the date from a human readable format, with options for the to date.

    * If the date cannot be parsed, `datetime.datetime.max` is returned.
    * If the day of the month is not specified, the last day is used.

    :param str date: date
    :return: a date object representing the date.
    :rtype: datetime.datetime
    """

    return parse_date(date, datetime.datetime.max, settings={'PREFER_DAY_OF_MONTH': 'last'})


def parse_date(date, default=None, settings=None):
    """
    Parse the date from a human readable format.

    If no default value is specified and there is an error, an exception is raised. Otherwise the default value is
    returned.

    :param str date: date
    :param datetime default: default value in case the date cannot be parsed.
    :param dict settings: a dictionary containing the parsing options. All the available options are defined here:
        https://dateparser.readthedocs.io/en/latest/dateparser.html#dateparser.conf.Settings.
    :return: a date object representing the date.
    :rtype: datetime.datetime
    """

    try:
        d = dateparser.parse(date, settings=settings)
        if d:
            return d
        raise ValueError(f'Cannot parse date: {date}')
    except Exception:
        if default:
            return default
        raise Exception


def compute_age(date, dob):
    """
    Compute a victim's age.

    :param datetime.datetime date: crash date
    :param datetime.datetime dob: date of birth
    :return: the victim's age.
    :rtype: int
    """
    DAYS_IN_YEAR = 365

    # Compute the age.
    return (date - dob).days // DAYS_IN_YEAR
