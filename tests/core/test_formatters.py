"""Test the formatter module."""
from datetime import date
import pytest

from scrapd.core.formatter import Formatter, CountFormatter
from scrapd.core.formatter import PythonFormatter, CSVFormatter, JSONFormatter

class TestFormatter:
    """Test the default formatter."""

    def test_formatter_00(self):
        """Ensure a formatter is retrieved."""
        f = Formatter()
        assert f._get_formatter()

    def test_formatter_count(self, capsys):
        from sys import stdout
        f = CountFormatter(output=stdout)
        f.printer(RESULTS)
        out, _ = capsys.readouterr()
        assert out.strip() == "1"

    def test_formatter_csv(self, capsys):
        """Ensure some correct text is in the output."""
        from sys import stdout
        f = CSVFormatter(output=stdout)
        f.printer(RESULTS)
        out, _ = capsys.readouterr()
        assert "2005-12-05" in out

    def test_formatter_json(self, capsys):
        """Ensure some correct text is in the output."""
        from sys import stdout
        f = JSONFormatter(output=stdout)
        f.printer(RESULTS)
        out, _ = capsys.readouterr()
        assert "Black" in out

    def test_formatter_json_bad_type(self):
        """Ensure some correct text is in the output."""
        from sys import stdout
        f = JSONFormatter(output=stdout)
        with pytest.raises(TypeError):
            f.printer(RESULTS_BAD_TYPE)

RESULTS = [
    {
        'Age': 13,
        'Case': '19-0400694',
        'DOB': date(2005, 12, 5),
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

RESULTS_BAD_TYPE = [
    {
        'Age': 13,
        'Case': set(),
        'DOB': '12/05/05',
    },
]
