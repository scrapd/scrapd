"""Test the APD module."""
from loguru import logger
import asynctest
import pytest

from scrapd.core import apd
from scrapd.core.constant import Fields
from tests import mock_data
from tests.test_common import TEST_DATA_DIR

# Disable logging for the tests.
logger.remove()


def load_test_page(page):
    """Load a test page."""
    page_fd = TEST_DATA_DIR / page
    return page_fd.read_text()


@pytest.fixture
def news_page(scope='session'):
    """Returns the test news page."""
    page_fd = TEST_DATA_DIR / 'news_page.html'
    return page_fd.read_text()


parse_twitter_fields_scenarios = {
    'traffic-fatality-2-3': {
        Fields.CASE: '19-0161105',
        Fields.CRASHES: '2',
    },
    'traffic-fatality-73-2': {
        Fields.AGE: 38,
        Fields.CASE: '18-3640187',
        Fields.CRASHES: '73',
        Fields.DOB: '02/09/80',
        Fields.DATE: 'December 30, 2018',
        Fields.ETHNICITY: 'White',
        Fields.FIRST_NAME: 'Corbin',
        Fields.GENDER: 'male',
        Fields.LAST_NAME: 'Sabillon-Garcia',
        Fields.LOCATION: '1400 E. Highway 71 eastbound',
        Fields.NOTES: 'The preliminary investigation shows that a 2003 Ford F150 was '
        'traveling northbound on the US Highway 183 northbound ramp to E. '
        'Highway 71, eastbound. The truck went across the E. Highway 71 and '
        'US Highway 183 ramp, rolled and came to a stop north of the '
        'roadway.',
        Fields.TIME: '2:24 a.m.',
    },
    'traffic-fatality-72-1': {
        Fields.CASE: '18-3551763',
        Fields.CRASHES: '72',
        Fields.DATE: 'December 21, 2018',
        Fields.LOCATION: '9500 N Mopac SB',
        Fields.TIME: '8:20 p.m.',
    },
    'traffic-fatality-71-2': {
        Fields.CASE: '18-3381590',
        Fields.CRASHES: '71',
        Fields.DATE: 'December 4, 2018',
        Fields.LOCATION: '183 service road westbound and Payton Gin Rd.',
        Fields.TIME: '8:39 p.m.',
    },
}

parse_page_content_scenarios = {
    'traffic-fatality-2-3': {
        **parse_twitter_fields_scenarios['traffic-fatality-2-3'],
        Fields.AGE: 58,
        Fields.CRASHES: '2',
        Fields.DOB: '02/15/1960',
        Fields.DATE: 'January 16, 2019',
        Fields.ETHNICITY: 'White',
        Fields.FIRST_NAME: 'Ann',
        Fields.GENDER: 'female',
        Fields.LAST_NAME: 'Bottenfield-Seago',
        Fields.LOCATION: 'West William Cannon Drive and Ridge Oak Road',
        Fields.TIME: '3:42 p.m.',
    },
    'traffic-fatality-73-2': {
        Fields.AGE: 38,
        Fields.CASE: '18-3640187',
        Fields.CRASHES: '73',
        Fields.DOB: '02/09/80',
        Fields.DATE: 'December 30, 2018',
        Fields.ETHNICITY: 'White',
        Fields.FIRST_NAME: 'Corbin',
        Fields.GENDER: 'male',
        Fields.LAST_NAME: 'Sabillon-Garcia',
        Fields.LOCATION: '1400 E. Highway 71 eastbound',
        Fields.TIME: '2:24 a.m.',
    },
    'traffic-fatality-72-1': {
        **parse_twitter_fields_scenarios['traffic-fatality-72-1'],
        Fields.AGE: 22,
        Fields.DOB: '3-29-96',
        Fields.ETHNICITY: 'White',
        Fields.FIRST_NAME: 'Elijah',
        Fields.GENDER: 'male',
        Fields.LAST_NAME: 'Perales',
    },
    'traffic-fatality-71-2': {
        **parse_twitter_fields_scenarios['traffic-fatality-71-2'],
        Fields.DOB: '6-1-64',
        Fields.FIRST_NAME: 'Barkat',
        Fields.LAST_NAME: 'Umatia',
        Fields.ETHNICITY: 'Other',
        Fields.GENDER: 'male',
        Fields.AGE: 54,
    }
}

parse_page_scenarios = {
    'traffic-fatality-2-3': {
        **parse_page_content_scenarios['traffic-fatality-2-3'],
        **parse_twitter_fields_scenarios['traffic-fatality-2-3'],
    },
    'traffic-fatality-73-2': {
        **parse_page_content_scenarios['traffic-fatality-73-2'],
        **parse_twitter_fields_scenarios['traffic-fatality-73-2'],
    },
    'traffic-fatality-72-1': {
        **parse_page_content_scenarios['traffic-fatality-72-1'],
        **parse_twitter_fields_scenarios['traffic-fatality-72-1'],
    },
}


def test_parse_twitter_title_00():
    """Ensure the Twitter title gets parsed correct: """
    actual = apd.parse_twitter_title(mock_data.twitter_title_00)
    expected = {'Fatal crashes this year': '73'}
    assert actual == expected


def test_parse_twitter_description_00():
    """Ensure the Twitter description gets parsed correctly."""
    actual = apd.parse_twitter_description(mock_data.twitter_description_00)
    expected = {
        'Case': '18-3640187',
        'Date': 'December 30, 2018',
        'Time': '2:24 a.m.',
        'Location': '1400 E. Highway 71 eastbound',
        'DOB': '02/09/80',
        'Notes': 'The preliminary investigation shows that a 2003 Ford F150 was traveling northbound on the US Highway 183 northbound ramp to E. Highway 71, eastbound. The truck went across the E. Highway 71 and US Highway 183 ramp, rolled and came to a stop north of the roadway.',
        'Gender': 'male',
        'Ethnicity': 'White',
        'Last Name': 'Sabillon-Garcia',
        'First Name': 'Corbin',
        'Age': 38,
    }
    assert actual == expected


def test_parse_twitter_description_01():
    """Ensure the Twitter description gets parsed correctly."""
    actual = apd.parse_twitter_description(mock_data.twitter_description_01)
    expected = {
        Fields.CASE: '19-0161105',
    }
    assert actual == expected


def test_parse_twitter_description_02():
    """Ensure a DOB recognized as a field can be parsed."""
    actual = apd.parse_twitter_description(mock_data.twitter_description_02)
    expected = {
        'Age': 57,
        'Case': '18-160882',
        'DOB': '01-22-1961',
        'Date': 'Tuesday, January 16, 2018',
        'Location': '1500 W. Slaughter Lane',
        'Time': '5:14 p.m.',
    }
    assert actual == expected


def test_extract_traffic_fatalities_page_details_link_00(news_page):
    """Ensure page detail links are extracted from news page."""
    actual = apd.extract_traffic_fatalities_page_details_link(news_page)
    expected = [
        ('/news/traffic-fatality-2-3', 'Traffic Fatality #2', '2'),
        ('/news/traffic-fatality-1-4', 'Traffic Fatality #1', '1'),
        ('/news/traffic-fatality-72-1', 'Traffic Fatality #72', '72'),
        ('/news/traffic-fatality-73-2', 'Traffic Fatality #73', '73'),
        ('/news/traffic-fatality-71-2', 'Traffic Fatality #71', '71'),
        ('/news/traffic-fatality-69-3', 'Traffic Fatality #69', '69'),
    ]
    assert actual == expected


def test_generate_detail_page_urls_00():
    """Ensure a full URL is generated from a partial one."""
    actual = apd.generate_detail_page_urls([
        ('/news/traffic-fatality-1-4', 'Traffic Fatality #1', '1'),
        ('/news/traffic-fatality-2-3', 'Traffic Fatality #2', '2'),
    ])
    expected = [
        'http://austintexas.gov/news/traffic-fatality-1-4',
        'http://austintexas.gov/news/traffic-fatality-2-3',
    ]
    assert actual == expected


def test_has_next_00(news_page):
    """Ensure we detect whether there are more news pages."""
    assert apd.has_next(news_page)


def test_has_next_01():
    """Ensure we detect whether there are no more news pages."""
    assert apd.has_next(None) is False


@pytest.mark.parametrize('filename,expected', [(k, v) for k, v in parse_page_content_scenarios.items()])
def test_parse_page_content_00(filename, expected):
    """Ensure information are properly extracted from the content detail page."""
    page_fd = TEST_DATA_DIR / filename
    page = page_fd.read_text()
    actual = apd.parse_page_content(page)
    assert actual == expected


@pytest.mark.parametrize('filename,expected', [(k, v) for k, v in parse_twitter_fields_scenarios.items()])
def test_parse_twitter_fields_00(filename, expected):
    """Ensure information are properly extracted from the twitter fields on detail page."""
    page_fd = TEST_DATA_DIR / filename
    page = page_fd.read_text()
    actual = apd.parse_twitter_fields(page)
    assert actual == expected


@pytest.mark.parametrize('filename,expected', [(k, v) for k, v in parse_page_scenarios.items()])
def test_parse_page_00(filename, expected):
    """Ensure information are properly extracted from the page."""
    page_fd = TEST_DATA_DIR / filename
    page = page_fd.read_text()
    actual = apd.parse_page(page)
    assert actual == expected


@asynctest.patch(
    "scrapd.core.apd.fetch_news_page",
    side_effect=[load_test_page(page) for page in [
        '296',
        '296?page=1',
        '296?page=27',
    ]])
@asynctest.patch(
    "scrapd.core.apd.fetch_detail_page",
    return_value=load_test_page('traffic-fatality-2-3'),
)
@pytest.mark.asyncio
async def test_date_filtering_00(fake_details, fake_news):
    """Ensure the date filtering do not fetch unnecessary data."""
    expected = 2
    _, actual = await apd.async_retrieve(pages=-1, from_="2050-01-02", to="2050-01-03")
    assert actual == expected
