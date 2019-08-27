"""Functions with regex patterns for parsing APD crash bulletins."""

import re

from dateparser.search import search_dates


def match_twitter_title_meta(page):
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


def match_twitter_description_meta(page):
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


def match_location_field(page):
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


def match_time_field(page):
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
    return match_pattern(page, time_pattern)


def match_case_field(page):
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


def match_crashes_field(page):
    """
    Extract the crash number from the content of the fatality page.

    :param str page: the content of the fatality page
    :return: a string representing the crash number.
    :rtype: str
    """
    crashes_pattern = re.compile(r'Traffic Fatality #(\d{1,3})')
    return match_pattern(page, crashes_pattern)


def match_date_field(page):
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
