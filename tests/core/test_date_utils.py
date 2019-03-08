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
    assert date_utils.is_in_range(current, from_, to) == expected


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


@pytest.mark.parametrize('date, expected', [
    ('Jan 10 2019', '01/10/2019'),
    ('2019-01-10', '01/10/2019'),
])
def test_clean_date_string_00(date, expected):
    """Ensure date string is properly formatted."""
    assert date_utils.clean_date_string(date) == expected
