"""Test the APD module."""
import datetime
from unittest import mock

import aiohttp
from aioresponses import aioresponses
import asynctest
from faker import Faker
from loguru import logger
import pytest
from tenacity import RetryError
from tenacity import stop_after_attempt

from scrapd.core import apd
from scrapd.core.constant import Fields
from tests import mock_data
from tests.test_common import TEST_DATA_DIR
from tests.test_common import scenario_ids
from tests.test_common import scenario_inputs

# Disable logging for the tests.
logger.remove()

# Set faker object.
fake = Faker()


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
        Fields.DOB: datetime.date(1980, 2, 9),
        Fields.DATE: datetime.date(2018, 12, 30),
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
        Fields.TIME: datetime.time(2, 24),
    },
    'traffic-fatality-72-1': {
        Fields.CASE: '18-3551763',
        Fields.CRASHES: '72',
        Fields.DATE: datetime.date(2018, 12, 21),
        Fields.LOCATION: '9500 N Mopac SB',
        Fields.TIME: datetime.time(20, 20),
    },
    'traffic-fatality-71-2': {
        Fields.CASE: '18-3381590',
        Fields.CRASHES: '71',
        Fields.DATE: datetime.date(2018, 12, 4),
        Fields.LOCATION: '183 service road westbound and Payton Gin Rd.',
        Fields.TIME: datetime.time(20, 39),
    },
}

parse_page_content_scenarios = {
    'traffic-fatality-2-3': {
        **parse_twitter_fields_scenarios['traffic-fatality-2-3'],
        Fields.AGE: 58,
        Fields.CRASHES: '2',
        Fields.DOB: datetime.date(1960, 2, 15),
        Fields.DATE: datetime.date(2019, 1, 16),
        Fields.ETHNICITY: 'White',
        Fields.FIRST_NAME: 'Ann',
        Fields.GENDER: 'female',
        Fields.LAST_NAME: 'Bottenfield-Seago',
        Fields.LOCATION: 'West William Cannon Drive and Ridge Oak Road',
        Fields.TIME: datetime.time(15, 42),
    },
    'traffic-fatality-73-2': {
        Fields.AGE: 38,
        Fields.CASE: '18-3640187',
        Fields.CRASHES: '73',
        Fields.DOB: datetime.date(1980, 2, 9),
        Fields.DATE: datetime.date(2018, 12, 30),
        Fields.ETHNICITY: 'White',
        Fields.FIRST_NAME: 'Corbin',
        Fields.GENDER: 'male',
        Fields.LAST_NAME: 'Sabillon-Garcia',
        Fields.LOCATION: '1400 E. Highway 71 eastbound',
        Fields.TIME: datetime.time(2, 24),
    },
    'traffic-fatality-72-1': {
        **parse_twitter_fields_scenarios['traffic-fatality-72-1'],
        Fields.AGE: 22,
        Fields.DOB: datetime.date(1996, 3, 29),
        Fields.ETHNICITY: 'White',
        Fields.FIRST_NAME: 'Elijah',
        Fields.GENDER: 'male',
        Fields.LAST_NAME: 'Perales',
    },
    'traffic-fatality-71-2': {
        **parse_twitter_fields_scenarios['traffic-fatality-71-2'],
        Fields.DOB: datetime.date(1964, 6, 1),
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
            'Date': datetime.date(2018, 12, 30),
            'Time': datetime.time(2, 24),
            'Location': '1400 E. Highway 71 eastbound',
            'DOB': datetime.date(1980, 2, 9),
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
    if 'Deceased' in actual:
        del actual['Deceased']
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
        'DOB': datetime.date(1961, 1, 22),
        'Date': datetime.date(2018, 1, 16),
        'Location': '1500 W. Slaughter Lane',
        'Time': datetime.time(17, 14),
    }
    if 'Deceased' in actual:
        del actual['Deceased']
    assert actual == expected


def test_parse_twitter_description_03():
    """Ensure a DOB recognized as a field can be parsed."""
    actual = apd.parse_twitter_description(mock_data.twitter_description_03)
    expected = {}
    assert actual == expected


@pytest.mark.parametrize('page,start,end',
                         scenario_inputs(mock_data.note_fields_scenarios),
                         ids=scenario_ids(mock_data.note_fields_scenarios))
def test_parse_notes_field(page, start, end):
    """Ensure Notes field are parsed correctly."""
    soup = apd.to_soup(page)
    deceased_tag_p, deceased_field_str = apd.parse_deceased_field(soup)
    notes = apd.notes_from_element(deceased_tag_p, deceased_field_str)
    assert notes.startswith(start)
    assert notes.endswith(end)


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
        Fields.DOB: datetime.date(1954, 10, 10),
    }),
    ("Eva Marie Gonzales, W/F, DOB: 01-22-1961 (passenger)", {
        Fields.FIRST_NAME: "Eva",
        Fields.LAST_NAME: "Gonzales",
        Fields.ETHNICITY: "White",
        Fields.GENDER: 'female',
        Fields.DOB: datetime.date(1961, 1, 22),
    }),
    (
        'DOB: 01-01-99',
        {
            Fields.DOB: datetime.date(1999, 1, 1),
        },
    ),
    (
        'Wing Cheung Chou | Asian male | 08/01/1949',
        {
            Fields.FIRST_NAME: "Wing",
            Fields.LAST_NAME: "Chou",
            Fields.ETHNICITY: "Asian",
            Fields.GENDER: "male",
            Fields.DOB: datetime.date(1949, 8, 1),
        },
    ),
    (
        'Christopher M Peterson W/M 10-8-1981',
        {
            Fields.FIRST_NAME: "Christopher",
            Fields.LAST_NAME: "Peterson",
            Fields.ETHNICITY: "White",
            Fields.GENDER: "male",
            Fields.DOB: datetime.date(1981, 10, 8),
        },
    ),
    (
        'Luis Angel Tinoco, Hispanic male (11-12-07',
        {
            Fields.FIRST_NAME: "Luis",
            Fields.LAST_NAME: "Tinoco",
            Fields.ETHNICITY: "Hispanic",
            Fields.GENDER: "male",
            Fields.DOB: datetime.date(2007, 11, 12)
        },
    ),
    (
        'Ronnie Lee Hall, White male, 8-28-51',
        {
            Fields.FIRST_NAME: "Ronnie",
            Fields.LAST_NAME: "Hall",
            Fields.ETHNICITY: "White",
            Fields.GENDER: "male",
            Fields.DOB: datetime.date(1951, 8, 28)
        },
    ),
    (
        'Hispanic male, 19 years of age',
        {
            Fields.ETHNICITY: "Hispanic",
            Fields.GENDER: "male",
            Fields.AGE: 19,
        },
    ),
    (
        'Patrick Leonard Ervin, Black male, D.O.B. August 30, 1966',
        {
            Fields.FIRST_NAME: "Patrick",
            Fields.LAST_NAME: "Ervin",
            Fields.ETHNICITY: "Black",
            Fields.GENDER: "male",
            Fields.DOB: datetime.date(1966, 8, 30)
        },
    ),
    (
        'Ernesto Gonzales Garcia, H/M, (DOB: 11/15/1977) ',
        {
            Fields.FIRST_NAME: "Ernesto",
            Fields.LAST_NAME: "Garcia",
            Fields.ETHNICITY: "Hispanic",
            Fields.GENDER: "male",
            Fields.DOB: datetime.date(1977, 11, 15)
        },
    ),
    (
        'B/F, DOB: 01-01-99',
        {
            Fields.ETHNICITY: "Black",
            Fields.GENDER: "female",
            Fields.DOB: datetime.date(1999, 1, 1)
        },
    ),
))
def test_process_deceased_field_00(deceased, expected):
    """Ensure a deceased field is parsed correctly."""
    d = apd.process_deceased_field(deceased)
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
        'last': None,
    }),
    (['Carlos', 'Cardenas', 'Jr.'], {
        'first': 'Carlos',
        'last': 'Cardenas',
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


@pytest.mark.parametrize(
    'input_,expected',
    (('<div class="item-list"><ul class="pager"><li class="pager-previous first">&nbsp;</li>'
      '<li class="pager-current">1 of 27</li>'
      '<li class="pager-next last"><a title="Go to next page" href="/department/news/296-page=1">next ›</a></li>'
      '</ul></div>', True), ))
def test_has_next_02(input_, expected):
    """Ensure we detect whether there are more news pages."""
    assert apd.has_next(input_) == expected


@pytest.mark.parametrize('filename,expected', [(k, v) for k, v in parse_page_content_scenarios.items()])
def test_parse_page_content_00(filename, expected):
    """Ensure information are properly extracted from the content detail page.
           Don't compare notes if parsed from details page."""
    page_fd = TEST_DATA_DIR / filename
    page = page_fd.read_text()
    actual, err = apd.parse_page_content(page)
    if 'Notes' in actual and 'Notes' not in expected:
        del actual['Notes']
    if 'Deceased' in actual and 'Deceased' not in expected:
        del actual['Deceased']
    assert actual == expected


def test_parse_page_content_01(mocker):
    """Ensure a `process_deceased_field` exception is caught and does not propagate."""
    page_fd = TEST_DATA_DIR / 'traffic-fatality-2-3'
    page = page_fd.read_text()
    mocker.patch('scrapd.core.apd.process_deceased_field', side_effect=ValueError)
    result, err = apd.parse_page_content(page)
    if 'Deceased' in result:
        del result['Deceased']
    assert len(result) == 6


def test_parse_page_content_02(mocker):
    """Ensure a log entry is created if there is no deceased field."""
    result, err = apd.parse_page_content('Case: 01-2345678')
    assert result


def test_parse_page_content_03():
    """Ensure a missing case number raises an exception."""
    with pytest.raises(ValueError):
        apd.parse_page_content('The is no case number here.')


@pytest.mark.parametrize('filename,expected', [(k, v) for k, v in parse_twitter_fields_scenarios.items()])
def test_parse_twitter_fields_00(filename, expected):
    """Ensure information are properly extracted from the twitter fields on detail page."""
    page_fd = TEST_DATA_DIR / filename
    page = page_fd.read_text()
    actual = apd.parse_twitter_fields(page)
    if 'Deceased' in actual and 'Deceased' not in expected:
        del actual['Deceased']
    assert actual == expected


@pytest.mark.parametrize('filename,expected', [(k, v) for k, v in parse_page_scenarios.items()])
def test_parse_page_00(filename, expected):
    """Ensure information are properly extracted from the page.
       Don't compare notes if parsed from details page."""
    page_fd = TEST_DATA_DIR / filename
    page = page_fd.read_text()
    actual = apd.parse_page(page, fake.uri())
    if 'Notes' in actual and 'Notes' not in expected:
        del actual['Notes']
    assert actual == expected


@pytest.mark.parametrize('filename,expected', [(k, v) for k, v in parse_page_scenarios.items()])
def test_parse_page_01(mocker, filename, expected):
    """Ensuring ."""
    data = {}
    parsing_errors = ['one error']
    page_fd = TEST_DATA_DIR / filename
    page = page_fd.read_text()
    pc = mocker.patch('scrapd.core.apd.parse_page_content', return_value=(data, parsing_errors))
    _ = apd.parse_page(page, fake.uri())
    assert pc.called_once


@asynctest.patch("scrapd.core.apd.fetch_news_page",
                 side_effect=[load_test_page(page) for page in ['296', '296-page=1', '296-page=27']])
@asynctest.patch("scrapd.core.apd.fetch_detail_page", return_value=load_test_page('traffic-fatality-2-3'))
@pytest.mark.asyncio
async def test_date_filtering_00(fake_details, fake_news):
    """Ensure the date filtering do not fetch unnecessary data."""
    expected = 2
    data, actual = await apd.async_retrieve(pages=-1, from_="2050-01-02", to="2050-01-03")
    assert actual == expected
    assert isinstance(data, list)


@asynctest.patch("scrapd.core.apd.fetch_news_page",
                 side_effect=[load_test_page(page) for page in ['296', '296-page=1', '296-page=27']])
@asynctest.patch("scrapd.core.apd.fetch_detail_page", return_value=load_test_page('traffic-fatality-2-3'))
@pytest.mark.asyncio
async def test_date_filtering_01(fake_details, fake_news):
    """Ensure the date filtering do not fetch unnecessary data."""
    data, _ = await apd.async_retrieve(pages=-5, from_="2019-01-02", to="2019-01-03")
    assert isinstance(data, list)


@asynctest.patch("scrapd.core.apd.fetch_news_page",
                 side_effect=[load_test_page(page) for page in ['296', '296-page=1', '296-page=27']])
@asynctest.patch(
    "scrapd.core.apd.fetch_detail_page",
    side_effect=[load_test_page(page) for page in ['traffic-fatality-2-3'] + ['traffic-fatality-71-2'] * 14])
@pytest.mark.asyncio
async def test_date_filtering_02(fake_details, fake_news):
    """Ensure the date filtering do not fetch unnecessary data."""
    data, page_count = await apd.async_retrieve(from_="2019-01-16", to="2019-01-16")
    assert isinstance(data, list)
    assert len(data) == 1
    assert page_count == 2


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


@pytest.mark.asyncio
async def test_fetch_text_01():
    """Ensure fetch_text retrieves some text."""
    url = fake.uri()
    with aioresponses() as m:
        m.get(url, payload=dict(foo='bar'))
        async with aiohttp.ClientSession() as session:
            text = await apd.fetch_text(session, url)
            assert '{"foo": "bar"}' == text


@asynctest.patch("scrapd.core.apd.fetch_news_page", side_effect=ValueError)
@pytest.mark.asyncio
async def test_async_retrieve_00(fake_news):
    """Ensure `async_retrieve` raises `ValueError` when `fetch_news_page` fails to retrieve data."""
    with pytest.raises(ValueError):
        await apd.async_retrieve()


@pytest.mark.parametrize('input_,expected', (
    ('<p><strong>Case:         </strong>19-0881844</p>', '19-0881844'),
    ('<p><strong>Case:</strong>           18-3640187</p>', '18-3640187'),
    ('<strong>Case:</strong></span><span style="color: rgb(32, 32, 32); '
     'font-family: &quot;Verdana&quot;,sans-serif; font-size: 10.5pt; '
     'mso-fareast-font-family: &quot;Times New Roman&quot;; '
     'mso-ansi-language: EN-US; mso-fareast-language: EN-US; mso-bidi-language: AR-SA; '
     'mso-bidi-font-family: &quot;Times New Roman&quot;;">           19-0161105</span></p>', '19-0161105'),
    ('<p><strong>Case:</strong>            18-1591949 </p>', '18-1591949'),
    ('<p><strong>Case:</strong>            18-590287<br />', '18-590287'),
))
def test_parse_case_field_00(input_, expected):
    """Ensure a case field gets parsed correctly."""
    actual = apd.parse_case_field(input_)
    assert actual == expected


@pytest.mark.parametrize(
    'input_, expected',
    (('<span property="dc:title" content="Traffic Fatality #12" class="rdf-meta element-hidden"></span>', '12'), ))
def test_parse_crashes_field_00(input_, expected):
    """Ensure the crashes field gets parsed correctly."""
    actual = apd.parse_crashes_field(input_)
    assert actual == expected


@asynctest.patch("scrapd.core.apd.fetch_detail_page", return_value='')
@pytest.mark.asyncio
async def test_fetch_and_parse_00(empty_page):
    """Ensure an empty page raises an exception."""
    with pytest.raises(RetryError):
        apd.fetch_and_parse.retry.stop = stop_after_attempt(1)
        await apd.fetch_and_parse(None, 'url')


@asynctest.patch("scrapd.core.apd.fetch_detail_page", return_value='Not empty page')
@pytest.mark.asyncio
async def test_fetch_and_parse_01(page, mocker):
    """Ensure a page that cannot be parsed returns an exception."""
    mocker.patch("scrapd.core.apd.parse_page", return_value={})
    with pytest.raises(RetryError):
        apd.fetch_and_parse.retry.stop = stop_after_attempt(1)
        await apd.fetch_and_parse(None, 'url')


@asynctest.patch("scrapd.core.apd.fetch_text", return_value='')
@pytest.mark.asyncio
async def test_fetch_news_page_00(fetch_text):
    """Ensure the fetch function is called with the right parameters."""
    page = 2
    params = {'page': page - 1}
    async with aiohttp.ClientSession() as session:
        try:
            await apd.fetch_news_page(session, page)
        except Exception:
            pass
    fetch_text.assert_called_once_with(session, apd.APD_URL, params)


@asynctest.patch("scrapd.core.apd.fetch_text", return_value='')
@pytest.mark.asyncio
async def test_fetch_detail_page_00(fetch_text):
    """Ensure the fetch function is called with the right parameters."""
    url = fake.uri()
    async with aiohttp.ClientSession() as session:
        try:
            await apd.fetch_detail_page(session, url)
        except Exception:
            pass
    fetch_text.assert_called_once_with(session, url)


@pytest.mark.parametrize('input_,expected',
                         (('<meta name="twitter:title" content="Traffic Fatality #2" />', 'Traffic Fatality #2'), ))
def test_extract_twitter_tittle_meta_00(input_, expected):
    """Ensure we can extract the twitter tittle from the meta tag."""
    actual = apd.extract_twitter_tittle_meta(input_)
    assert actual == expected


@pytest.mark.parametrize('input_,expected', (
    ('<meta name="twitter:description" content="Case:           18-3551763 Date:            December 21, 2018 '
     'Time:            8:20 p.m. Location:     9500 N Mopac SB" />',
     'Case:           18-3551763 Date:            December 21, 2018 Time:            8:20 p.m. '
     'Location:     9500 N Mopac SB'),
    ('<meta name="twitter:description" content="Case:           19-0161105" />', 'Case:           19-0161105'),
))
def test_extract_twitter_description_meta_00(input_, expected):
    """Ensure we can extract the twitter tittle from the meta tag."""
    actual = apd.extract_twitter_description_meta(input_)
    assert actual == expected


@pytest.mark.parametrize('input_,expected', (
    ('Time: </span>   Approximately 01:14a.m.', datetime.time(1, 14)),
    ('<tag>Time:     08:35 pm<br />', datetime.time(20, 35)),
    ('Time:  8:47  P.M.', datetime.time(20, 47)),
    ('Time:12:47 p.M.', datetime.time(12, 47)),
    ('Time: 5:16', datetime.time(5, 16)),
    ('Time: 05:16 ', datetime.time(5, 16)),
    ('Time: 18:26', datetime.time(18, 26)),
    ('Time: 22:56', datetime.time(22, 56)),
    ('Time: 54:34', None),
    ('Time: 28:24', None),
    ('Time: 4:66 pm', None),
    ('Time: 18:46 pm', datetime.time(18, 46)),
    ('Time: 00:24 a.m.', datetime.time(0, 24)),
    ('<p>	<strong>Time:</strong>       8 p.m.</p>', datetime.time(20, 0)),
))
def test_parse_time_field_00(input_, expected):
    """Ensure a time field gets parsed correctly."""
    actual = apd.parse_time_field(input_)
    assert actual == expected


@pytest.mark.parametrize('input_,expected', (
    ('<strong>Date:   </strong>April 18, 2019</p>', datetime.date(2019, 4, 18)),
    ('>Date:   </strong> Night of May 22 2019</p>', datetime.date(2019, 5, 22)),
    ('>Date:</span></strong>   Wednesday, Oct. 3, 2018</p>', datetime.date(2018, 10, 3)),
    ('>Date:  night Apr 1-2012</p>', datetime.date(2012, 4, 1)),
    ('>Date:  feb. 2 2018</p>', datetime.date(2018, 2, 2)),
    ('>Date:  10-1-17</p>', datetime.date(2017, 10, 1)),
    ('>Date:  Morning of 2,2,19 </p>', datetime.date(2019, 2, 2)),
    ('>Date:  3/3/19</p>', datetime.date(2019, 3, 3)),
    ('', None),
    ('>Date: Afternoon</p>', None),
))
def test_parse_date_field_00(input_, expected):
    """Ensure a date field gets parsed correctly."""
    actual = apd.parse_date_field(input_)
    assert actual == expected


@pytest.mark.parametrize('input_,expected', (
    (pytest.param('<p>	<strong>Deceased: </strong> Luis Fernando Martinez-Vertiz | Hispanic male | 04/03/1994</p>',
                  'Luis Fernando Martinez-Vertiz | Hispanic male | 04/03/1994',
                  id="p, strong, pipes")),
    (pytest.param('<p>	<strong>Deceased: </strong> Cecil Wade Walker, White male, D.O.B. 3-7-70</p>',
                  'Cecil Wade Walker, White male, D.O.B. 3-7-70',
                  id="p, strong, commas")),
    (pytest.param(
        '<p style="margin-left:.25in;">'
        '<strong>Deceased:&nbsp;</strong> Halbert Glen Hendricks | Black male | 9-24-78</p>',
        'Halbert Glen Hendricks | Black male | 9-24-78',
        id="p with style, strong, pipes")),
    (pytest.param('', '', id="Deceased tag not found")),
    (pytest.param(
        '<p>	<strong>Deceased:&nbsp; </strong>Hispanic male, 19 years of age<br>'
        '&nbsp;<br>'
        'The preliminary investigation revealed that a 2016, black Toyota 4Runner was exiting a private driveway at '
        '8000 W. Hwy. 290. Signs are posted for right turn only and the driver of the 4Runner failed to comply and '
        'made a left turn. A 2008, gray Ford Mustang was traveling westbound in the inside lane and attempted to avoid '
        'the 4Runner but struck its front end. The Mustang continued into eastbound lanes of traffic and was struck by '
        'a 2013, maroon Dodge Ram.<br>'
        '&nbsp;<br>'
        'The driver of the Mustang was pronounced deceased at the scene.<br>'
        '&nbsp;<br>'
        'Anyone with information regarding this case should call APD’s Vehicular Homicide Unit Detectives at '
        '(512) 974-6935. You can also submit tips by downloading APD’s mobile app, Austin PD, for free on '
        '<a href="https://austintexas.us5.list-manage.com/track/click?u=1861810ce1dca1a4c1673747c&amp;'
        'id=26ced4f341&amp;e=bcdeacc118">iPhone</a> and <a href="https://austintexas.us5.list-manage.com/track/click'
        '?u=1861810ce1dca1a4c1673747c&amp;id=3abaf7d912&amp;e=bcdeacc118">Android</a>.&nbsp;</p>',
        'Hispanic male, 19 years of age',
        id='XX years of age of age format + included in notes paragraph')),
    (pytest.param(
        '<p>	<strong><span style="font-family: &quot;Verdana&quot;,sans-serif;">Deceased:</span></strong>&nbsp; '
        '&nbsp;Ann Bottenfield-Seago, White female, DOB 02/15/1960<br>'
        '&nbsp;<br>'
        'The preliminary investigation shows that the grey, 2003 Volkwagen Jetta being driven by '
        'Ann Bottenfield-Seago failed to yield at a stop sign while attempting to turn westbound on to West William '
        'Cannon Drive from Ridge Oak Road. The Jetta collided with a black, 2017 Chevrolet truck that was eastbound in '
        'the inside lane of West William Cannon Drive. Bottenfield-Seago was pronounced deceased at the scene. The '
        'passenger in the Jetta and the driver of the truck were both transported to a local hospital with non-life '
        'threatening injuries. No charges are expected to be filed.<br>'
        '&nbsp;<br>'
        'APD is investigating this case. Anyone with information regarding this case should call APD’s Vehicular '
        'Homicide Unit Detectives at (512) 974-3761. You can also submit tips by downloading APD’s mobile app, '
        'Austin PD, for free on <a href="https://austintexas.us5.list-manage.com/track/click?'
        'u=1861810ce1dca1a4c1673747c&amp;id=d8c2ad5a29&amp;e=bcdeacc118"><span style="color: rgb(197, 46, 38); '
        'text-decoration: none; text-underline: none;">iPhone</span></a> and '
        '<a href="https://austintexas.us5.list-manage.com/track/click?'
        'u=1861810ce1dca1a4c1673747c&amp;id=5fcb8ff99e&amp;e=bcdeacc118"><span style="color: rgb(197, 46, 38); '
        'text-decoration: none; text-underline: none;">Android</span></a>.<br>'
        '&nbsp;<br>'
        'This is Austin’s second fatal traffic crash of 2018, resulting&nbsp;in two fatalities this year. At this time '
        'in 2018, there were two fatal traffic crashes and three traffic fatalities.<br>'
        '&nbsp;<br><strong><i><span style="font-family: &quot;Verdana&quot;,sans-serif;">These statements are based '
        'on the initial assessment of the fatal crash and investigation is still pending. Fatality information may '
        'change.</span></i></strong></p>',
        'Ann Bottenfield-Seago, White female, DOB 02/15/1960',
        id='included in notes paragraph')),
    (pytest.param(
        '<p>	<strong>Deceased:   </strong>David John Medrano,<strong> </strong>Hispanic male, D.O.B. 6-9-70</p>',
        'David John Medrano, Hispanic male, D.O.B. 6-9-70',
        id='stray strong in the middle')),
))
def test_parse_deceased_field_00(input_, expected):
    """Ensure the deceased field gets parsed correctly."""
    field = apd.to_soup(input_)
    _, deceased_str = apd.parse_deceased_field(field)
    assert deceased_str == expected


@pytest.mark.parametrize('input_,expected', (
    (
        {
            'Time': 345
        },
        {
            'Time': 345
        },
    ),
    (
        {
            'Time': ['123', '345']
        },
        {
            'Time': '123 345'
        },
    ),
    (
        {
            'Time': ' '
        },
        {},
    ),
    (
        {
            'Time': None
        },
        {},
    ),
))
def test_sanitize_fatality_entity(input_, expected):
    """Ensure field values are sanitized."""
    actual = apd.sanitize_fatality_entity(input_)
    assert actual == expected


@pytest.mark.parametrize('input_,expected', (
    (
        '>Location:</span></strong>     West William Cannon Drive and Ridge Oak Road</p>',
        'West William Cannon Drive and Ridge Oak Road',
    ),
    (
        '>Location:</strong>     183 service road westbound and Payton Gin Rd.</p>',
        '183 service road westbound and Payton Gin Rd.',
    ),
    (
        '<p>	<strong>Location:  </strong>8900 block of N Capital of Texas Highway   </p>',
        '8900 block of N Capital of Texas Highway   ',
    ),
))
def test_parse_location_field_00(input_, expected):
    """Ensure."""
    actual = apd.parse_location_field(input_)
    assert actual == expected
