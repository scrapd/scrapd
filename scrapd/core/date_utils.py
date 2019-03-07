"""Define a module to manipulate dates."""
import datetime

import dateparser


def is_posterior(d1, d2):
    """
    Return True is d1 is posterior to d2 (i.e. it happened after).

    :param str d1: date 1
    :param str d2: date 2
    :return: True is d1 is posterior to d2
    :rtype: bool
    """

    return parse_date(d1) < parse_date(d2)


def clean_date_string(date):
    """
    Parse the date from an unspecified format to the specified format.

    :param str date:
    :return: a date string in the uniform %m/%d/%Y format.
    :rtype: str
    """
    dt = parse_date(date)
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
            # In case that a date only contains 2 digits, we have to determine whether it should be
            # 19xx or 20xx.
            now = datetime.datetime.now()
            if d.year > now.year:
                d = datetime.datetime(d.year - 100, d.month, d.day)
            return d
        raise ValueError(f'Cannot parse date: {date}')
    except Exception:
        if default:
            return default
        raise Exception


def is_in_range(date, from_=None, to=None):
    """
    Check whether a date is comprised between 2 others.

    :param str date: date to vheck
    :param str from_: start date, defaults to None
    :param str to: end date, defaults to None
    :return: `True` if the date is between `from_` and `to`
    :rtype: bool
    """
    current_date = parse_date(date)
    from_date_ = from_date(from_)
    to_date_ = to_date(to)

    return from_date_ <= current_date <= to_date_


def compute_age(date, dob):
    """
    Compute a victim's age.

    :param str date: crash date
    :param str dob: date of birth
    :return: the victim's age.
    :rtype: int
    """
    DAYS_IN_YEAR = 365
    dob_ = parse_date(dob)

    # Compute the age.
    return (parse_date(date) - dob_).days // DAYS_IN_YEAR
