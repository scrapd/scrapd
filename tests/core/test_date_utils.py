"""Define the module to test `date_utils`."""
import datetime
import pytest

from scrapd.core import date_utils
from scrapd.core import regex


@pytest.mark.parametrize('current,from_,to,expected', [
    (datetime.date(2019, 1, 10), datetime.date(2019, 1, 1), datetime.date(2019, 1, 31), True),
    (datetime.date(2019, 1, 1), datetime.date.min, datetime.date.max, True),
    (datetime.date(2019, 1, 1), None, None, True),
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


@pytest.mark.parametrize('input_,expected', (
    ('Time: </span>   Approximately 01:14a.m.', datetime.time(1, 14)),
    ('<tag>Time:     08:35 pm<br />', datetime.time(20, 35)),
    ('Time:  8:47  P.M.', datetime.time(20, 47)),
    ('Time:12:47 p.M.', datetime.time(12, 47)),
    ('Time: 5:16', datetime.time(5, 16)),
    ('Time: 05:16 ', datetime.time(5, 16)),
    ('Time: 18:26', datetime.time(18, 26)),
    ('Time: 22:56', datetime.time(22, 56)),
    ('Time: 54:34', None),
    ('Time: 28:24', None),
    ('Time: 4:66 pm', None),
    ('Time: 18:46 pm', datetime.time(18, 46)),
    ('Time: 00:24 a.m.', datetime.time(0, 24)),
    ('<p>	<strong>Time:</strong>       8 p.m.</p>', datetime.time(20, 0)),
))
def test_parse_time_field_00(input_, expected):
    """Ensure a time field gets parsed correctly."""
    time_str = regex.match_time_field(input_)
    actual = date_utils.parse_time(time_str)
    assert actual == expected


@pytest.mark.parametrize('input_,expected', (
    ('<strong>Date:   </strong>April 18, 2019</p>', datetime.date(2019, 4, 18)),
    ('>Date:   </strong> Night of May 22 2019</p>', datetime.date(2019, 5, 22)),
    ('>Date:</span></strong>   Wednesday, Oct. 3, 2018</p>', datetime.date(2018, 10, 3)),
    ('>Date:  night Apr 1-2012</p>', datetime.date(2012, 4, 1)),
    ('>Date:  feb. 2 2018</p>', datetime.date(2018, 2, 2)),
    ('>Date:  10-1-17</p>', datetime.date(2017, 10, 1)),
    ('>Date:  Morning of 2,2,19 </p>', datetime.date(2019, 2, 2)),
    ('>Date:  3/3/19</p>', datetime.date(2019, 3, 3)),
    ('', None),
    ('>Date: Afternoon</p>', None),
))
def test_parse_date_field_00(input_, expected):
    """Ensure a date field gets parsed correctly."""
    actual = regex.match_date_field(input_)
    assert actual == expected
