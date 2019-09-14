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
from scrapd.core import model


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
        assert '19-2540190' in out

    def test_formatter_json_date_style(self, capsys):
        """Check that dates are stored in month-first format."""
        f = JSONFormatter(output=sys.stdout)
        f.printer(RESULTS)
        out, _ = capsys.readouterr()
        assert '"dob": "06/19/1978"' in out

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
        assert "case='19-2540190'" in out


RESULTS = [
    model.Report(
        case='19-2540190',
        crash=58,
        date=datetime.date(2019, 9, 11),
        fatalities=[
            model.Fatality(
                age=41,
                dob=datetime.date(1978, 6, 19),
                ethnicity=model.Ethnicity.white,
                gender=model.Gender.male,
                first='Joe',
                last='Ogg',
                middle='H',
            ),
        ],
        link='http://austintexas.gov/news/traffic-fatality-58-4',
        latitude=0.0,
        location='Hwy 290 WB at the 183 SB Flyover',
        longitude=0.0,
        notes='The preliminary investigation shows Joe H. Ogg was driving a red, 2001 Harley Davidson Motorcycle '
        'westbound on Hwy 290 to the southbound 183 flyover when he failed to negotiate the curve and struck a '
        'wall with the bike. Joe Ogg went over the wall, falling into the westbound lanes of 290 below. He was '
        'pronounced deceased on scene.',
        time=datetime.time(4, 37),
    )
]

RESULTS_BAD_TYPE = [
    {
        'Age': 13,
        'Case': set(),
        'DOB': '12/05/05',
    },
]
