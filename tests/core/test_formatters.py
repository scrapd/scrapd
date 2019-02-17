"""Test the formatter module."""
from scrapd.core.formatter import Formatter


class TestFormatter:
    """Test the default formatter."""

    def test_formatter_00(self):
        """Ensure a formatter is retrieved."""
        f = Formatter()
        assert f._get_formatter()


RESULTS = [
    {
        'Age': 13,
        'Case': '19-0400694',
        'DOB': '12/05/05',
        'Date': 'February 9, 2019',
        'Ethnicity': 'Black',
        'Fatal crashes this year': '7',
        'First Name': 'Zion',
        'Gender': 'male',
        'Last Name': 'Mouton',
        'Link': 'http://austintexas.gov/news/traffic-fatality-7-4',
        'Location': '6000 block of Springdale Road',
        'Time': '12:48 p.m.'
    },
]
