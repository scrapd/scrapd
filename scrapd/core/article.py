"""Manage the parsing of the press release article."""
import re
import unicodedata

import bs4

from scrapd.core import date_utils
from scrapd.core import deceased
from scrapd.core import model
from scrapd.core import regex
from scrapd.core.constant import Fields


def to_soup(html):
    """
    Create a beautiful soup object from a HTML string.

    :param string html: represents a HTML document
    :return: A BeautifulSoup object.
    :rtype: bs4.BeautifulSoup
    """
    soup = bs4.BeautifulSoup(html, 'html.parser')
    return soup


def get_deceased_tag(soup):
    """
    Get the tag with information about one or more deceased people.

    :param bs4.BeautifulSoup soup:
        the content of the bulletin page

    :return list:
        the tag labeled "Deceased" in the bulletin
    """

    def starts_with_deceased(tag):
        return tag.get_text().strip().startswith("Deceased")

    answers = []
    first = soup.find(starts_with_deceased)
    if not first:
        return answers

    answers = [first]
    for next_tag in first.find_next_siblings(starts_with_deceased):
        answers.append(next_tag)

    return answers


def parse_deceased_tag(deceased_tag_p):
    """
    Find the part of the relevant HTML tag with the text of a Deceased record.

    :param bs4.tag deceased_tag_p: HTML tag starting with "Deceased"

    :return: the part of the tag's text with Name, Ethnicity, and DOB.
    :rtype str:
    """
    deceased_text = deceased_tag_p.get_text()
    # NOTE(rgreinho): Where do the 20 and 100 numbers come from? There should not be magic numbers.
    if 20 < len(deceased_text) < 100 and "preliminary" not in deceased_text:
        split_text = re.split(r'Deceased(?: \d)?:', deceased_text, maxsplit=1)
        if len(split_text) > 1:
            return split_text[1].strip()

    deceased_field_str = ''
    starting_tag = deceased_tag_p.find("strong") or deceased_tag_p
    for passage in starting_tag.next_siblings:
        if not passage.string:
            continue
        if "preliminary" in passage:
            break
        if "Arrested:" in passage.string:
            break
        deceased_field_str += passage.string

    return deceased_field_str.strip()


def parse_deceased_field(soup):
    """
    Extract content from deceased field on the fatality page.

    :param bs4.BeautifulSoup soup: the content of the bulletin page
    :return:
    :rtype:
    """
    errors = []
    fatalities = []
    deceased_tags = get_deceased_tag(soup)
    for deceased_tag in deceased_tags:
        deceased_field = parse_deceased_tag(deceased_tag)
        try:
            fatality = []
            err = []
            for processed_deceased in deceased.process_deceased_field(deceased_field):
                f, e = processed_deceased
                fatality.append(f)
                err += e
        except ValueError as e:  # pragma: no cover
            errors.append(str(e))
        else:
            fatalities.extend(fatality)
            errors.extend(err)

    return fatalities, errors


def parse_content(page):
    """
    Parse the detail page to extract fatality information.

    :param str news_page: the content of the fatality page
    :return: a dictionary representing a fatality and a list of errors.
    :rtype: dict, list
    """
    d = {}
    parsing_errors = []

    # Normalize the page.
    normalized_detail_page = unicodedata.normalize("NFKD", page)

    # Parse the `Case` field.
    d[Fields.CASE] = regex.match_case_field(normalized_detail_page)
    if not d.get(Fields.CASE):
        raise ValueError('a case number is mandatory')

    # Parse the `Date` field.
    d[Fields.DATE] = regex.match_date_field(normalized_detail_page)
    if not d.get(Fields.DATE):
        raise ValueError('a date is mandatory')

    # Parse the `Crashes` field.
    crash_str = regex.match_crash_field(normalized_detail_page)
    if crash_str:
        d[Fields.CRASH] = crash_str
    else:
        parsing_errors.append("could not retrieve the crash number")

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
        d[Fields.LOCATION] = location_str.strip()
    else:
        parsing_errors.append("could not retrieve the location")

    # Convert to a report object.
    report = model.Report(**d)
    report.compute_fatalities_age()

    # Convert the page to a BeautifulSoup object.
    soup = to_soup(normalized_detail_page.replace("<br>", "</br>"))

    # Parse the `Deceased` field.
    deceased_fields, err = parse_deceased_field(soup)
    if deceased_fields:
        report.fatalities = deceased_fields
        parsing_errors.extend(err)
    else:
        parsing_errors.append("could not retrieve the deceased information")
    report.compute_fatalities_age()

    # Fill in Notes from Details page
    if deceased_fields:
        notes = parse_notes_field(soup)
        if notes:
            report.notes = notes
        else:
            parsing_errors.append("could not retrieve the notes information")

    return report, parsing_errors


def parse_notes_field(soup):
    """
    Get Notes from deceased field's BeautifulSoup element.

    :param soup bs4.Beautifulsoup: the content of the bulletin page
    :param str deceased_field_str: the Deceased field, other than the Notes section, as a string
    :return: notes from the Deceased field of the APD bulletin
    :rtype: str
    """
    deceased_tag = get_deceased_tag(soup)[-1]
    split_tag = parse_deceased_tag(deceased_tag)
    deceased_text = deceased_tag.text
    for sibling in deceased_tag.next_siblings:
        if isinstance(sibling, bs4.NavigableString):
            deceased_text += sibling
        else:
            deceased_text += sibling.text
    notes = deceased_text.split(split_tag)[1]
    if 'arrested:' in notes.lower():
        filtered_notes = [part for part in list(filter(None, notes.split('\n'))) if 'arrested:' not in part.lower()]
        if filtered_notes:
            notes = '\n'.join(filtered_notes)
        else:
            alt = [el for el in list(deceased_tag.parent.next_siblings) if isinstance(el, bs4.element.Tag)]
            notes = alt[0].text if len(alt) == 1 else ''
    if "APD is investigating this case" in notes:
        without_boilerplate = notes.split("APD is investigating this case")[0]
    else:
        without_boilerplate = notes.split("Anyone with information regarding")[0]
    return without_boilerplate.strip("()<>").strip()
