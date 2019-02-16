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
from scrapd.core.gsheets import GSheets

CSVFIELDS = [
    Fields.CRASHES,
    Fields.CASE,
    Fields.DATE,
    Fields.TIME,
    Fields.LOCATION,
    Fields.FIRST_NAME,
    Fields.LAST_NAME,
    Fields.ETHNICITY,
    Fields.GENDER,
    Fields.DOB,
    Fields.AGE,
    Fields.LINK,
    Fields.NOTES,
]


class Formatter():
    """
    Define the Formatter base class.

    The default printer method simply uses the `print()` function.
    """

    formatters = {}
    __format_name__ = 'default'

    def __init__(self, format_='json', output=sys.stdout):  # noqa: D107
        self.format = format_
        self.output = output

    def __init_subclass__(cls, **kwargs):  # noqa: D105
        super().__init_subclass__(**kwargs)
        cls.formatters[cls.__format_name__] = cls

    def _get_formatter(self):
        """Return the appropriate formatter."""
        formatter = self.formatters.get(self.format, self)
        return formatter()

    def print(self, results, **kwargs):
        """
        Print the results with the appropriate formatter.

        :param list(dict) results: the results to display.
        """
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
        print(json.dumps(results, sort_keys=True, indent=2), file=self.output)


class CSVFormatter(Formatter):
    """
    Define the CSV formatter.

    Displays the results as a CSV.
    """

    __format_name__ = 'csv'

    def printer(self, results, **kwargs):  # noqa: D102
        writer = csv.DictWriter(self.output, fieldnames=CSVFIELDS, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)


class GSheetFormatter(Formatter):
    """
    Define the GSheet formatter.

    Stores the results into a Google Sheets document.
    """

    __format_name__ = 'gsheets'

    def printer(self, results, **kwargs):  # noqa: D102
        credentials = kwargs.get('gcredentials')
        if not credentials:
            raise AttributeError('Google credentials are required.')
        contributors = kwargs.get('gcontributors', '').split(',')
        if not contributors:
            raise AttributeError('At least 1 contributor is required.')
        gs = GSheets(credentials, contributors)
        gs.authenticate()
        gs.create(datetime.datetime.now().strftime('%Y-%m-%d'))
        gs.add_csv_data(CSVFIELDS, results)


class CountFormatter(Formatter):
    """
    Define the Count formatter.

    Simply displays the number of results matching the search criterias.
    """

    __format_name__ = 'count'

    def printer(self, results, **kwargs):  # noqa: D102
        print(len(results), file=self.output)
