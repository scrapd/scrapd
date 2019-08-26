"""Parsing functions for text referring to one person in a fatal collision bulletin."""
import calendar
import re

from scrapd.core.constant import Fields
from scrapd.core import date_utils


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

    return d, parsing_errors


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
    except ValueError:
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
