"""Manage the parsing of the twitter fields."""
import re

from pydantic import ValidationError

from scrapd.core import date_utils
from scrapd.core import deceased
from scrapd.core import model
from scrapd.core import regex
from scrapd.core.constant import Fields


def match_title_meta(page):
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
    return regex.match_pattern(page, pattern)


def match_description_meta(page):
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
    return regex.match_pattern(page, pattern)


def tokenize_description(twitter_description):
    """Split the content of the description based on keywords.

    :param str twitter_description: the content of twitter description field
    :return: a dict representing the tokenized twitter description.
    :rtype: dict
    """
    d = {}
    if not twitter_description:
        return d

    # Split the description to be able to parse it.
    current_field = None
    description_words = twitter_description.split()
    expected_headings = {"Case", "Date", "Deceased", "DOB", "D.O.B.", "Location", "Time"}
    for word in description_words:
        if word.strip(":") in expected_headings:
            current_field = word.strip(":")
            expected_headings.remove(word.strip(":"))
            continue

        if word.endswith(":") or not current_field:
            continue

        if d.get(current_field):
            # DOB must only contain one word.
            if current_field in ['DOB', 'D.O.B.']:
                continue

            # Otherwise, just append the word.
            d[current_field] += f" {word}"
        else:
            d[current_field] = word

    return d


def normalize_tokens(d):
    """
    Normalize the description tokens.

    The normalization happens in place.

    :param dict d: a dict representing the tokenized version of the description.
    :return: the list of parsing errors that occured during the normalization process.
    :rtype: list
    """
    err = []

    # Handle the DOB variations.
    if d.get("D.O.B."):
        d["DOB"] = d.pop("D.O.B.")

    # Split the deceaased fields of turn it into a list.
    if d.get("Deceased"):
        d['fatalities'] = []
        dob_marker = f'DOB: {d["DOB"]}' if d.get('DOB') else ''
        tmp_fatalities = d['Deceased'].split('Deceased') if 'Deceased' in d['Deceased'] else [
            f"{d['Deceased']} {dob_marker}"
        ]

        for fatality in tmp_fatalities:
            try:
                f, errors = deceased.process_deceased_field(fatality)
            except ValueError as e:
                err.append(str(e))
                continue
            else:
                d['fatalities'].append(f)
                err.extend(errors)

    # Parse the `Date` field.
    fatality_date = d.get('Date')
    if fatality_date:
        d[Fields.DATE] = date_utils.parse_date(fatality_date)

    # Convert the time to a time object.
    fatality_time = d.get('Time')
    if fatality_time:
        d[Fields.TIME] = date_utils.parse_time(fatality_time)

    return err


def to_report(d):
    """
    Turn a normalized tokenized description into a Report object.

    This conversion validates the dict against the model, ensuring that each attribute matches the specification. The
    tokens that are not part of the model are ignored.

    :param dict d: a dict representing the tokenized version of the description.
    :return: either a `model.Report` object representing the dict, or the list of errors preventing its creation.
    :rtype: tuple(model.Report, list())
    """
    report = None
    err = []

    # Prepare the dict to populate the report.
    dd = {k.lower(): v for k, v in d.items()}
    try:
        report = model.Report(**dd)
        report.compute_fatalities_age()
    except ValidationError as e:
        err = [f"{error['loc'][0]}: {error['msg']} ({error['type']})" for error in e.errors()]

    return report, err


def parse_description(twitter_description):
    """
    Convert text of twitter_description field to a dict with list and datetime values.

    The Twitter description sometimes contains all the information that we need,
    but sometimes doesn't have the deceased person's name.
    Even though it is still unstructured data, it sometimes is easier
    to parse than the data from the detail page.

    :param str twitter_description: Twitter description embedded in the fatality details page
    :return: either a `model.Report` object representing the dict, or the list of errors preventing its creation.
    :rtype: tuple(model.Report, list())
    """
    errors = []
    d = tokenize_description(twitter_description)
    err = normalize_tokens(d)
    if err:
        errors.extend(err)  # pragma: no cover
    report, err = to_report(d)
    if err:
        errors.extend(err)

    return report, errors


def parse_title(twitter_title):
    """
    Parse the Twitter title metadata.

    :param str twitter_title: Twitter title embedded in the fatality details page
    :return: A string representing the 'crash' field.
    :rtype: str
    """
    if not twitter_title:
        return ''

    # Extract the fatality number from the title.
    match = regex.match_crash_field(twitter_title)
    return match if match else ''


def parse(page):
    """Parse the twitter metadata."""
    twitter_title = match_title_meta(page)
    twitter_description = match_description_meta(page)

    # Parse the twitter description.
    report, err = parse_description(twitter_description)
    if not report:
        return None, err  # pragma: no cover

    # Other parse the twitter title.
    crash = parse_title(twitter_title)
    if crash:
        report.crash = int(crash)

    # Return the report.
    return report, err
