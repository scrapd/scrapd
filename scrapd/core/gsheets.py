"""Define a wrapper around GSpread to manipulate Google Spreadsheets."""

import gspread
from loguru import logger
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']


class GSheets:
    """Manipulate Google Spreadsheets."""

    def __init__(self, credential_file=None, contributors=None):
        """
        Initialize the instance.

        :param str credential_file: path to the Google Sheets credentials file
        :param str contributors: list of contributors to this document
        """

        self.gc = None
        self.gc_file = credential_file
        self.contributors = contributors if contributors else []
        self.spreadsheet = None
        self.worksheet = None

    def authenticate(self):  # pragma: no cover
        """Authenticate against the spreadsheet service."""
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.gc_file, SCOPE)
        self.gc = gspread.authorize(credentials)

    def create(self, name):  # pragma: no cover
        """
        Create a new spreadsheet.

        :param str name: spreadsheet name.
        """
        # Create a new spreadsheet.
        self.spreadsheet = self.gc.create(name)

        # Share it with contributors to be able to use it.
        self.share()

        # Use the first sheet.
        self.worksheet = self.spreadsheet.get_worksheet(0)

    def share(self):
        """
        Share the spreadsheet with contributors.

        Expected contributor format: `<account>:<type>:<role>`
        """
        for contributor in self.contributors:
            try:
                account, type_, role_ = contributor.split(':')
            except ValueError as e:
                logger.error(f'Cannot parse contributor "{contributor}". Verify the format: {e}')
            else:
                self.spreadsheet.share(account, perm_type=type_, role=role_)

    def add_csv_data(self, fieldnames, data):
        """
        Add data from a CSV.

        :param list(str) fieldnames: first line of the document, headers
        :param list(dict )data: a list of dictionary where each entry represents a fatality
        """
        # Write the headers.
        logger.debug(f'Add headers: {fieldnames}')
        self.worksheet.append_row(fieldnames)

        # Go through the data.
        for entry in data:
            # Prepare row.
            row = []
            for fieldname in fieldnames:
                row.append(entry.get(fieldname, ''))

            # Add row.
            logger.debug(f'Append row: {row}')
            self.worksheet.append_row(row)
