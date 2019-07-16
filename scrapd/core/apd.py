"""Define the module containing the function used to scrap data from the APD website."""
import asyncio
import calendar
import re
import unicodedata
from urllib.parse import urljoin

import aiohttp
import bs4
import dateparser
from dateparser.search import search_dates
from loguru import logger
from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_exponential

from scrapd.core.constant import Fields
from scrapd.core import date_utils

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
    PATTERN = r'<a href="(/news/traffic-fatality-\d{1,3}-\d|\S*)">(Traffic Fatality #(\d{1,3})).*\s*</a>'
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
    :return: `True` if there is another news page available, `False` otherwise.
    :rtype: bool
    """
    if not news_page:
        return False

    pattern = re.compile(
        r'''
        <a                  # Beginning of the anchor
        \s+
        title=\"[^\"]*\"    # Anchor tittle
        \s+
        href=\"[^\"]*\">    # Anchor href
        (next\s›)            # Test indicating a next page
        </a>                # End of the anchor.
        ''',
        re.VERBOSE | re.MULTILINE,
    )
    element = match_pattern(news_page, pattern)
    return bool(element)


def parse_twitter_title(twitter_title):
    """
    Parse the Twitter tittle metadata.

    :param str twitter_title: Twitter tittle embedded in the fatality details page
    :return: A dictionary containing the 'Fatal crashes this year' field.
    :rtype: dict
    """
    d = {}
    if not twitter_title:
        return d

    # Extract the fatality number from the title.
    match = parse_crashes_field(twitter_title)
    if match:
        d[Fields.CRASHES] = match

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
    d = {}
    if not twitter_description:
        return d

    # Split the description to be able to parse it.
    current_field = None
    description_words = twitter_description.split()
    for word in description_words:
        # A word ending with a colon (':') is considered a field.
        if word.endswith(':'):
            current_field = word.replace(':', '')
            continue
        if not current_field:
            continue
        d.setdefault(current_field, []).append(word)

    # Parse the `Date` field.
    fatality_date = d.get(Fields.DATE)
    if fatality_date:
        # Ensure it is a string.
        if isinstance(fatality_date, list):
            fatality_date = ' '.join(fatality_date)

        # Turn it into a date object.
        d[Fields.DATE] = date_utils.parse_date(fatality_date)

    # Convert the time to a time object.
    fatality_time = d.get(Fields.TIME)
    if fatality_time:
        # Ensure it is a string.
        if isinstance(fatality_time, list):
            fatality_time = ' '.join(fatality_time)
        dt = dateparser.parse(fatality_time)
        d[Fields.TIME] = dt.time() if dt else None

    # Handle special case where Date of birth is a token `DOB:`.
    tmp_dob = d.get(Fields.DOB)
    if tmp_dob and isinstance(tmp_dob, list):
        d[Fields.DOB] = date_utils.parse_date(tmp_dob[0])

    r, _ = common_fatality_parsing(d)
    return r


def parse_details_page_notes(details_page_notes):
    """
    Clean up a details page notes section.

    The purpose of this function is to attempt to extract the sentences about
    the crash with some level of fidelity, but does not always return
    a perfectly parsed sentence as the HTML syntax varies widely.

    :param str details_description: the paragraph after the Deceased information
    :return: A paragraph containing the details of the fatality in sentence form.
    :rtype: str
    """
    # Ideally the Notes will be contained in a paragraph tag.
    start_tag = details_page_notes.find('<p>') + len('<p>')
    end_tag = details_page_notes.find('</p>', start_tag)

    # Here .upper().isupper() tests if the substring of the
    # text passed in contains any letters. If it doesn't,
    # the Notes may be located after a <br \>.
    if not details_page_notes[start_tag:end_tag].upper().isupper():
        start_tag = details_page_notes.find(r'<br \>') + len(r'<br \>')

    snippet = details_page_notes[start_tag:end_tag]

    # Remove the end of line characters.
    squished = snippet.replace('\n', ' ')

    # Look for the first capital letter and start from there.
    first_cap = 0
    for index, c in enumerate(squished):
        if c.isupper():
            first_cap = index
            break

    # Remove HTML tags.
    no_html = re.sub(re.compile('<.*?>'), '', squished[first_cap:])

    # Remove tabs and, if subjects included, remove.
    remove_subjects = re.split(r'\s{2,}', no_html)

    # Demographic info is usually only included in subject description.
    # DOB would be better, but that is sometimes missing.
    final = ' '.join([segment for segment in remove_subjects if 'male' not in segment])

    # This phrase signals the end of a report.
    footer_string = 'Fatality information may change.'
    end_pos = final.find(footer_string)

    if end_pos != -1:
        final = final[:end_pos + len(footer_string)]

    return final


def common_fatality_parsing(d):
    """
    Perform parsing common to Twitter descriptions and page content.

    Ensures that the values are all strings and removes the 'Deceased' field which does not contain
    relevant information anymore.

    :param dict d: the fatality to finish parsing
    :return: A dictionary containing the details information about the fatality with sanitized entries.
    :rtype: dict, list
    """
    parsing_errors = []

    # Extracting other fields from 'Deceased' field.
    if d.get(Fields.DECEASED):
        try:
            d.update(process_deceased_field(d.get(Fields.DECEASED)))
        except ValueError as e:
            parsing_errors.append(str(e))

    # Compute the victim's age.
    if d.get(Fields.DATE) and d.get(Fields.DOB):
        d[Fields.AGE] = date_utils.compute_age(d.get(Fields.DATE), d.get(Fields.DOB))

    if d.get(Fields.AGE, -1) < 0:
        parsing_errors.append(f'age is invalid: {d.get(Fields.AGE)}')

    return sanitize_fatality_entity(d), parsing_errors


def sanitize_fatality_entity(d):
    """
    Clean up a fatality entity.

    :return: A dictionary containing the details information about the fatality with sanitized entries.
    :rtype: dict
    """
    # Ensure the values have the right format.
    empty_values = []
    for k, v in d.items():
        # Lists must be converted to strings.
        if isinstance(v, list):
            d[k] = ' '.join(v)

        # Strip the strings.
        if isinstance(v, str):
            d[k] = v.strip()

        # Store keys of empty values.
        if not d[k]:
            empty_values.append(k)

    # Remove empty values.
    for key in empty_values:
        del d[key]

    return d


def parse_name(name):
    """
    Parse the victim's name.

    :param list name: a list reprenting the deceased person's full name split on space characters
    :return: a dictionary representing just the victim's first and last name
    :rtype: dict
    """
    GENERATIONAL_TITLES = ['jr', 'jr.', 'sr', 'sr.']
    d = {}
    try:
        for i in range(1, len(name)):
            d["last"] = name[-i].replace(',', '')
            if d["last"].lower() not in GENERATIONAL_TITLES:
                break
        d["first"] = name[0].replace(',', '')
    except (IndexError, TypeError):
        pass
    return d


def dob_search(split_deceased_field):
    """
    Search for the DOB in a deceased field.

    :param list split_deceased_field: a list representing the deceased field
    :return: the DOB index within the split deceased field.
    :rtype: int
    """
    dob_index = -1
    dob_tokens = [Fields.DOB, '(D.O.B', '(D.O.B.', '(D.O.B:', '(DOB', '(DOB:', 'D.O.B.', 'DOB:']
    while dob_index < 0 and dob_tokens:
        dob_token = dob_tokens.pop()
        try:
            dob_index = split_deceased_field.index(dob_token)
        except ValueError:
            pass
        else:
            break

    return dob_index


def process_deceased_field(deceased_field):
    """
    Parse the deceased field.

    At this point the deceased field, if it exists, is garbage as it contains First Name, Last Name, Ethnicity,
    Gender, D.O.B. and Notes. We need to explode this data into the appropriate fields.

    :param str deceased_field: the deceased field from the fatality report
    :return: a dictionary representing a deceased field.
    :rtype: dict
    """
    if isinstance(deceased_field, list):
        deceased_field = ' '.join(deceased_field)

    # Try to parse the deceased fields when the fields are comma separated.
    try:
        return parse_comma_delimited_deceased_field(deceased_field)
    except Exception:
        pass

    # Try to parse the deceased fields when the fields are pipe separated.
    try:
        return parse_pipe_delimited_deceased_field(deceased_field)
    except Exception:
        pass

    # Try to parse the deceased fields when the fields are space separated.
    try:
        return parse_space_delimited_deceased_field(deceased_field)
    except Exception:
        pass

    # Try to parse the deceased fields assuming it contains an age.
    try:
        return parse_age_deceased_field(deceased_field)
    except Exception:
        pass

    raise ValueError(f'cannot parse {Fields.DECEASED}: {deceased_field}')


def parse_age_deceased_field(deceased_field):
    """
    Parse deceased field assuming it contains an age.

    :param str deceased_field: the deceased field
    :return: a dictionary representing the deceased field.
    :rtype: dict
    """
    age_pattern = re.compile(r'([0-9]+) years')

    # Raises AttributeError upon failure.
    age = re.search(age_pattern, deceased_field).group(1)
    split_deceased_field = age_pattern.split(deceased_field)
    d = parse_fleg(split_deceased_field[0].split())
    d[Fields.AGE] = int(age)
    return d


def parse_comma_delimited_deceased_field(deceased_field):
    """
    Parse deceased fields seperated with commas.

    :param str deceased_field: a list representing the deceased field
    :return: a dictionary representing the deceased field.
    :rtype: dict
    """
    split_deceased_field = re.split(r' |(?<=[A-Za-z])/', deceased_field)

    # Find the DOB token as we use it as a delimiter.
    dob_index = dob_search(split_deceased_field)
    if dob_index < 0:
        raise ValueError(f'Cannot find DOB in the deceased field: {deceased_field}')
    raw_dob = split_deceased_field[dob_index + 1]

    if any(raw_dob.startswith(calendar.month_abbr[month_index]) for month_index in range(1, 13)):
        raw_dob = " ".join(split_deceased_field[dob_index + 1:dob_index + 4])

    # Parse the field.
    fleg = split_deceased_field[:dob_index]
    d = parse_deceased_field_common([raw_dob], fleg)

    # Add the notes.
    notes = split_deceased_field[dob_index + 2:]
    if notes:
        d[Fields.NOTES] = ' '.join(notes)
    return d


def parse_pipe_delimited_deceased_field(deceased_field):
    """
    Parse deceased fields separated with pipes.

    :param str deceased_field: the deceased field as a string.
    :return: a dictionary representing the deceased field.
    :rtype: dict
    """
    split_deceased_field = deceased_field.split('|')
    fleg = (split_deceased_field[0] + split_deceased_field[1]).split()
    return parse_deceased_field_common(split_deceased_field, fleg)


def parse_space_delimited_deceased_field(deceased_field):
    """
    Parse deceased fields separated with spaces.

    :param str deceased_field: the deceased field as a string.
    :return: a dictionary representing the deceased field.
    :rtype: dict
    """
    split_deceased_field = re.split(r' |/', deceased_field)
    fleg = split_deceased_field[:-1]
    return parse_deceased_field_common(split_deceased_field, fleg)


def parse_deceased_field_common(split_deceased_field, fleg):
    """
    Parse the deceased field.

    :param list split_deceased_field: [description]
    :param dict fleg: a dictionary containing First, Last, Ethnicity, Gender fields
    :return: a dictionary representing the deceased field.
    :rtype: dict
    """
    # Populate FLEG.
    d = parse_fleg(fleg)

    # Extract and clean up DOB.
    raw_dob = split_deceased_field[-1].strip()
    dob_guess = date_utils.parse_date(raw_dob)
    d[Fields.DOB] = date_utils.check_dob(dob_guess)

    return d


def parse_fleg(fleg):
    """
    Parse FLEG. `fleg` stands for First, Last, Ethnicity, Gender.

    :param list fleg: values representing the fleg.
    :return: a dictionary containing First, Last, Ethnicity, Gender fields
    :rtype: dict
    """
    # Try to pop out the results one by one. If pop fails, it means there is nothing left to retrieve.
    d = {}
    try:
        d[Fields.GENDER] = fleg.pop().replace(',', '').lower()
        if d.get(Fields.GENDER, '').lower() == 'f':
            d[Fields.GENDER] = 'female'
        elif d.get(Fields.GENDER, '').lower() == 'm':
            d[Fields.GENDER] = 'male'

        d[Fields.ETHNICITY] = fleg.pop().replace(',', '')
        if d.get(Fields.ETHNICITY, '').lower() == 'w':
            d[Fields.ETHNICITY] = 'White'
        elif d.get(Fields.ETHNICITY, '').lower() == 'h':
            d[Fields.ETHNICITY] = 'Hispanic'
        elif d.get(Fields.ETHNICITY, '').lower() == 'b':
            d[Fields.ETHNICITY] = 'Black'
    except IndexError:
        pass

    name = parse_name(fleg)
    if name.get("last"):
        d[Fields.LAST_NAME] = name.get("last", '')
    if name.get("first"):
        d[Fields.FIRST_NAME] = name.get("first", '')
    return d


def notes_from_element(deceased, deceased_field_str):
    """
    Get Notes from deceased field's BeautifulSoup element.

    :param deceased bs4.Beautifulsoup.element.Tag:
        the first <p> tag of the Deceased field of the APD bulletin
    :param deceased_field_str:
        the string corresponding to the Deceased field
    :return: notes from the Deceased field of the APD bulletin
    :rtype: str
    """
    text = deceased.text
    for sibling in deceased.next_siblings:
        if isinstance(sibling, bs4.NavigableString):
            text += sibling
        else:
            text += sibling.text
    notes = text.split(deceased_field_str)[1]
    if "APD is investigating this case" in notes:
        without_boilerplate = notes.split("APD is investigating this case")[0]
    else:
        without_boilerplate = notes.split("Anyone with information regarding")[0]
    return without_boilerplate.strip("()<>").strip()


def parse_page_content(detail_page, notes_parsed=False):
    """
    Parse the detail page to extract fatality information.

    :param str news_page: the content of the fatality page
    :return: a dictionary representing a fatality.
    :rtype: dict
    """
    d = {}
    parsing_errors = []
    normalized_detail_page = unicodedata.normalize("NFKD", detail_page)
    soup = bs4.BeautifulSoup(normalized_detail_page,
                             'html.parser',
                             parse_only=bs4.SoupStrainer(property="content:encoded"))

    # Parse the `Case` field.
    d[Fields.CASE] = parse_case_field(normalized_detail_page)
    if not d.get(Fields.CASE):
        raise ValueError('A case number is mandatory.')

    # Parse the `Crashes` field.
    crash_str = parse_crashes_field(normalized_detail_page)
    if crash_str:
        d[Fields.CRASHES] = crash_str
    else:
        parsing_errors.append("could not retrieve the crash number")

    # Parse the `Date` field.
    date_field = parse_date_field(normalized_detail_page)
    if date_field:
        d[Fields.DATE] = date_field
    else:
        parsing_errors.append("could not retrieve the crash date")

    # Parse the `Deceased` field.
    deceased_tag_p, deceased_field_str = parse_deceased_field(soup)
    if deceased_field_str:
        d[Fields.DECEASED] = deceased_field_str
    else:
        parsing_errors.append("could not retrieve the deceased information")

    # Parse the `Time` field.
    time_str = parse_time_field(normalized_detail_page)
    if time_str:
        d[Fields.TIME] = time_str
    else:
        parsing_errors.append("could not retrieve the crash time")

    # Parse the location field.
    location_str = parse_location_field(normalized_detail_page)
    if location_str:
        d[Fields.LOCATION] = location_str
    else:
        parsing_errors.append("could not retrieve the location")

    # Fill in Notes from Details page if not in twitter description.
    if deceased_field_str and not notes_parsed:
        d[Fields.NOTES] = notes_from_element(deceased_tag_p, deceased_field_str)

    r, err = common_fatality_parsing(d)
    return r, parsing_errors + err


def parse_case_field(page):
    """
    Extract the case number from the content of the fatality page.

    :param str page: the content of the fatality page
    :return: a string representing the case number.
    :rtype: str
    """
    case_pattern = re.compile(
        r'''
        Case:           # The name of the field we are looking for.
        .*              # Any character.
        (\d{2}-\d{6,7}) # The case the number we are looking for.
        ''',
        re.VERBOSE,
    )
    return match_pattern(page, case_pattern)


def parse_crashes_field(page):
    """
    Extract the crash number from the content of the fatality page.

    :param str page: the content of the fatality page
    :return: a string representing the crash number.
    :rtype: str
    """
    crashes_pattern = re.compile(r'Traffic Fatality #(\d{1,3})')
    return match_pattern(page, crashes_pattern)


def parse_date_field(page):
    """
    Extract the date from the content of the fatality page.

    :param str page: the content of the fatality page
    :return: a string representing the date.
    :rtype: str
    """
    date_pattern = re.compile(
        r'''
        >Date:          # The name of the desired field.
        .*\s{2,}        # Any character and whitespace.
        (?:</strong>)?  # Non-capture (literal match).
        ([^<]*)         # Capture any character except '<'.
        <               # Non-capture (literal match)
        ''',
        re.VERBOSE,
    )
    date = match_pattern(page, date_pattern).replace('.', ' ')
    date = search_dates(date)
    return date[0][1].date() if date else None


def parse_deceased_field(soup):
    """
    Extract content from deceased field on the fatality page.

    :param bs4.BeautifulSoup soup: the content of the fatality page
    :return:
        a tuple containing the tag for the Deceased paragraph
        and the Deceased field as a string
    :rtype: tuple
    """

    def starts_with_deceased(tag):
        return tag.get_text().strip().startswith("Deceased:")

    deceased_tag_p = soup.find(starts_with_deceased)
    try:
        deceased_text = deceased_tag_p.get_text()
        if len(deceased_text) < 100 and "preliminary" not in deceased_text:
            return deceased_tag_p, deceased_text.split("Deceased:")[1].strip()
    except AttributeError:
        pass

    try:
        deceased_field_str = deceased_tag_p.find("strong").next_sibling.string.strip()
    except AttributeError:
        deceased_field_str = None
    return deceased_tag_p, deceased_field_str


def parse_time_field(page):
    """
    Extract the time from the content of the fatality page.

    :param str page: the content of the fatality page
    :return: a string representing the time.
    :rtype: str
    """
    time_pattern = re.compile(
        r'''
        Time:                             # The name of the desired field.
        (?:</strong>)?                    # Non capture closing strong tag
        \D*?                              # Any non-digit character (lazy).
        (
        (?:0?[1-9]|1[0-2]):?[0-5]?\d?     # 12h format.
        \s*                               # Any whitespace (zero-unlimited).
        [AaPp]\.?[Mm]\.?                  # AM/PM variations.
        |                                 # OR
        (?:[01]?[0-9]|2[0-3]):[0-5][0-9]  # 24h format.
        )
        ''',
        re.VERBOSE,
    )
    time = match_pattern(page, time_pattern)
    dt = dateparser.parse(time)
    return dt.time() if time else None


def parse_location_field(page):
    """
    Extract the location information from the content of the fatality page.

    :param page: the content of the fatality page
    :type page: str
    """
    location_pattern = re.compile(
        r'''
        >Location:      # The name of the desired field.
        \s*             # Any whitespace (at least 2)
        (?:</span>)?    # Non capture closing span tag
        (?:</strong>)?  # Non capture closing strong tag
        \s{2,}          # Any whitespace (at least 2)
        (?:</strong>)?  # Non capture closing strong tag
        ([^<]+)         # Capture any character except '<'.
        ''',
        re.VERBOSE,
    )
    return match_pattern(page, location_pattern)


def match_pattern(text, pattern, group_number=0):
    """
    Match a pattern.

    :param str text: the text to match the pattern against
    :param compiled regex pattern: the pattern to look for
    :param int group_number: the capturing group number
    :return: a string representing the captured group.
    :rtype: str
    """
    match = re.search(pattern, text)
    return match.groups()[group_number] if match else ''


def extract_twitter_tittle_meta(page):
    """
    Extract the twitter title from the metadata fields.

    :param str page: the content of the fatality page
    :return: a string representing the twitter tittle.
    :rtype: str
    """
    pattern = re.compile(
        r'''
        <meta
        \s+
        name=\"twitter:title\"
        \s+
        content=\"(.*)\"
        \s+
        />
        ''',
        re.VERBOSE,
    )
    return match_pattern(page, pattern)


def extract_twitter_description_meta(page):
    """
    Extract the twitter description from the metadata fields.

    :param str page: the content of the fatality page
    :return: a string representing the twitter description.
    :rtype: str
    """
    pattern = re.compile(
        r'''
        <meta
        \s+
        name=\"twitter:description\"
        \s+
        content=\"(.*)\"
        \s+
        />
        ''',
        re.VERBOSE,
    )
    return match_pattern(page, pattern)


def parse_twitter_fields(page):
    """
    Parse the Twitter fields on a detail page.

    :param str page: the content of the fatality page
    :return: a dictionary representing a fatality.
    :rtype: dict
    """
    twitter_title = extract_twitter_tittle_meta(page)
    twitter_description = extract_twitter_description_meta(page)

    # Parse the elements.
    title_d = parse_twitter_title(twitter_title)
    desc_d = parse_twitter_description(twitter_description)
    d = {**title_d, **desc_d}
    return d


def parse_page(page, url):
    """
    Parse the page using all parsing methods available.

    :param str  page: the content of the fatality page
    :param str url: detail page URL
    :return: a dictionary representing a fatality.
    :rtype: dict
    """
    # Parse the page.
    twitter_d = parse_twitter_fields(page)
    page_d, err = parse_page_content(page, bool(twitter_d.get(Fields.NOTES)))
    if err:
        logger.debug(f'Fatality report {url} was not parsed correctly:\n\t * ' + '\n\t * '.join(err))

    # Merge the results, from right to left.
    # (i.e. the rightmost object will override the object just before it, etc.)
    d = {**page_d, **twitter_d}

    # We needed the deceased field to be in the return value of parse_page_content for testing.
    # But now we can delete it.
    if d.get('Deceased'):
        del d['Deceased']

    return d


@retry()
async def fetch_and_parse(session, url):
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
    d = parse_page(page, url)
    if not d:
        raise ValueError(f'No data could be extracted from the page {url}.')

    # Add the link.
    d[Fields.LINK] = url

    # Return the result.
    return d


async def async_retrieve(pages=-1, from_=None, to=None, attempts=1, backoff=1):
    """
    Retrieve fatality data.

    :param str pages: number of pages to retrieve or -1 for all
    :param str from_: the start date
    :param str to: the end date
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
                )(session, link) for link in links
            ]
            page_res = await asyncio.gather(*tasks)

            # If the page contains fatalities, ensure all of them happened within the specified time range.
            if page_res:
                entries_in_time_range = [
                    entry for entry in page_res if date_utils.is_between(entry[Fields.DATE], from_date, to_date)
                ]

                # If 2 pages in a row:
                #   1) contain results
                #   2) but none of them contain dates within the time range
                #   3) and we did not collect any valid entries
                # Then we can stop the operation.
                past_entries = all([date_utils.is_before(entry[Fields.DATE], from_date) for entry in page_res])
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

                # Store the results if the case number is new.
                res.update({
                    entry.get(Fields.CASE): entry
                    for entry in entries_in_time_range if entry.get(Fields.CASE) not in res
                })

            # Stop if there is no further pages.
            if not has_next(news_page) or page >= pages > 0:
                break

            page += 1

    return list(res.values()), page
