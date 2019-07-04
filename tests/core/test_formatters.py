"""Test the formatter module."""
import datetime
import sys

import pytest

from scrapd.core.formatter import (
    CountFormatter,
    CSVFormatter,
    Formatter,
    JSONFormatter,
    PythonFormatter,
)


class TestFormatter:
    """Test the default formatter."""

    def test_formatter_00(self):
        """Ensure a formatter is retrieved."""
        f = Formatter()
        assert f._get_formatter()

    def test_formatter_count(self, capsys):
        """Ensure Count formatter returns a number."""
        f = CountFormatter(output=sys.stdout)
        f.printer(RESULTS)
        out, _ = capsys.readouterr()
        output = out.strip()
        assert output == "1"
        assert int(output)

    def test_formatter_csv(self, capsys):
        """Ensure some correct text is in the output."""
        f = CSVFormatter(output=sys.stdout)
        f.printer(RESULTS)
        out, _ = capsys.readouterr()
        assert "12/05/2005" in out

    def test_formatter_json_date_style(self, capsys):
        """Check that dates are stored in month-first format."""
        f = JSONFormatter(output=sys.stdout)
        f.printer(RESULTS)
        out, _ = capsys.readouterr()
        assert '"DOB": "12/05/2005"' in out

    def test_formatter_typeerror(self):
        """Ensure some correct text is in the output."""
        f = JSONFormatter(output=sys.stdout)
        with pytest.raises(TypeError):
            f.printer(RESULTS_BAD_TYPE)

    def test_formatter_python(self, capsys):
        """Ensure the python formatter displays objects correctly."""
        f = PythonFormatter(output=sys.stdout)
        f.printer({'key': 'value'})
        out, _ = capsys.readouterr()
        assert out.strip() == "{'key': 'value'}"

    def test_formatter_default(self, capsys):
        """Ensure the default formatter outputs to stdout."""
        f = Formatter(format_='default', output=sys.stdout)
        f.printer(RESULTS)
        out, _ = capsys.readouterr()
        assert "'Case': '19-0400694'" in out


RESULTS = [
    {
        'Age': 13,
        'Case': '19-0400694',
        'DOB': datetime.date(2005, 12, 5),
        'Date': 'February 9, 2019',
        'Ethnicity': 'Black',
        'Fatal crashes this year': '7',
        'First Name': 'Zion',
        'Gender': 'male',
        'Last Name': 'Mouton',
        'Link': 'http://austintexas.gov/news/traffic-fatality-7-4',
        'Location': '6000 block of Springdale Road',
        'Time': datetime.time(12, 48),
    },
]

RESULTS_BAD_TYPE = [
    {
        'Age': 13,
        'Case': set(),
        'DOB': '12/05/05',
    },
]
