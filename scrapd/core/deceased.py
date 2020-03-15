"""
Manage the parsing of fatalities.

Deceased is a special field as it contains a lot of other fields:
- First name
- Middle name(s)
- Last name
- Ethinicity
- Gender
- Date of birth
- (Notes)
"""
import calendar
from dataclasses import asdict
from dataclasses import dataclass
import re

# import bs4
from pydantic import ValidationError

from scrapd.core import date_utils
from scrapd.core import model
from scrapd.core.constant import Fields


@dataclass
class Name:
    """Represent a victim's full name."""

    first: str = ''
    generation: str = ''
    last: str = ''
    middle: str = ''


def to_fatality(d):
    """
    Turn a normalized tokenized description into a Fatality object.

    This conversion validates the dict against the model, ensuring that each attribute matches the specification. The
    tokens that are not part of the model are ignored.

    :param dict d: a dict representing the tokenized version of the description.
    :return: either a `model.Report` object representing the dict, or the list of errors preventing its creation.
    :rtype: tuple(model.Report, list())
    """
    fatality = None
    err = []

    # Prepare the dict to populate the report.
    dd = {k.lower(): v for k, v in d.items()}
    try:
        fatality = model.Fatality(**dd)
    except ValidationError as e:
        err = [
            f"{error['loc'][0]}: \"{dd.get(error['loc'][0])}\" {error['msg']} ({error['type']})"
            for error in e.errors()
        ]

    return fatality, err


def parse_name(full_name):
    """
    Parse the victim's name.

    :param str name: a str reprenting the deceased person's full name
    :return: a fatality.Name object
    :rtype: fatality.Name
    """
    GENERATIONAL_TITLES = ['jr', 'jr.', 'sr', 'sr.']
    n = Name()

    # Return an empty name object if there is no full name provided.
    if not full_name:
        return n

    # Split and clean the name.
    split_name = full_name.split()
    clean_split_name = list(map(lambda x: x.replace(',', ''), split_name))

    # Find the generation if any.
    for i, item in enumerate(clean_split_name):
        if item.lower() in GENERATIONAL_TITLES:
            n.generation = clean_split_name.pop(i).strip()
            break

    # Extract the name values.
    try:
        n.first = clean_split_name.pop(0).strip()
        n.last = clean_split_name.pop().strip()
        n.middle = ' '.join(clean_split_name).strip()
    except IndexError:
        pass

    return n


def parse_gender(gender):
    """
    Parse victim's gender.

    :param str gender: a string representing the vinctim's gender
    :return: a `model.Gender` object representing the vinctim's gender.
    :rtype: `model.Gender`
    """
    if not gender:
        return model.Gender.undefined

    # Normalize the gender.
    g = gender.replace(',', '').capitalize()

    # Handle female special cases.
    if g in ['F']:
        return model.Gender.female

    # Handle male special cases.
    if g in ['M']:
        return model.Gender.male

    # Try regular options.
    try:
        return model.Gender(g)
    except ValueError:
        return model.Gender.undefined


def parse_ethinicity(ethnicity):
    """
    Parse victim's ethnicity.

    :param str ethinicity: a string representing the vinctim's ethnicity
    :return: a `model.Ethnicity` object representing the vinctim's ethnicity.
    :rtype: `model.Ethnicity`
    """
    if not ethnicity:
        return model.Ethnicity.undefined

    # Normalize the gender.
    e = ethnicity.replace(',', '').capitalize()

    # Handle black special cases.
    if e in ['B']:
        return model.Ethnicity.black

    # Handle hispanic special cases.
    if e in ['H']:
        return model.Ethnicity.hispanic

    # Handle white special cases.
    if e in ['W']:
        return model.Ethnicity.white

    # Try regular options.
    try:
        return model.Ethnicity(e)
    except ValueError:
        return model.Ethnicity.undefined


def parse_fleg(fleg):
    """
    Parse FLEG. `fleg` stands for First, Last, Ethnicity, Gender.

    :param list fleg: values representing the fleg.
    :return: a dictionary containing First, Last, Ethnicity, Gender fields
    :rtype: dict
    """
    d = {}
    # Try to pop out the results one by one. If pop fails, it means there is nothing left to retrieve.
    try:
        d[Fields.GENDER] = parse_gender(fleg.pop())
        d[Fields.ETHNICITY] = parse_ethinicity(fleg.pop())
    except IndexError:
        pass

    name = parse_name(' '.join(fleg))
    d.update(**asdict(name))
    return d


def dob_search(split_deceased_field):
    """
    Search for the DOB in a deceased field.

    :param list split_deceased_field: a list representing the deceased field
    :return: the DOB index within the split deceased field.
    :rtype: int
    """
    dob_index = -1
    dob_tokens = [Fields.DOB, 'DOB', '(D.O.B', '(D.O.B.', '(D.O.B:', '(DOB', '(DOB:', 'D.O.B.', 'DOB:', 'born', 'Born']
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
    :return: a tuple containing a model.Fatality and a list of associated parsing errors.
    :rtype: tuple(model.Fatality, list())
    """
    # Parse methods ordered by usage.
    parse_methods = [
        parse_comma_delimited_deceased_field,
        parse_pipe_delimited_deceased_field,
        parse_space_delimited_deceased_field,
        parse_age_deceased_field,
        parse_unidentified,
    ]

    # Execute the parsing methods in order.
    for m in parse_methods:
        try:
            d = m(deceased_field)
            if isinstance(d, dict):
                return [to_fatality(d)]
            if isinstance(d, list):
                return [to_fatality(entry) for entry in d]
        except (ValueError, IndexError):
            pass

    raise ValueError(f'cannot parse {Fields.DECEASED}: "{deceased_field}"')  # pragma: no cover


def parse_age_deceased_field(deceased_field):
    """
    Parse deceased field assuming it contains an age.

    :param str deceased_field: the deceased field
    :return: a dictionary representing the deceased field.
    :rtype: dict
    """
    age_pattern = re.compile(r'([0-9]+) years')

    age = re.search(age_pattern, deceased_field)
    if age is None:
        raise ValueError("age not found in Deceased field")
    split_deceased_field = age_pattern.split(deceased_field)
    d = parse_fleg(split_deceased_field[0].split())
    d[Fields.AGE] = int(age.group(1))

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


def parse_unidentified(deceased_field):
    """
    Parse deceased field with unidentified victims.

    :param str deceased_field: the deceased field as a string.
    :return: a list of dictionaries representing the deceased field.
    :rtype: list of dicts
    """
    unidentified_deceased_pattern = re.compile(
        r'''
        (?:                         # Non captured group
        (Unidentified               # The "Unidentified" keyword
        |                           # Or
        Unknown                     # The "Unknown" keyword
        )
        ,?                          # Potentially a comma
        \s                          # A whitespace
        (?P<ethinicty>[^\s]+\s)?    # The ethinicty
        (?P<gender>female|male)     # The gender
        )
        ''',
        re.VERBOSE,
    )
    matches = re.finditer(unidentified_deceased_pattern, deceased_field)
    unidentified_fatalities = []
    for match in matches:
        d = {
            Fields.GENDER: (match.group('gender') or 'Undefined').strip().capitalize(),
            Fields.ETHNICITY: (match.group('ethinicty') or 'Undefined').strip().capitalize(),
        }
        unidentified_fatalities.append(d)

    if not unidentified_fatalities:
        raise ValueError("no unidentified fatality found")
    return unidentified_fatalities


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
