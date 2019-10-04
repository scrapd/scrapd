"""
Define the formatter module.

This module contains all the classes with the ability to print the results. They destination depends on the custom
formatter used to print the results and can be sdtout, sdterr, a file or even a remote storage if the formatter allows
it.
"""
import csv
import datetime
import json
import pprint
import sys

from scrapd.core.constant import Fields
from scrapd.core import model

CSVFIELDS = [
    Fields.CRASH,
    Fields.CASE,
    Fields.DATE,
    Fields.TIME,
    Fields.LOCATION,
    Fields.FIRST_NAME,
    Fields.MIDDLE_NAME,
    Fields.LAST_NAME,
    Fields.GENERATION,
    Fields.ETHNICITY,
    Fields.GENDER,
    Fields.DOB,
    Fields.AGE,
    Fields.LINK,
    Fields.NOTES,
]


def json_serializers(obj):
    """
    Convert custom objects to string for serialization.

    :rtype: str
    """
    json_encoders = {
        datetime.date: lambda x: x.strftime("%Y-%m-%d"),
        datetime.time: lambda x: x.strftime("%H:%M:%S"),
        model.Ethnicity: lambda x: x.value,
        model.Fatality: lambda x: x.dict(),
        model.Gender: lambda x: x.value,
        model.Report: lambda x: x.dict(),
    }
    try:
        return json_encoders[type(obj)](obj)
    except KeyError:
        raise TypeError("Type %s not serializable" % type(obj))


def to_json(results):
    """
    Convert dict of parsed fields to JSON string.

    :param results dict: results of scraping APD news site

    :rtype: str
    """
    return json.dumps(results, sort_keys=True, indent=2, default=json_serializers)


class Formatter():
    """
    Define the Formatter base class.

    The default printer method simply uses the `print()` function.
    """

    formatters = {}
    __format_name__ = 'default'

    def __init__(self, format_='json', output=None):  # noqa: D107
        self.format = format_
        self.output = output or sys.stdout

    def __init_subclass__(cls, **kwargs):  # noqa: D105
        super().__init_subclass__(**kwargs)
        cls.formatters[cls.__format_name__] = cls

    def _get_formatter(self):
        """Return the appropriate formatter."""
        formatter = self.formatters.get(self.format, self)
        return formatter()

    def print(self, results, **kwargs):  # pragma: no cover
        """
        Print the results with the appropriate formatter.

        :param list(dict) results: the results to display.
        """
        # Coverage is disabled for this function as the fact that we set output to sys.stdout early messes up
        # with capsys in pytest, and prevents it to capture the out correctly.
        # https://github.com/pytest-dev/pytest/issues/1132
        formatter = self._get_formatter()
        formatter.printer(results, **kwargs)

    # pylint: disable=unused-argument
    def printer(self, results, **kwargs):
        """
        Define the printer method.

        :param list(dict) results: the results to display.
        """
        print(results, file=self.output)


class PythonFormatter(Formatter):
    """
    Define the Python formatter.

    Displays the results using `PrettyPrinter` with an indentation of 2 spaces.
    """

    __format_name__ = 'python'

    def printer(self, results, **kwargs):  # noqa: D102
        pp = pprint.PrettyPrinter(indent=2, stream=self.output)
        pp.pprint(results)


class JSONFormatter(Formatter):
    """
    Define the JSON formatter.

    Displays the results as JSON. The keys are sorted and an indentation of 2 spaces is set.
    """

    __format_name__ = 'json'

    def printer(self, results, **kwargs):  # noqa: D102
        json_string = to_json(results)
        print(json_string, file=self.output)


class CSVFormatter(Formatter):
    """
    Define the CSV formatter.

    Displays the results as a CSV.
    """

    __format_name__ = 'csv'

    def printer(self, results, **kwargs):  # noqa: D102
        rows = []
        for entry in results:
            for fatality in entry.fatalities:
                rows.append({
                    Fields.CRASH: entry.crash,
                    Fields.CASE: entry.case,
                    Fields.DATE: entry.date,
                    Fields.TIME: entry.time,
                    Fields.LOCATION: entry.location,
                    Fields.FIRST_NAME: fatality.first,
                    Fields.MIDDLE_NAME: fatality.middle,
                    Fields.LAST_NAME: fatality.last,
                    Fields.GENERATION: fatality.generation,
                    Fields.ETHNICITY: fatality.ethnicity.value,
                    Fields.GENDER: fatality.gender.value,
                    Fields.DOB: fatality.dob,
                    Fields.AGE: fatality.age,
                    Fields.LINK: entry.link,
                    Fields.NOTES: entry.notes,
                })
        writer = csv.DictWriter(self.output, fieldnames=CSVFIELDS, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


class CountFormatter(Formatter):
    """
    Define the Count formatter.

    Simply displays the number of results matching the search criterias.
    """

    __format_name__ = 'count'

    def printer(self, results, **kwargs):  # noqa: D102
        print(len(results), file=self.output)
