"""Define the scenarios for the feature tests."""
import pytest
from pytest_bdd import given
from pytest_bdd import scenario
from pytest_bdd import then

from scrapd.core import apd
from scrapd.core import model
from scrapd.core.formatter import Formatter
from tests.test_common import TEST_ROOT_DIR


@scenario(
    TEST_ROOT_DIR / 'features/retrieve.feature',
    'Retrieve information',
    example_converters={'entry_count': int},
)
def test_collect_information():
    """Ensure a user retrieves correct information."""


@given('the user wants to store the results in <format>')
def output_format(format):
    """Define the output format specified by the user."""
    return {'format': format}


@given('retrieve the fatality details from <from_date> to <to_date>')
def time_range(from_date, to_date):
    """Define the time range specified by the user."""
    time_range_params = {}
    if from_date:
        time_range_params['from_'] = from_date or None
    if to_date:
        time_range_params['to'] = to_date or None
    return time_range_params


@then('the generated file must contain <entry_count> entries')
@pytest.mark.asyncio
def ensure_results(mocker, event_loop, output_format, time_range, entry_count):
    """Ensure we get the right amount of entries."""
    results, _ = event_loop.run_until_complete(apd.async_retrieve(pages=-1, **time_range))
    assert results is not None
    assert len(results) == entry_count
    assert isinstance(results, list)
    if results:
        assert isinstance(results[0], model.Report)

    # Get the format and print the results.
    format_ = output_format['format'].lower()
    formatter = Formatter(format_)
    formatter.print(results)
