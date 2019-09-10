"""Parsing functions for Austin Police Department bulletins about fatal collisions."""

import re
import unicodedata

import bs4
from loguru import logger

from scrapd.core import date_utils
from scrapd.core import person
from scrapd.core import regex
from scrapd.core.constant import Fields


def get_deceased_tag(soup):
    """
    Get the tag with information about one or more deceased people.

    :param bs4.BeautifulSoup soup: the content of the bulletin page

    :return:
        the tag labeled "Deceased" in the bulletin
    """

    def starts_with_deceased(tag):
        return tag.get_text().strip().startswith("Deceased")

    answers = []
    first = soup.find(starts_with_deceased)
    if first:
        answers = [first]
        for next_tag in first.find_next_siblings(starts_with_deceased):
            answers.append(next_tag)
    return answers


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
    deceased = get_deceased_tag(soup)[-1]
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

    :param str page: the content of the fatality page
    :param str url: detail page URL
    :return: a dictionary representing a fatality.
    :rtype: dict
    """
    # Parse the page.
    twitter_d = parse_twitter_fields(page)
    page_d, err = parse_page_content(page, bool(twitter_d.get(Fields.NOTES)))

    deceased_people = person.parse_people(people=page_d.get(Fields.DECEASED) or twitter_d.get(Fields.DECEASED),
                                          birth_date=twitter_d.get(Fields.DOB) or page_d.get(Fields.DOB),
                                          collision_date=twitter_d.get(Fields.DATE) or page_d.get(Fields.DATE))

    for person_d, parsing_errors in deceased_people:
        # Merge the results, from right to left.
        # (i.e. the rightmost object will override the object just before it, etc.)
        d = {**page_d, **twitter_d, **person_d}
        err = err + parsing_errors
        if err:
            logger.debug(f'Fatality report {url} was not parsed correctly:\n\t * ' + '\n\t * '.join(err))

        # We needed the deceased field to be in the return value of parse_page_content for testing.
        # But now we can delete it.
        if d.get('Deceased'):
            del d['Deceased']

        d = sanitize_fatality_entity(d)
        yield d


def to_soup(html):
    """
    Create a beautiful soup object from a HTML string.

    :param string html: represents a HTML document
    :return: A BeautifulSoup object.
    :rtype: bs4.BeautifulSoup
    """
    soup = bs4.BeautifulSoup(html, 'html.parser')
    return soup


def parse_deceased_tag(deceased_tag_p):
    """
    Find the part of the relevant HTML tag with the text of a Deceased record.

    :param bs4.tag deceased_tag_p: HTML tag starting with "Deceased"

    :return: the part of the tag's text with Name, Ethnicity, and DOB.
    :rtype str:
    """

    deceased_text = deceased_tag_p.get_text()
    if 20 < len(deceased_text) < 100 and "preliminary" not in deceased_text:
        return re.split(r'Deceased(?: \d)?:', deceased_text, maxsplit=1)[1].strip()

    deceased_field_str = ''
    starting_tag = deceased_tag_p.find("strong")
    if not starting_tag:
        starting_tag = deceased_tag_p
    for passage in starting_tag.next_siblings:
        if not passage.string:
            continue
        if "preliminary" in passage:
            break
        deceased_field_str += passage.string

    return deceased_field_str.strip()


def split_on_dates(entry):
    """
    Use dates to determine if a Deceased field refers to multiple people.

    If more than one date appears, the entry is split into multiple
    Deceased fields, each ending with a date, which is presumably the
    date of birth.

    :param entry:
        a candidate Deceased field

    :return: one or more Deceased fields
    :rtype list:
    """
    date_regex = r'\d\/\d{1,2}\/\d{4}'
    date_split_regex = r'(?<=\d\/\d{2}\/\d{4})\s'

    date_occurences = len(re.findall(date_regex, entry))
    if date_occurences > 1:
        return re.split(date_split_regex, entry)[:date_occurences]
    return [entry]


def parse_deceased_field(soup):
    """
    Extract content from deceased field on the fatality page.

    :param bs4.BeautifulSoup soup: the content of the bulletin page
    :return:
        the Deceased field as a string
    :rtype: str
    """
    deceased_tag_p = get_deceased_tag(soup)

    deceased_fields = [parse_deceased_tag(tag) for tag in deceased_tag_p]
    flattened_list = [deceased for entry in deceased_fields for deceased in split_on_dates(entry)]
    return flattened_list


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
    soup = to_soup(normalized_detail_page.replace("<br>", "</br>"))

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
    deceased_field_list = parse_deceased_field(soup)
    if deceased_field_list:
        d[Fields.DECEASED] = deceased_field_list
    else:
        parsing_errors.append("could not retrieve the deceased information")

    # Fill in Notes from Details page if not in twitter description.
    if deceased_field_list and not notes_parsed:
        notes = parse_notes_field(soup, d[Fields.DECEASED][-1])
        if notes:
            d[Fields.NOTES] = notes
    if not d.get(Fields.NOTES):
        parsing_errors.append("could not retrieve the notes information")

    return d, parsing_errors


def twitter_deceased_field_to_list(deceased_field):
    """
    Convert a string Deceased field to a list of items about deceased people.

    Relies on the field containing "Deceased 1", "Deceased 2", etc. between
    the mentions of individuals.

    :param deceased_field:
        a string representing the Deceased field from a Twitter summary of an
        APD traffit fatality bulletin

    :return:
        a list of strings describing individuals from the Deceased field

    :rtype: list
    """
    if "Deceased" in deceased_field:
        return deceased_field.split("Deceased")
    return [deceased_field]


def twitter_description_to_dict(twitter_description):
    """
    Convert text of twitter_description field to a dict with string values.

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
    expected_headings = {"Age", "Case", "Date", "Deceased", "DOB", "D.O.B.", "Location", "Time", "Notes"}
    for word in description_words:
        if word.strip(":") in expected_headings:
            current_field = word.strip(":")
            expected_headings.remove(word.strip(":"))
            continue
        if word == 'preliminary':
            current_field = 'Notes'
            word = 'The preliminary'
        if word.endswith(":") or not current_field:
            continue
        if d.get(current_field):
            d[current_field] = d[current_field] + f" {word}"
        else:
            d[current_field] = word

    if d.get("Deceased"):
        d["Deceased"] = twitter_deceased_field_to_list(d["Deceased"])

    if d.get("D.O.B."):
        d["DOB"] = d.pop("D.O.B.")
    return d


def parse_twitter_description(twitter_description):
    """
    Convert text of twitter_description field to a dict with list and datetime values.

    The Twitter description sometimes contains all the information that we need,
    but sometimes doesn't have the deceased person's name.
    Even though it is still unstructured data, it sometimes is easier
    to parse than the data from the detail page.

    :param str twitter_description: Twitter description embedded in the fatality details page
    :return: A dictionary containing the details information about the fatality.
    :rtype: dict
    """
    d = twitter_description_to_dict(twitter_description)

    # Parse the `Date` field.
    fatality_date = d.get(Fields.DATE)
    if fatality_date:

        # Turn it into a date object.
        d[Fields.DATE] = date_utils.parse_date(fatality_date)

    # Convert the time to a time object.
    fatality_time = d.get(Fields.TIME)
    if fatality_time:
        d[Fields.TIME] = date_utils.parse_time(fatality_time)

    # Handle special case where Date of birth is a token `DOB:`.
    tmp_dob = d.get(Fields.DOB)
    if tmp_dob:
        try:
            d[Fields.DOB] = date_utils.parse_date(tmp_dob)
        except ValueError:
            d[Fields.DOB] = date_utils.parse_date(tmp_dob.split()[0])

    return d


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
    Parse the Twitter title metadata.

    :param str twitter_title: Twitter title embedded in the fatality details page
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
