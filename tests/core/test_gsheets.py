"""Test the GSheets module."""
from faker import Faker
from gspread.models import Spreadsheet
from loguru import logger

from scrapd.core.gsheets import GSheets

logger.remove()


class Test_GSheets:
    """."""
    fake = Faker()

    def test_share_00(self, mocker):
        """Ensure the document is shared with valid contributors."""
        contributors = ['alice@gmail.com:user:writer', 'alice@gmail.com:user:reader']
        g = GSheets(self.fake.file_path(depth=1, category=None, extension='json'), contributors)
        g.spreadsheet = Spreadsheet(None, None)
        g.spreadsheet.share = mocker.MagicMock()

        g.share()

        assert g.spreadsheet.share.call_count == len(contributors)

    def test_share_01(self, mocker):
        """Ensure the document is not shared with invalid contributors."""
        contributors = ['alice@gmail.com']
        g = GSheets(self.fake.file_path(depth=1, category=None, extension='json'), contributors)
        g.spreadsheet = Spreadsheet(None, None)
        g.spreadsheet.share = mocker.MagicMock()

        g.share()

        assert not g.spreadsheet.share.called

    def test_add_csv_data_00(self, mocker):
        """Ensure the data is appended to the worksheet."""
        fake_fields = self.fake.pylist(10, True, str)
        fake_data = []
        for _ in range(self.fake.random_digit()):
            fake_entry = {}
            for field in fake_fields:
                fake_entry[field] = self.fake.word()
            fake_data.append(fake_entry)

        g = GSheets(self.fake.file_path(depth=1, category=None, extension='json'), [])
        g.spreadsheet = Spreadsheet(None, None)
        g.worksheet = mocker.MagicMock()
        g.worksheet.append_row = mocker.MagicMock()
        g.add_csv_data(fake_fields, fake_data)

        assert not g.worksheet.append_row.call_count == len(fake_data)
