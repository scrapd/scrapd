"""Define the common values and functions to run the tests."""
from pathlib import Path

from scrapd.core import constant

TEST_ROOT_DIR = Path(__file__).resolve().parent
TEST_DATA_DIR = TEST_ROOT_DIR / 'data'
TEST_DUMP_DIR = TEST_ROOT_DIR.parent / constant.DUMP_DIR


def load_test_page(page):
    """Load a test page."""
    page_fd = TEST_DATA_DIR / page
    return page_fd.read_text()


def load_dumped_page(page):
    """Load a dumped page."""
    page_fd = TEST_DUMP_DIR / page
    return page_fd.read_text()


def scenario_inputs(scenarios):
    """Parse the scenarios and feed the data to the test function."""
    return [test_input[0] for test_input in scenarios]


def scenario_ids(scenarios):
    """Parse the scenarios and feed the IDs to the test function."""
    return [test_input[1] for test_input in scenarios]
