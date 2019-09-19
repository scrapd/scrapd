""".Test the person module."""
import datetime

import pytest

from scrapd.core import person
from scrapd.core.constant import Fields


@pytest.mark.parametrize('deceased,expected', (("Rosbel “Rudy” Tamez, Hispanic male (D.O.B. 10-10-54)", {
    Fields.FIRST_NAME: "Rosbel",
    Fields.LAST_NAME: "Tamez",
    Fields.ETHNICITY: "Hispanic",
    Fields.GENDER: "male",
    Fields.DOB: datetime.date(1954, 10, 10),
}), ("Eva Marie Gonzales, W/F, DOB: 01-22-1961 (passenger)", {
    Fields.FIRST_NAME: "Eva",
    Fields.LAST_NAME: "Gonzales",
    Fields.ETHNICITY: "White",
    Fields.GENDER: 'female',
    Fields.DOB: datetime.date(1961, 1, 22),
}), (
    'DOB: 01-01-99',
    {
        Fields.DOB: datetime.date(1999, 1, 1),
    },
), (
    'Wing Cheung Chou | Asian male | 08/01/1949',
    {
        Fields.FIRST_NAME: "Wing",
        Fields.LAST_NAME: "Chou",
        Fields.ETHNICITY: "Asian",
        Fields.GENDER: "male",
        Fields.DOB: datetime.date(1949, 8, 1),
    },
), (
    'Christopher M Peterson W/M 10-8-1981',
    {
        Fields.FIRST_NAME: "Christopher",
        Fields.LAST_NAME: "Peterson",
        Fields.ETHNICITY: "White",
        Fields.GENDER: "male",
        Fields.DOB: datetime.date(1981, 10, 8),
    },
), (
    'Luis Angel Tinoco, Hispanic male (11-12-07',
    {
        Fields.FIRST_NAME: "Luis",
        Fields.LAST_NAME: "Tinoco",
        Fields.ETHNICITY: "Hispanic",
        Fields.GENDER: "male",
        Fields.DOB: datetime.date(2007, 11, 12)
    },
), (
    'Ronnie Lee Hall, White male, 8-28-51',
    {
        Fields.FIRST_NAME: "Ronnie",
        Fields.LAST_NAME: "Hall",
        Fields.ETHNICITY: "White",
        Fields.GENDER: "male",
        Fields.DOB: datetime.date(1951, 8, 28)
    },
), (
    'Hispanic male, 19 years of age',
    {
        Fields.ETHNICITY: "Hispanic",
        Fields.GENDER: "male",
        Fields.AGE: 19,
    },
), (
    'Patrick Leonard Ervin, Black male, D.O.B. August 30, 1966',
    {
        Fields.FIRST_NAME: "Patrick",
        Fields.LAST_NAME: "Ervin",
        Fields.ETHNICITY: "Black",
        Fields.GENDER: "male",
        Fields.DOB: datetime.date(1966, 8, 30)
    },
), (
    'Ernesto Gonzales Garcia, H/M, (DOB: 11/15/1977) ',
    {
        Fields.FIRST_NAME: "Ernesto",
        Fields.LAST_NAME: "Garcia",
        Fields.ETHNICITY: "Hispanic",
        Fields.GENDER: "male",
        Fields.DOB: datetime.date(1977, 11, 15)
    },
), (
    'B/F, DOB: 01-01-99',
    {
        Fields.ETHNICITY: "Black",
        Fields.GENDER: "female",
        Fields.DOB: datetime.date(1999, 1, 1)
    },
), (
    'John Doe, Hispanic male, born 9-10-80',
    {
        Fields.FIRST_NAME: "John",
        Fields.LAST_NAME: "Doe",
        Fields.ETHNICITY: "Hispanic",
        Fields.GENDER: "male",
        Fields.DOB: datetime.date(1980, 9, 10)
    },
)))
def test_process_deceased_field_00(deceased, expected):
    """Ensure a deceased field is parsed correctly."""
    d = person.process_deceased_field(deceased)
    for key in expected:
        assert d[key] == expected[key]


@pytest.mark.parametrize('name,expected', (
    (['Jonathan,', 'Garcia-Pineda,'], {
        'first': 'Jonathan',
        'last': 'Garcia-Pineda'
    }),
    (['Rosbel', '“Rudy”', 'Tamez'], {
        'first': 'Rosbel',
        'last': 'Tamez'
    }),
    (['Christopher', 'M', 'Peterson'], {
        'first': 'Christopher',
        'last': 'Peterson'
    }),
    (['David', 'Adam', 'Castro,'], {
        'first': 'David',
        'last': 'Castro'
    }),
    (['Delta', 'Olin,'], {
        'first': 'Delta',
        'last': 'Olin'
    }),
    (None, {
        'first': None,
        'last': None,
    }),
    (['Carlos', 'Cardenas', 'Jr.'], {
        'first': 'Carlos',
        'last': 'Cardenas',
    }),
))
def test_parse_name(name, expected):
    """Ensure parser finds the first and last name given the full name."""
    parsed = person.parse_name(name)
    assert parsed.get("first") == expected["first"]
    assert parsed.get("last") == expected["last"]


def test_parse_person_errors():
    result, errors = person.parse_person("text that can't be parsed")
    assert len(errors) == 2
