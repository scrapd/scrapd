"""Define the module to test `date_utils`."""
import datetime
import pytest

from scrapd.core import date_utils


@pytest.mark.parametrize('current,from_,to,expected', [
    ('Jan 10', 'Jan 1', 'Jan 31', True),
    ('Jan 1', None, None, True),
])
def test_is_in_range_00(current, from_, to, expected):
    """Ensure a date is in range."""
    assert (date_utils.from_date(from_) <= date_utils.parse_date(current) <= date_utils.to_date(to)) == expected


@pytest.mark.parametrize('date, default, settings, expected', [
    ('Jan 1 2019', None, None, datetime.datetime(2019, 1, 1, 0, 0)),
    ('Not a date', datetime.datetime.min, None, datetime.datetime(1, 1, 1, 0, 0)),
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
    (datetime.datetime(2019, 1, 10, 0, 0), datetime.datetime(2019, 1, 10, 0, 0)),
    (datetime.datetime(2054, 10, 10, 0, 0), datetime.datetime(1954, 10, 10, 0, 0)),
])
def test_check_dob_00(date, expected):
    """Ensure a DOB is valid."""
    assert date_utils.check_dob(date) == expected
