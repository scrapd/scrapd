"""Define a module to manipulate dates."""
import datetime

import dateparser


def is_before(d1, d2):
    """
    Return True if d1 is strictly before d2.

    :param datetime.date d1: date 1
    :param datetime.date d2: date 2
    :return: True is d1 is before d2.
    :rtype: bool
    """
    return d1 < d2


def check_dob(dob):
    """
    In case that a date only contains 2 digits, determine century.

    :param datetime.date dob: DOB
    :return: DOB with 19xx or 20xx as appropriate
    :rtype: datetime.date
    """

    now = datetime.date.today()
    if dob.year > now.year:
        dob = datetime.date(dob.year - 100, dob.month, dob.day)
    return dob


def from_date(date):
    """
    Parse the date from a human readable format, with options for the from date.

    * If the date cannot be parsed, `datetime.date.min` is returned.
    * If the day of the month is not specified, the first day is used.

    :param str date: date
    :return: a date object representing the date.
    :rtype: datetime.date
    """

    return parse_date(date, datetime.date.min, settings={'PREFER_DAY_OF_MONTH': 'first'})


def to_date(date):
    """
    Parse the date from a human readable format, with options for the to date.

    * If the date cannot be parsed, `datetime.date.max` is returned.
    * If the day of the month is not specified, the last day is used.

    :param str date: date
    :return: a date object representing the date.
    :rtype: datetime.date
    """

    return parse_date(date, datetime.date.max, settings={'PREFER_DAY_OF_MONTH': 'last'})


def parse_date(date, default=None, settings=None):
    """
    Parse the date from a human readable format.

    If no default value is specified and there is an error, an exception is raised. Otherwise the default value is
    returned.

    :param str date: date
    :param datetime.date default: default value in case the date cannot be parsed.
    :param dict settings: a dictionary containing the parsing options. All the available options are defined here:
        https://dateparser.readthedocs.io/en/latest/dateparser.html#dateparser.conf.Settings.
    :return: a date object representing the date.
    :rtype: datetime.date
    """

    try:
        d = dateparser.parse(date, settings=settings)
        if d:
            return d.date()
        raise ValueError(f'Cannot parse date: {date}')
    except Exception:
        if default:
            return default
        raise Exception


def is_between(date, from_=None, to=None):
    """
    Check whether a date is comprised between 2 others.

    :param datetime.date date: date to check
    :param datetime.date from_: start date, defaults to None
    :param datetime.date to: end date, defaults to None
    :return: `True` if the date is between `from_` and `to`
    :rtype: bool
    """
    if not from_:
        from_ = datetime.date.min
    if not to:
        to = datetime.date.max
    return from_ <= date <= to


def compute_age(date, dob):
    """
    Compute a victim's age.

    :param datetime.date date: crash date
    :param datetime.date dob: date of birth
    :return: the victim's age.
    :rtype: int
    """
    DAYS_IN_YEAR = 365

    # Compute the age.
    return (date - dob).days // DAYS_IN_YEAR
