import calendar
import re
import unicodedata

import bs4
from loguru import logger

from scrapd.core import date_utils
from scrapd.core import regex
from scrapd.core.constant import Fields


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


def parse_notes_field(soup, deceased_field_str):
    """
    Get Notes from deceased field's BeautifulSoup element.

    :param soup bs4.Beautifulsoup:
        the content of the bulletin page

    :param str deceased_field_str:
        the Deceased field, other than the Notes section, as a string

    :return: notes from the Deceased field of the APD bulletin
    :rtype: str
    """
    deceased = get_deceased_tag(soup)
    if not deceased:
        return ''
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


def get_deceased_tag(soup):
    """
    Get the tag with information about one or more deceased people.

    :param bs4.BeautifulSoup soup: the content of the bulletin page

    :return:
        the tag labeled "Deceased" in the bulletin
"""

    def starts_with_deceased(tag):
        return tag.get_text().strip().startswith("Deceased")

    return soup.find(starts_with_deceased)


def parse_deceased_field(soup):
    """
    Extract content from deceased field on the fatality page.

    :param bs4.BeautifulSoup soup: the content of the bulletin page
    :return:
        the Deceased field as a string
    :rtype: str
    """
    deceased_tag_p = get_deceased_tag(soup)

    try:
        deceased_text = deceased_tag_p.get_text()
        if len(deceased_text) < 100 and "preliminary" not in deceased_text:
            return deceased_text.split(":")[1].strip()
    except AttributeError:
        pass

    try:
        deceased_field_str = deceased_tag_p.find("strong").next_sibling.string.strip()
    except AttributeError:
        deceased_field_str = ''
    return deceased_field_str


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


def to_soup(html):
    """
    Create a beautiful soup object from a HTML string.

    :param string html: represents a HTML document
    :return: A BeautifulSoup object.
    :rtype: bs4.BeautifulSoup
    """
    soup = bs4.BeautifulSoup(html, 'html.parser')
    return soup


def parse_page_content(detail_page, notes_parsed=False):
    """
    Parse the detail page to extract fatality information.

    :param str news_page: the content of the fatality page
    :return: a dictionary representing a fatality and a list of errors.
    :rtype: dict, list
    """
    d = {}
    parsing_errors = []
    normalized_detail_page = unicodedata.normalize("NFKD", detail_page)
    soup = to_soup(normalized_detail_page)

    # Parse the `Case` field.
    d[Fields.CASE] = regex.match_case_field(normalized_detail_page)
    if not d.get(Fields.CASE):
        raise ValueError('A case number is mandatory.')

    # Parse the `Crashes` field.
    crash_str = regex.match_crashes_field(normalized_detail_page)
    if crash_str:
        d[Fields.CRASHES] = crash_str
    else:
        parsing_errors.append("could not retrieve the crash number")

    # Parse the `Date` field.
    date_field = regex.match_date_field(normalized_detail_page)
    if date_field:
        d[Fields.DATE] = date_field
    else:
        parsing_errors.append("could not retrieve the crash date")

    # Parse the `Time` field.
    time_str = regex.match_time_field(normalized_detail_page)
    time = date_utils.parse_time(time_str)
    if time:
        d[Fields.TIME] = time
    else:
        parsing_errors.append("could not retrieve the crash time")

    # Parse the location field.
    location_str = regex.match_location_field(normalized_detail_page)
    if location_str:
        d[Fields.LOCATION] = location_str
    else:
        parsing_errors.append("could not retrieve the location")

    # Parse the `Deceased` field.
    deceased_field_str = parse_deceased_field(soup)
    if deceased_field_str:
        d[Fields.DECEASED] = deceased_field_str
    else:
        parsing_errors.append("could not retrieve the deceased information")

    # Fill in Notes from Details page if not in twitter description.
    if not notes_parsed:
        notes = parse_notes_field(soup, deceased_field_str)
        if notes:
            d[Fields.NOTES] = notes
        else:
            parsing_errors.append("could not retrieve the notes information")

    r, err = common_fatality_parsing(d)
    return r, parsing_errors + err


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
        d[Fields.TIME] = date_utils.parse_time(fatality_time)

    # Handle special case where Date of birth is a token `DOB:`.
    tmp_dob = d.get(Fields.DOB)
    if tmp_dob and isinstance(tmp_dob, list):
        d[Fields.DOB] = date_utils.parse_date(tmp_dob[0])

    r, _ = common_fatality_parsing(d)
    return r


def parse_twitter_fields(page):
    """
    Parse the Twitter fields on a detail page.

    :param str page: the content of the fatality page
    :return: a dictionary representing a fatality.
    :rtype: dict
    """
    twitter_title = regex.match_twitter_title_meta(page)
    twitter_description = regex.match_twitter_description_meta(page)

    # Parse the elements.
    title_d = parse_twitter_title(twitter_title)
    desc_d = parse_twitter_description(twitter_description)
    d = {**title_d, **desc_d}
    return d


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
    match = regex.match_crashes_field(twitter_title)
    if match:
        d[Fields.CRASHES] = match

    return d


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
