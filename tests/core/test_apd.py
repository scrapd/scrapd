"""Test the APD module."""
from unittest import mock

import aiohttp
import asynctest
from loguru import logger
import pytest

from scrapd.core import apd
from scrapd.core.constant import Fields
from tests import mock_data
from tests.test_common import TEST_DATA_DIR
from tests.test_common import scenario_ids
from tests.test_common import scenario_inputs

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
        Fields.DOB: '02/09/1980',
        Fields.DATE: '12/30/2018',
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
        Fields.DATE: '12/21/2018',
        Fields.LOCATION: '9500 N Mopac SB',
        Fields.TIME: '8:20 p.m.',
    },
    'traffic-fatality-71-2': {
        Fields.CASE: '18-3381590',
        Fields.CRASHES: '71',
        Fields.DATE: '12/04/2018',
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
        Fields.DATE: '01/16/2019',
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
        Fields.DOB: '02/09/1980',
        Fields.DATE: '12/30/2018',
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
        Fields.DOB: '03/29/1996',
        Fields.ETHNICITY: 'White',
        Fields.FIRST_NAME: 'Elijah',
        Fields.GENDER: 'male',
        Fields.LAST_NAME: 'Perales',
    },
    'traffic-fatality-71-2': {
        **parse_twitter_fields_scenarios['traffic-fatality-71-2'],
        Fields.DOB: '06/01/1964',
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


@pytest.mark.parametrize('input_,expected', (
    (
        mock_data.twitter_title_00,
        {
            'Fatal crashes this year': '73'
        },
    ),
    (None, {}),
))
def test_parse_twitter_title_00(input_, expected):
    """Ensure the Twitter title gets parsed correct."""
    actual = apd.parse_twitter_title(input_)
    assert actual == expected


@pytest.mark.parametrize('input_,expected', (
    (
        mock_data.twitter_description_00,
        {
            'Case': '18-3640187',
            'Date': '12/30/2018',
            'Time': '2:24 a.m.',
            'Location': '1400 E. Highway 71 eastbound',
            'DOB': '02/09/1980',
            'Notes': 'The preliminary investigation shows that a 2003 Ford F150 was '
            'traveling northbound on the US Highway 183 northbound ramp to E. Highway 71, eastbound. '
            'The truck went across the E. Highway 71 and US Highway 183 ramp, rolled '
            'and came to a stop north of the roadway.',
            'Gender': 'male',
            'Ethnicity': 'White',
            'Last Name': 'Sabillon-Garcia',
            'First Name': 'Corbin',
            'Age': 38,
        },
    ),
    (None, {}),
))
def test_parse_twitter_description_00(input_, expected):
    """Ensure the Twitter description gets parsed correctly."""
    actual = apd.parse_twitter_description(input_)
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
        'DOB': '01/22/1961',
        'Date': '01/16/2018',
        'Location': '1500 W. Slaughter Lane',
        'Time': '5:14 p.m.',
    }
    assert actual == expected


def test_parse_twitter_description_03():
    """Ensure a DOB recognized as a field can be parsed."""
    actual = apd.parse_twitter_description(mock_data.twitter_description_03)
    expected = {}
    assert actual == expected


parse_details_page_notes_scenarios = [
    ((mock_data.details_page_notes_01, ''), 'Ensure a malformed entry is not parsed'),
    ((mock_data.details_page_notes_02, mock_data.details_page_notes_02_expected),
     'Ensure details page notes parsed correctly'),
]


@pytest.mark.parametrize(
    'input_,expected',
    scenario_inputs(parse_details_page_notes_scenarios),
    ids=scenario_ids(parse_details_page_notes_scenarios))
def test_parse_details_page_notes_01(input_, expected):
    """Ensure details page notes parsed correctly."""
    actual = apd.parse_details_page_notes(input_)
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


@pytest.mark.parametrize('deceased,expected', (
    ("Rosbel “Rudy” Tamez, Hispanic male (D.O.B. 10-10-54)", {
        Fields.FIRST_NAME: "Rosbel",
        Fields.LAST_NAME: "Tamez",
        Fields.ETHNICITY: "Hispanic",
        Fields.GENDER: "male",
        Fields.DOB: '10/10/1954',
    }),
    ("Eva Marie Gonzales, W/F, DOB: 01-22-1961 (passenger)", {
        Fields.FIRST_NAME: "Eva",
        Fields.LAST_NAME: "Gonzales",
        Fields.ETHNICITY: "White",
        Fields.GENDER: 'female',
        Fields.DOB: '01/22/1961',
    }),
    (
        'DOB: 01-01-99',
        {
            Fields.DOB: '01/01/1999',
        },
    ),
    (
        'Wing Cheung Chou | Asian male | 08/01/1949',
        {
            Fields.FIRST_NAME: "Wing",
            Fields.LAST_NAME: "Chou",
            Fields.ETHNICITY: "Asian",
            Fields.GENDER: "male",
            Fields.DOB: '08/01/1949',
        },
    ),
    (
        'Christopher M Peterson W/M 10-8-1981',
        {
            Fields.FIRST_NAME: "Christopher",
            Fields.LAST_NAME: "Peterson",
            Fields.ETHNICITY: "White",
            Fields.GENDER: "male",
            Fields.DOB: '10/08/1981',
        },
    ),
    (
        'Luis Angel Tinoco, Hispanic male (11-12-07',
        {
            Fields.FIRST_NAME: "Luis",
            Fields.LAST_NAME: "Tinoco",
            Fields.ETHNICITY: "Hispanic",
            Fields.GENDER: "male",
            Fields.DOB: '11/12/2007'
        },
    ),
    (
        'Ronnie Lee Hall, White male, 8-28-51',
        {
            Fields.FIRST_NAME: "Ronnie",
            Fields.LAST_NAME: "Hall",
            Fields.ETHNICITY: "White",
            Fields.GENDER: "male",
            Fields.DOB: '08/28/1951'
        },
    ),
))
def test_parse_deceased_field_00(deceased, expected):
    """Ensure a deceased field is parsed correctly."""
    d = {}
    d = apd.parse_deceased_field(deceased)
    for key in expected:
        assert d[key] == expected[key]


@pytest.mark.parametrize('name,expected', (
    (['Jonathan,', 'Garcia-Pineda,'], {
        'first': 'Jonathan',
        'last': 'Garcia-Pineda'
    }),
    (['Rosbel', '“Rudy”', 'Tamez'], {
        'first': 'Rosbel',
        'last': 'Tamez'
    }),
    (['Christopher', 'M', 'Peterson'], {
        'first': 'Christopher',
        'last': 'Peterson'
    }),
    (['David', 'Adam', 'Castro,'], {
        'first': 'David',
        'last': 'Castro'
    }),
    (['Delta', 'Olin,'], {
        'first': 'Delta',
        'last': 'Olin'
    }),
    (None, {
        'first': None,
        'last': None
    }),
))
def test_parse_name(name, expected):
    """Ensure parser finds the first and last name given the full name."""
    parsed = apd.parse_name(name)
    assert parsed.get("first") == expected["first"]
    assert parsed.get("last") == expected["last"]


def test_extract_traffic_fatalities_page_details_link_01():
    """Ensure page detail links are extracted from news page."""
    news_page = """
    <div class="views-field views-field-title">
        <span class="field-content">
            <a href="/news/traffic-fatality-59-update">Traffic Fatality #59- Update</a>
        </span>
    </div>
    """
    actual = apd.extract_traffic_fatalities_page_details_link(news_page)
    expected = [('/news/traffic-fatality-59-update', 'Traffic Fatality #59', '59')]
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
    """Ensure information are properly extracted from the content detail page.
           Don't compare notes if parsed from details page."""
    page_fd = TEST_DATA_DIR / filename
    page = page_fd.read_text()
    actual = apd.parse_page_content(page)
    if 'Notes' in actual and 'Notes' not in expected:
        del actual['Notes']
    assert actual == expected


def test_parse_page_content_01(mocker):
    """Ensure a `parse_deceased_field` exception is caught and does not propagate."""
    page_fd = TEST_DATA_DIR / 'traffic-fatality-2-3'
    page = page_fd.read_text()
    mocker.patch('scrapd.core.apd.parse_deceased_field', side_effect=ValueError)
    apd.parse_page_content(page)


@pytest.mark.parametrize('filename,expected', [(k, v) for k, v in parse_twitter_fields_scenarios.items()])
def test_parse_twitter_fields_00(filename, expected):
    """Ensure information are properly extracted from the twitter fields on detail page."""
    page_fd = TEST_DATA_DIR / filename
    page = page_fd.read_text()
    actual = apd.parse_twitter_fields(page)
    assert actual == expected


@pytest.mark.parametrize('filename,expected', [(k, v) for k, v in parse_page_scenarios.items()])
def test_parse_page_00(filename, expected):
    """Ensure information are properly extracted from the page.
       Don't compare notes if parsed from details page."""
    page_fd = TEST_DATA_DIR / filename
    page = page_fd.read_text()
    actual = apd.parse_page(page)
    if 'Notes' in actual and 'Notes' not in expected:
        del actual['Notes']
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
    data, actual = await apd.async_retrieve(pages=-1, from_="2050-01-02", to="2050-01-03")
    assert actual == expected
    assert isinstance(data, list)


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
async def test_date_filtering_01(fake_details, fake_news):
    """Ensure the date filtering do not fetch unnecessary data."""
    data, _ = await apd.async_retrieve(pages=-5, from_="2019-01-02", to="2019-01-03")
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_fetch_text_00():
    """Ensure `fetch_text` retries several times."""
    text = None
    apd.fetch_text.retry.sleep = mock.Mock()
    async with aiohttp.ClientSession() as session:
        try:
            text = await apd.fetch_text(session, 'fake_url')
        except Exception:
            pass
    assert not text
    assert apd.fetch_text.retry.statistics['attempt_number'] > 1


@asynctest.patch("scrapd.core.apd.fetch_news_page", side_effect=ValueError)
@pytest.mark.asyncio
async def test_async_retrieve_00(fake_news):
    """Ensure `async_retrieve` raises `ValueError` when `fetch_news_page` fails to retrieve data."""
    with pytest.raises(ValueError):
        _, _ = await apd.async_retrieve()


@pytest.mark.parametrize('input_,expected', (
    ('<p><strong>Case:         </strong>19-0881844</p>', '19-0881844'),
    ('<p><strong>Case:</strong>           18-3640187</p>', '18-3640187'),
    ('<strong>Case:</strong></span><span style="color: rgb(32, 32, 32); '
     'font-family: &quot;Verdana&quot;,sans-serif; font-size: 10.5pt; '
     'mso-fareast-font-family: &quot;Times New Roman&quot;; '
     'mso-ansi-language: EN-US; mso-fareast-language: EN-US; mso-bidi-language: AR-SA; '
     'mso-bidi-font-family: &quot;Times New Roman&quot;;">           19-0161105</span></p>', '19-0161105'),
))
def test_parse_case_field_00(input_, expected):
    """Ensure a case field gets parsed correctly."""
    actual = apd.parse_case_field(input_)
    assert actual == expected
