"""Define the module to test `date_utils`."""
import datetime
import pytest

from scrapd.core import date_utils


@pytest.mark.parametrize('current,from_,to,expected', [
    ('Jan 10', 'Jan 1', 'Jan 31', True),
    ('Jan 1', None, None, True),
])
def test_is_between_00(current, from_, to, expected):
    """Ensure a date is in range."""
    assert date_utils.is_between(current, from_, to) == expected


@pytest.mark.parametrize('date, default, settings, expected', [
    ('Jan 1 2019', None, None, datetime.date(2019, 1, 1)),
    ('Not a date', datetime.date.min, None, datetime.date(1, 1, 1)),
])
def test_parse_date_00(date, default, settings, expected):
    """Ensure a parsed date returns a value."""
    assert date_utils.parse_date(date, default=default, settings=settings) == expected


def test_parse_date_01():
    """Ensure an invalid date with no default raises an exception."""
    with pytest.raises(Exception):
        date_utils.parse_date('Not a date')


@pytest.mark.parametrize('date, dob, expected', [
    ('Jan 10 2019', False, '01/10/2019'),
    ('2019-01-10', False, '01/10/2019'),
    ('10-10-54', True, '10/10/1954'),
])
def test_clean_date_string_00(date, dob, expected):
    """Ensure date string is properly formatted."""
    assert date_utils.clean_date_string(date, dob) == expected


@pytest.mark.parametrize('date, expected', [
    (datetime.date(2019, 1, 10), datetime.date(2019, 1, 10)),
    (datetime.date(2054, 10, 10), datetime.date(1954, 10, 10)),
])
def test_check_dob_00(date, expected):
    """Ensure a DOB is valid."""
    assert date_utils.check_dob(date) == expected


@pytest.mark.parametrize('d1, d2, expected', [
    ('Jan 01 2019', 'Jan 02 2019', True),
    ('Jan 02 2019', 'Jan 01 2019', False),
    ('Jan 01 2019', 'Jan 01 2019', False),
])
def test_is_before(d1, d2, expected):
    """Ensure a d1 is before d2."""
    assert date_utils.is_before(d1, d2) == expected
