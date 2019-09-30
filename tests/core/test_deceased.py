"""Test the fatality module."""
import datetime

import pytest

from scrapd.core import deceased
from scrapd.core import model

name_scenarios = [
    {
        'full': None,
        'expected': deceased.Name(),
        'id': 'none',
    },
    {
        'full': '',
        'expected': deceased.Name(),
        'id': 'empty',
    },
    {
        'full': 'Jonathan, Garcia-Pineda',
        'expected': deceased.Name(first='Jonathan', last='Garcia-Pineda'),
        'id': 'double-surname',
    },
    {
        'full': 'Rosbel “Rudy” Tamez',
        'expected': deceased.Name(first='Rosbel', middle='“Rudy”', last='Tamez'),
        'id': 'middle-name-nickname',
    },
    {
        'full': 'David Adam Castro,',
        'expected': deceased.Name(first='David', middle='Adam', last='Castro'),
        'id': 'middle-name+last-name-comma',
    },
    {
        'full': 'Delta Olin,',
        'expected': deceased.Name(first='Delta', last='Olin'),
        'id': 'first-last-comma',
    },
    {
        'full': 'Carlos Cardenas Jr.',
        'expected': deceased.Name(first='Carlos', last='Cardenas', generation='Jr.'),
        'id': 'generation',
    },
    {
        'full': 'John',
        'expected': deceased.Name(first='John'),
        'id': 'first-only',
    },
]

gender_scenarios = [
    {
        'gender': None,
        'expected': model.Gender.undefined,
        'id': 'none',
    },
    {
        'gender': '',
        'expected': model.Gender.undefined,
        'id': 'empty',
    },
    {
        'gender': 'male',
        'expected': model.Gender.male,
        'id': 'male',
    },
    {
        'gender': 'm',
        'expected': model.Gender.male,
        'id': 'male-short',
    },
    {
        'gender': 'female',
        'expected': model.Gender.female,
        'id': 'female',
    },
    {
        'gender': 'f',
        'expected': model.Gender.female,
        'id': 'female-short',
    },
]

ethnicity_scenarios = [
    {
        'ethnicity': None,
        'expected': model.Ethnicity.undefined,
        'id': 'none',
    },
    {
        'ethnicity': '',
        'expected': model.Ethnicity.undefined,
        'id': 'empty',
    },
    {
        'ethnicity': 'w',
        'expected': model.Ethnicity.white,
        'id': 'white-short',
    },
    {
        'ethnicity': 'h',
        'expected': model.Ethnicity.hispanic,
        'id': 'hispanic-short',
    },
    {
        'ethnicity': 'b',
        'expected': model.Ethnicity.black,
        'id': 'black-short',
    },
    {
        'ethnicity': 'Eastern',
        'expected': model.Ethnicity.eastern,
        'id': 'eastern',
    },
    {
        'ethnicity': 'Other',
        'expected': model.Ethnicity.other,
        'id': 'other',
    },
]

dob_search_scenarios = [
    {
        'input_': 'Rosbel “Rudy” Tamez, Hispanic male (D.O.B. 10-10-54)',
        'expected': 5,
        'id': '(D.O.B.)',
    },
]

deceased_scenarios = [
    {
        'input_': 'Rosbel “Rudy” Tamez, Hispanic male (D.O.B. 10-10-54)',
        'expected': model.Fatality(
            dob=datetime.date(1954, 10, 10),
            ethnicity=model.Ethnicity.hispanic,
            first='Rosbel',
            gender=model.Gender.male,
            last='Tamez',
            middle='“Rudy”',
        ),
        'id': 'comma-delimited',
    },
    {
        'input_': 'Eva Marie Gonzales, W/F, DOB: 01-22-1961 (passenger)',
        'expected': model.Fatality(
            dob=datetime.date(1961, 1, 22),
            ethnicity=model.Ethnicity.white,
            first='Eva',
            gender=model.Gender.female,
            last='Gonzales',
            middle='Marie',
        ),
        'id': 'comma-delimited-shorts',
    },
    {
        'input_': 'DOB: 01-01-99',
        'expected': model.Fatality(dob=datetime.date(1999, 1, 1)),
        'id': 'dob-only',
    },
    {
        'input_': 'Wing Cheung Chou | Asian male | 08/01/1949',
        'expected': model.Fatality(
            dob=datetime.date(1949, 8, 1),
            ethnicity=model.Ethnicity.asian,
            first='Wing',
            gender=model.Gender.male,
            last='Chou',
            middle='Cheung',
        ),
        'id': 'pipe-delimited',
    },
    {
        'input_': 'Christopher M Peterson W/M 10-8-1981',
        'expected': model.Fatality(
            dob=datetime.date(1981, 10, 8),
            ethnicity=model.Ethnicity.white,
            first='Christopher',
            gender=model.Gender.male,
            last='Peterson',
            middle='M',
        ),
        'id': 'space-delimited-shorts',
    },
    {
        'input_': 'Luis Angel Tinoco, Hispanic male (11-12-07',
        'expected': model.Fatality(
            dob=datetime.date(2007, 11, 12),
            ethnicity=model.Ethnicity.hispanic,
            first='Luis',
            gender=model.Gender.male,
            last='Tinoco',
            middle='Angel',
        ),
        'id': 'comma-delimited-shorts-parenthesis-dob',
    },
    {
        'input_': 'Ronnie Lee Hall, White male, 8-28-51',
        'expected': model.Fatality(
            dob=datetime.date(1951, 8, 28),
            ethnicity=model.Ethnicity.white,
            first='Ronnie',
            gender=model.Gender.male,
            last='Hall',
            middle='Lee',
        ),
        'id': 'comma-delimited-shorts-no-dob-marker',
    },
    {
        'input_': 'Hispanic male, 19 years of age',
        'expected': model.Fatality(
            age=19,
            ethnicity=model.Ethnicity.hispanic,
            gender=model.Gender.male,
        ),
        'id': 'years-of-age',
    },
    {
        'input_': 'Patrick Leonard Ervin, Black male, D.O.B. August 30, 1966',
        'expected': model.Fatality(
            dob=datetime.date(1966, 8, 30),
            ethnicity=model.Ethnicity.black,
            first='Patrick',
            gender=model.Gender.male,
            last='Ervin',
            middle='Leonard',
        ),
        'id': 'comma-delimited-full-english-date',
    },
    {
        'input_': 'Ernesto Gonzales Garcia, H/M, (DOB: 11/15/1977)',
        'expected': model.Fatality(
            dob=datetime.date(1977, 11, 15),
            ethnicity=model.Ethnicity.hispanic,
            first='Ernesto',
            gender=model.Gender.male,
            last='Garcia',
            middle='Gonzales',
        ),
        'id': 'comma-delimited-shorts-(dob:',
    },
    {
        'input_': 'B/F, DOB: 01-01-99',
        'expected': model.Fatality(
            dob=datetime.date(1999, 1, 1),
            ethnicity=model.Ethnicity.black,
            gender=model.Gender.female,
        ),
        'id': 'no-names-shorts',
    },
    {
        'input_': 'Felipe Ramirez, Hispanic male, born 9-16-93',
        'expected': model.Fatality(
            dob=datetime.date(1993, 9, 16),
            ethnicity=model.Ethnicity.hispanic,
            first='Felipe',
            gender=model.Gender.male,
            last='Ramirez',
        ),
        'id': 'born-instead-of-dob',
    },
]


class TestFatality:
    """Test the fatality parsing."""

    @pytest.mark.parametrize(
        'input_,expected',
        [pytest.param(s['full'], s['expected'], id=s['id']) for s in name_scenarios],
    )
    def test_parse_name(self, input_, expected):
        """Ensure a victim's full name is parsed."""
        actual = deceased.parse_name(input_)
        assert actual == expected

    @pytest.mark.parametrize(
        'input_,expected',
        [pytest.param(s['gender'], s['expected'], id=s['id']) for s in gender_scenarios],
    )
    def test_parse_gender(self, input_, expected):
        """Ensure a victim's gender is parsed."""
        actual = deceased.parse_gender(input_)
        assert actual == expected

    @pytest.mark.parametrize(
        'input_,expected',
        [pytest.param(s['ethnicity'], s['expected'], id=s['id']) for s in ethnicity_scenarios],
    )
    def test_parse_ethinicity(self, input_, expected):
        """Ensure a victim's ethnicity is parsed."""
        actual = deceased.parse_ethinicity(input_)
        assert actual == expected

    # @pytest.mark.parametrize(
    #     'input_,expected',
    #     [pytest.param(s['ethnicity'], s['expected'], id=s['id']) for s in ethnicity_scenarios],
    # )
    # def test_parse_fleg(self, input_, expected):
    #     """Ensure victim's FLEG is parsed."""
    #     actual = fatality.parse_fleg(input_)
    #     assert actual == expected

    @pytest.mark.parametrize(
        'input_,expected',
        [pytest.param(s['input_'].split(), s['expected'], id=s['id']) for s in dob_search_scenarios],
    )
    def test_dob_search(self, input_, expected):
        """Ensure the DOB separator is found."""
        actual = deceased.dob_search(input_)
        assert actual == expected

    @pytest.mark.parametrize(
        'input_,expected',
        [pytest.param(s['input_'], s['expected'], id=s['id']) for s in deceased_scenarios],
    )
    def test_process_deceased_field(self, input_, expected):
        """Ensure the deceased field gets processed correctly."""
        actual, _ = deceased.process_deceased_field(input_)
        assert actual == expected

    @pytest.mark.parametrize(
        'input_,expected',
        [
            pytest.param({'age': 'age'}, (None, 1), id='age-as-string'),
        ],
    )
    def test_to_fatality(self, input_, expected):
        """."""
        actual, err = deceased.to_fatality(input_)
        assert actual == expected[0]
        assert len(err) == expected[1]
