"""Define the module containing the function used to scrap data from the APD website."""
import asyncio
from pathlib import Path
import re
from urllib.parse import urljoin

import aiohttp
from loguru import logger
from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_exponential

from scrapd.core import article
from scrapd.core import constant
from scrapd.core import date_utils
from scrapd.core import model
from scrapd.core.regex import match_pattern

APD_URL = 'http://austintexas.gov/department/news/296'
PAGE_DETAILS_URL = 'http://austintexas.gov/'


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=3), reraise=True)
async def fetch_text(session, url, params=None):
    """
    Fetch the data from a URL as text.

    :param aiohttp.ClientSession session: aiohttp session
    :param str url: request URL
    :param dict params: request paramemters, defaults to None
    :return: the data from a URL as text.
    :rtype: str
    """
    if not params:
        params = {}
    try:
        async with session.get(url, params=params) as response:
            logger.debug(response.url)
            return await response.text()
    except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
    ) as e:
        logger.error(f'aiohttp exception for {url} -> {e}')
        raise e


async def fetch_news_page(session, page=1):
    """
    Fetch the content of a specific news page from the APD website.

    The page number starts at 1.

    :param aiohttp.ClientSession session: aiohttp session
    :param int page: page number to fetch, defaults to 1
    :return: the page content.
    :rtype: str
    """
    params = {}
    if page > 1:
        params['page'] = page - 1
    return await fetch_text(session, APD_URL, params)


async def fetch_detail_page(session, url):
    """
    Fetch the content of a detail page.

    :param aiohttp.ClientSession session: aiohttp session
    :param str url: request URL
    :return: the page content.
    :rtype: str
    """
    return await fetch_text(session, url)


def extract_traffic_fatalities_page_details_link(news_page):
    """
    Extract the fatality detail page links from the news page.

    :param str news_page: html content of the new pages
    :return: a list of links.
    :rtype: list or `None`
    """
    regex = re.compile(
        r'''
        (?:
            (/news/traffic-fatality-(\d{1,3})(?:-(\d?|[a-z]+))?)\"
            |
            (/news/fatality-crash-(\d{1,3})-(\d))
        )
        ''',
        re.VERBOSE | re.MULTILINE,
    )
    matches = regex.findall(news_page, re.MULTILINE)
    compact_matches = []
    for match in matches:
        parts = tuple(part for part in match if part != '')
        compact_matches.append(parts)
    return compact_matches


def generate_detail_page_urls(titles):
    """
    Generate the full URLs of the fatality detail pages.

    :param list titles: a list of partial link
    :return: a list of full links to the fatality detail pages.
    :rtype: list
    """
    return [urljoin(PAGE_DETAILS_URL, title[0]) for title in titles]


def has_next(news_page):
    """
    Return `True` if there is another news page available.

    :param str news_page: the news page to parse
    :return: `True` if there is another news page available, `False` otherwise.
    :rtype: bool
    """
    if not news_page:
        return False

    pattern = re.compile(
        r'''
        <span\saria-hidden=\"true\">
        (››)                        # Test indicating a next page
        </span>
        ''',
        re.VERBOSE | re.MULTILINE,
    )
    element = match_pattern(news_page, pattern)
    return bool(element)


def parse_page(page, url, dump=False):
    """
    Parse the page using all parsing methods available.

    :param str page: the content of the fatality page
    :param str url: detail page URL
    :return: a dictionary representing a fatality.
    :rtype: dict
    """
    report = model.Report(case='19-123456')

    # Parse the page.
    article_report, artricle_err = article.parse_content(page)
    report.update(article_report)
    if artricle_err:  # pragma: no cover
        article_err_str = f'\nArticle fields:\n\t * ' + "\n\t * ".join(artricle_err) if artricle_err else ''
        logger.debug(f'Errors while parsing {url}:{article_err_str}')

        # Dump the file.
        if dump:
            dumpr_dir = Path(constant.DUMP_DIR)
            dumpr_dir.mkdir(parents=True, exist_ok=True)
            dump_file_name = url.split('/')[-1]
            dump_file = dumpr_dir / dump_file_name
            dump_file.write_text(page)

    return report


@retry()
async def fetch_and_parse(session, url, dump=False):
    """
    Parse a fatality page from a URL.

    :param aiohttp.ClientSession session: aiohttp session
    :param str url: detail page URL
    :return: a dictionary representing a fatality.
    :rtype: dict
    """
    # Retrieve the page.
    page = await fetch_detail_page(session, url)
    if not page:
        raise ValueError(f'The URL {url} returned a 0-length content.')

    # Parse it.
    report = parse_page(page, url, dump)
    if not report:
        raise ValueError(f'No data could be extracted from the page {url}.')

    # Add the report link.
    report.link = url

    return report


async def async_retrieve(pages=-1, from_=None, to=None, attempts=1, backoff=1, dump=False):
    """
    Retrieve fatality data.

    :param str pages: number of pages to retrieve or -1 for all
    :param str from_: the start date
    :param str to: the end date
    :param int attempts: number of attempts per report
    :param int backoff: initial backoff time (second)
    :param bool dump: dump reports with parsing issues
    :return: the list of fatalities and the number of pages that were read.
    :rtype: tuple
    """
    res = {}
    page = 1
    has_entries = False
    no_date_within_range_count = 0
    from_date = date_utils.from_date(from_)
    to_date = date_utils.to_date(to)

    logger.debug(f'Retrieving fatalities from {from_date} to {to_date}.')

    async with aiohttp.ClientSession() as session:
        while True:
            # Fetch the news page.
            logger.info(f'Fetching page {page}...')
            try:
                news_page = await fetch_news_page(session, page)
            except Exception:
                raise ValueError(f'Cannot retrieve news page #{page}.')

            # Looks for traffic fatality links.
            page_details_links = extract_traffic_fatalities_page_details_link(news_page)

            # Generate the full URL for the links.
            links = generate_detail_page_urls(page_details_links)
            logger.debug(f'{len(links)} fatality page(s) to process.')

            # Fetch and parse each link.
            tasks = [
                fetch_and_parse.retry_with(
                    stop=stop_after_attempt(attempts),
                    wait=wait_exponential(multiplier=backoff),
                    reraise=True,
                )(session, link, dump) for link in links
            ]
            page_res = await asyncio.gather(*tasks)

            if page_res:
                # If the page contains fatalities, ensure all of them happened within the specified time range.
                entries_in_time_range = [
                    entry for entry in page_res if date_utils.is_between(entry.date, from_date, to_date)
                ]

                # If 2 pages in a row:
                #   1) contain results
                #   2) but none of them contain dates within the time range
                #   3) and we did not collect any valid entries
                # Then we can stop the operation.
                past_entries = all([date_utils.is_before(entry.date, from_date) for entry in page_res])
                if from_ and past_entries and not has_entries:
                    no_date_within_range_count += 1
                if no_date_within_range_count > 1:
                    logger.debug(f'{len(entries_in_time_range)} fatality page(s) within the specified time range.')
                    break

                # Check whether we found entries in the previous pages.
                if not has_entries:
                    has_entries = not has_entries and bool(entries_in_time_range)
                logger.debug(f'{len(entries_in_time_range)} fatality page(s) is/are within the specified time range.')

                # If there are none in range, we do not need to search further, and we can discard the results.
                if has_entries and not entries_in_time_range:
                    logger.debug(f'There are no data within the specified time range on page {page}.')
                    break

                # Store the results if the ID number is new.
                res.update({entry.case: entry for entry in entries_in_time_range if entry.case not in res})

            # Stop if there is no further pages.
            if not has_next(news_page) or page >= pages > 0:
                break

            page += 1

    return list(res.values()), page
