"""Define the module containing the function used to scrap data from the APD website."""
import asyncio
import csv
import re
import unicodedata
from urllib.parse import urljoin

import aiohttp
import dateparser
from loguru import logger
from lxml import html

from scrapd.core.constant import Fields

APD_URL = 'http://austintexas.gov/department/news/296'
PAGE_DETAILS_URL = 'http://austintexas.gov/news/'


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
    async with session.get(url, params=params) as response:
        return await response.text()


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


def extract_traffic_fatalities_page_details_link(news_page):
    """
    Extract the fatality detail page links from the news page.

    :param str news_page: html content of the new pages
    :return: a list of links.
    :rtype: list or `None`
    """
    PATTERN = r'<a href="(/news/traffic-fatality-\d{1,3}-\d)">(Traffic Fatality #(\d{1,3}))</a>'
    regex = re.compile(PATTERN)
    matches = regex.findall(news_page, re.MULTILINE)
    return matches


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
    :return: `True` if there is another news page available, `False otherwise.
    :rtype: bool
    """

    NEXT_XPATH = '/html/body/div[3]/div[2]/div[2]/div[2]/div/div/div/div/div[2]/div[3]/div/div/div/div[3]/ul/li[3]/a'
    root = html.fromstring(news_page)
    elements = root.xpath(NEXT_XPATH)
    return bool(elements)


def parse_twitter_title(twitter_title):
    """
    Parse the Twitter tittle metadata.

    :param str twitter_title: Twitter tittle embedded in the fatality details page
    :return: A dictionary containing the 'Fatal crashes this year' field.
    :rtype: dict
    """
    d = {}

    # Extract the fatality number from the title.
    match = re.search(r'\d{1,3}', twitter_title)
    if match:
        d['Fatal crashes this year'] = match.group()

    return d


def parse_twitter_description(twitter_description):
    """
    Parse the Twitter description metadata.

    The Twitter description contains all the information that we need, and even though it is still unstructured data,
    it is easier to parse than the data from the detail page.

    :param str twitter_description: Twitter description embedded in the fatality details page
    :return: A dictionary containing the details information about the fatality.
    :rtype: dict
    """
    current_field = None
    d = {}

    # Split the description to be able to parse it.
    description_words = twitter_description.split()
    for word in description_words:
        # A word ending with a colon (':') is considered a field.
        if word.endswith(':'):
            current_field = word.replace(':', '')
            continue
        d.setdefault(current_field, []).append(word)

    # Parse the Deceased field.
    if d.get('Deceased'):
        d.update(parse_deaceased_field(d.get('Deceased')))

    # Compute the victim's age.
    if d.get(Fields.DATE) and d.get(Fields.DOB):
        d[Fields.AGE] = compute_age(' '.join(d.get(Fields.DATE)), d.get(Fields.DOB))

    return sanitize_fatality_entity(d)


def compute_age(date, dob):
    """
    Compute a victim's age.

    :param str date: crash date
    :param str dob: date of birth
    :return: the victim's age.
    :rtype: int
    """
    DAYS_IN_YEAR = 365
    return (dateparser.parse(date) - dateparser.parse(dob)).days // DAYS_IN_YEAR


def sanitize_fatality_entity(d):
    """
    Clean up a fatality entity.

    Ensures that the values are all strings and removes the 'Deceased' field which does not contain
    relevant information anymore.

    :param dict d: the fatality to sanatize
    :return: A dictionary containing the details information about the fatality with sanitized entries.
    :rtype: dict
    """
    for k, v in d.items():
        if isinstance(v, list):
            d[k] = ' '.join(v)
    if d.get('Deceased'):
        del d['Deceased']

    return d


def parse_deaceased_field(deceased_field):
    """
    Parse the deceased field.

    At this point the deceased field, if it exists, is garbage as it contains First Name, Last Name, Ethnicity,
    Gender, D.O.B. and Notes. We need to explode this data into the appropriate fields.

    :param list deceased_field: a list where each item is a word from the deceased field
    :return: a dictionary representing a deceased field.
    :rtype: dict
    """
    d = {}
    try:
        dob_index = deceased_field.index(Fields.DOB)
    except ValueError:
        pass
    else:
        d[Fields.DOB] = deceased_field[dob_index + 1]
        d[Fields.NOTES] = ' '.join(deceased_field[dob_index + 2:])

        # `fleg` stands for First, Last, Ethnicity, Gender. It represents the info stored before the DOB.
        fleg = deceased_field[:dob_index]
        d[Fields.GENDER] = fleg.pop().replace(',', '')
        d[Fields.ETHNICITY] = fleg.pop().replace(',', '')
        d[Fields.LAST_NAME] = fleg.pop().replace(',', '')
        d[Fields.FIRST_NAME] = fleg.pop().replace(',', '')

    return d


def parse_detail_page(detail_page):
    """
    Parse the detail page to extract fatality information.

    :param str news_page: the content of the fatality page
    :return: a dictionary representing a fatality.
    :rtype: dict
    """
    d = {}
    searches = [
        (Fields.CASE, re.compile(r'Case:.*</strong>\s*([0-9\-]+)')),
        (Fields.DATE, re.compile(r'Date:.*</strong>\s*([^<]+)')),
        (Fields.TIME, re.compile(r'Time:.*</strong>\s*([^<]+)')),
        (Fields.LOCATION, re.compile(r'Location:.*</strong>\s*([^<]+)')),
        (Fields.DECEASED, re.compile(r'Deceased:.*</strong>\s*([^<]+)')),
    ]
    normalized_detail_page = unicodedata.normalize("NFKD", detail_page)
    for search in searches:
        match = re.search(search[1], normalized_detail_page)
        if match:
            d[search[0]] = match.groups()[0]

    # Parse the Deceased field.
    if d.get('Deceased'):
        d.update(parse_deaceased_field(d.get('Deceased').split()))

    # Compute the victim's age.
    if d.get(Fields.DATE) and d.get(Fields.DOB):
        d[Fields.AGE] = compute_age(d.get(Fields.DATE), d.get(Fields.DOB))

    return sanitize_fatality_entity(d)


async def parse_page_details(session, url):
    """
    Parse a details page from a URL.

    :param aiohttp.ClientSession session: aiohttp session
    :param str url: detail page URL
    :return: a dictionary representing a fatality.
    :rtype: dict
    """
    TWITTER_TITLE_XPATH = '/html/head/meta[@name="twitter:title"]'
    TWITTER_DESCRIPTION_XPATH = '/html/head/meta[@name="twitter:description"]'
    twitter_title = ''
    twitter_description = ''

    # Retrieve the page.
    page = await fetch_text(session, url)

    # Collect the elements.
    html_ = html.fromstring(page)
    elements = html_.xpath(TWITTER_TITLE_XPATH)
    if elements:
        twitter_title = elements[0].get('content')
    elements = html_.xpath(TWITTER_DESCRIPTION_XPATH)
    if elements:
        twitter_description = elements[0].get('content')

    # Parse the elements.
    title_d = parse_twitter_title(twitter_title)
    desc_d = parse_twitter_description(twitter_description)
    page_d = parse_detail_page(page)

    # Merge the results, from right to left.
    # (i.e. the rightmost object will overiide the object just before it, etc.)
    d = {**title_d, **page_d, **desc_d, Fields.LINK: url}
    return d


async def async_retrieve():
    """Retrieve fatality data."""
    res = []
    page = 1
    async with aiohttp.ClientSession() as session:
        while True:
            logger.info(f'Fetching page {page}...')
            news_page = await fetch_news_page(session, page)
            page_details_links = extract_traffic_fatalities_page_details_link(news_page)
            links = generate_detail_page_urls(page_details_links)
            tasks = [parse_page_details(session, link) for link in links]
            res += await asyncio.gather(*tasks)

            if not has_next(news_page):
                break
            # break

            page += 1

    # Write CSV file.
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
        Fields.NOTES,
        Fields.LINK,
    ]

    output = 'scrapd.csv'
    with open(output, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSVFIELDS)
        writer.writeheader()
        writer.writerows(res)

    return res
