"""Test the APD module."""
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
from scrapd.core import article
from tests.test_common import load_dumped_page
from tests.test_common import load_test_page
from tests.test_common import TEST_DATA_DIR

# Disable logging for the tests.
logger.remove()

# Set faker object.
fake = Faker()


@pytest.fixture
def news_page(scope='session'):
    """Returns the test news page."""
    page_fd = TEST_DATA_DIR / 'news_page.html'
    return page_fd.read_text()


@pytest.mark.parametrize(
    'input_,expected',
    [
        pytest.param(
            load_test_page('296'),
            [
                ('/news/fatality-crash-20-2', '20', '2'),
                ('/news/fatality-crash-17-2', '17', '2'),
                ('/news/fatality-crash-18-2', '18', '2'),
                ('/news/fatality-crash-19-3', '19', '3'),
                ('/news/fatality-crash-15-2', '15', '2'),
                ('/news/fatality-crash-16-2', '16', '2'),
            ],
            id='news-page-0',
        ),
        pytest.param(
            load_test_page('296-page=2'),
            [
                ('/news/fatality-crash-4-1', '4', '1'),
                ('/news/fatality-crash-3-2', '3', '2'),
                ('/news/fatality-crash-1-2', '1', '2'),
                ('/news/fatality-crash-2-2', '2', '2'),
                ('/news/traffic-fatality-86', '86'),
                ('/news/traffic-fatality-85', '85'),
                ('/news/traffic-fatality-84', '84'),
            ],
            id='news-page-2',
        ),
        pytest.param(
            load_test_page('296-page=3'),
            [
                ('/news/traffic-fatality-83', '83'),
                ('/news/traffic-fatality-82', '82'),
                ('/news/traffic-fatality-81', '81'),
                ('/news/traffic-fatality-80-0', '80', '-0'),
                ('/news/traffic-fatality-79-0', '79', '-0'),
                ('/news/traffic-fatality-77-1', '77', '-1'),
                ('/news/traffic-fatality-78-0', '78', '-0'),
                ('/news/traffic-fatality-75-0', '75', '-0'),
                ('/news/traffic-fatality-76-0', '76', '-0'),
            ],
            id='news-page-3',
        ),
    ],
)
def test_extract_traffic_fatalities_page_details_link_00(input_, expected):
    """Ensure page detail links are extracted from news page."""
    actual = apd.extract_traffic_fatalities_page_details_link(input_)
    assert actual == expected


def test_extract_traffic_fatalities_page_details_link_01():
    """Ensure page detail links are extracted from news page."""
    news_page = """
    <div class="views-field views-field-title">
        <span class="field-content">
            <a href="/news/fatality-crash-20-2" hreflang="en">Fatality Crash #20</a>
        </span>
    </div>
    """
    actual = apd.extract_traffic_fatalities_page_details_link(news_page)
    expected = [('/news/fatality-crash-20-2', '20')]
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
    ((
        '<li class="pager__item pager__item--next">'
        '<a href="?page=1" title="Go to next page" rel="next">'
        '<span class="visually-hidden">Next page</span>'
        '<span aria-hidden="true">››</span>'
        '</a>'
        '</li>',
        True,
    ), ),
)
def test_has_next_02(input_, expected):
    """Ensure we detect whether there are more news pages."""
    assert apd.has_next(input_) == expected


@asynctest.patch("scrapd.core.apd.fetch_news_page",
                 side_effect=[load_test_page(page) for page in ['296', '296-page=1', '296-page=27']])
@asynctest.patch("scrapd.core.apd.fetch_detail_page", return_value=load_test_page('fatality-crash-20-2'))
@pytest.mark.asyncio
async def test_date_filtering_00(fake_details, fake_news):
    """Ensure the date filtering do not fetch unnecessary data."""
    expected = 2
    data, actual = await apd.async_retrieve(pages=-1, from_="2050-01-02", to="2050-01-03")
    assert actual == expected
    assert isinstance(data, list)


@asynctest.patch("scrapd.core.apd.fetch_news_page",
                 side_effect=[load_test_page(page) for page in ['296', '296-page=1', '296-page=27']])
@asynctest.patch("scrapd.core.apd.fetch_detail_page", return_value=load_test_page('fatality-crash-20-2'))
@pytest.mark.asyncio
async def test_date_filtering_01(fake_details, fake_news):
    """Ensure the date filtering do not fetch unnecessary data."""
    data, _ = await apd.async_retrieve(pages=-5, from_="2019-01-02", to="2019-01-03")
    assert isinstance(data, list)


@asynctest.patch("scrapd.core.apd.fetch_news_page",
                 side_effect=[load_test_page(page) for page in ['296', '296-page=1', '296-page=27']])
@asynctest.patch(
    "scrapd.core.apd.fetch_detail_page",
    side_effect=[load_test_page(page) for page in ['traffic-fatality-2-3'] + ['traffic-fatality-71-2'] * 25])
@pytest.mark.asyncio
async def test_date_filtering_02(fake_details, fake_news):
    """Ensure the date filtering do not fetch unnecessary data."""
    data, page_count = await apd.async_retrieve(from_="2019-01-16", to="2019-01-16")
    assert isinstance(data, list)
    assert len(data) == 1
    assert page_count == 2


@asynctest.patch("scrapd.core.apd.fetch_news_page",
                 side_effect=[load_test_page(page) for page in ['296', '296-page=1', '296-page=27']])
@asynctest.patch("scrapd.core.apd.fetch_detail_page", side_effect=[load_test_page('traffic-fatality-50-3')] * 20)
@pytest.mark.asyncio
async def test_both_fatalities_from_one_incident(fake_details, fake_news):
    data, _ = await apd.async_retrieve(pages=-1, from_="2019-08-16", to="2019-08-18", attempts=1, backoff=1)
    assert isinstance(data, list)
    assert len(data) == 1
    assert len(data[0].fatalities) == 2
    assert data[0].fatalities[0].age == 36
    assert data[0].fatalities[1].age == 27


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


@asynctest.patch("scrapd.core.apd.fetch_detail_page", return_value='')
@pytest.mark.asyncio
async def test_fetch_and_parse_00(empty_page):
    """Ensure an empty page raises an exception."""
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


@asynctest.patch("scrapd.core.apd.fetch_detail_page", return_value='Not empty page')
@pytest.mark.asyncio
async def test_fetch_and_parse_01(page, mocker):
    """Ensure a page that cannot be parsed returns an exception."""
    mocker.patch("scrapd.core.apd.parse_page", return_value={})
    with pytest.raises(RetryError):
        apd.fetch_and_parse.retry.stop = stop_after_attempt(1)
        await apd.fetch_and_parse(None, 'url')


@pytest.mark.parametrize('page_dump', [
    pytest.param('traffic-fatality-1-2', id='dumped'),
])
@pytest.mark.dump
def test_dumped_page(page_dump):
    """
    Helper test to allow debugging offline.

    Run the following command: `pytest -s -n0 -x -vvv -m dump`
    """
    try:
        page = load_dumped_page(page_dump)
    except FileNotFoundError:
        raise FileNotFoundError(f'Dump file "{page_dump}" not found: run "scrapd --dump" first.')
    else:
        twitter_report, twitter_err = twitter.parse(page)
        assert not twitter_err
        article_report, artricle_err = article.parse_content(page)
        assert not artricle_err
