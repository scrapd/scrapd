"""Test the twitter module."""
import datetime

import pytest

from scrapd.core import model
from scrapd.core import twitter
from scrapd.core.constant import Fields
from tests.test_common import load_test_page

# Represents the expected output when parsing the data from the twitter fields.
# KEEP the keys alphabetically ordered to simplify looking for values manually.
parse_twitter_fields_scenarios = {
    'traffic-fatality-71-2': {
        Fields.CASE: '18-3381590',
        Fields.CRASH: '71',
        Fields.DATE: datetime.date(2018, 12, 4),
        Fields.LOCATION: '183 service road westbound and Payton Gin Rd.',
        Fields.TIME: datetime.time(20, 39),
    },
    'traffic-fatality-72-1': {
        Fields.CASE: '18-3551763',
        Fields.CRASH: '72',
        Fields.DATE: datetime.date(2018, 12, 21),
        Fields.LOCATION: '9500 N Mopac SB',
        Fields.TIME: datetime.time(20, 20),
    },
}

twitter_scenarios = [
    {
        'id': 'case-number-only',
        'page': 'traffic-fatality-2-3',
        'description': "Case:           19-0161105",
        'expected': model.Report(case="19-0161105", crash=2),
        'errors': 0,
    },
    {
        'id': 'regular',
        'page': 'traffic-fatality-73-2',
        'description': """
        Case:           18-3640187 Date:            December 30, 2018 Time:            2:24 a.m.
        Location:     1400 E. Highway 71 eastbound Deceased:   Corbin Sabillon-Garcia, White male, DOB 02/09/80
        The preliminary investigation shows that a 2003 Ford F150 was traveling northbound on the US Highway 183
        northbound ramp to E. Highway 71, eastbound. The truck went across the E. Highway 71 and US Highway 183 ramp,
        rolled and came to a stop north of the roadway.
        """,
        'expected': model.Report(
            case='18-3640187',
            crash=73,
            date=datetime.date(2018, 12, 30),
            fatalities=[
                model.Fatality(
                    age=38,
                    dob=datetime.date(1980, 2, 9),
                    ethnicity=model.Ethnicity.white,
                    first='Corbin',
                    gender=model.Gender.male,
                    last='Sabillon-Garcia',
                    middle='',
                ),
            ],
            location='1400 E. Highway 71 eastbound',
            time=datetime.time(2, 24),
        ),
        'errors': None,
    },
    {
        'id': 'no-notes',
        'page': None,
        'description': """
        Case:            18-160882 Date:             Tuesday, January 16, 2018  Time:             5:14 p.m.
        Location:      1500 W. Slaughter Lane Deceased:     Eva Marie Gonzales, W/F, DOB: 01-22-1961 (passenger)
        """,
        'expected': model.Report(
            case='18-160882',
            date=datetime.date(2018, 1, 16),
            fatalities=[
                model.Fatality(
                    age=57,
                    dob=datetime.date(1961, 1, 22),
                    ethnicity=model.Ethnicity.white,
                    first='Eva',
                    gender=model.Gender.female,
                    last='Gonzales',
                    middle='Marie',
                ),
            ],
            time=datetime.time(17, 14),
            location='1500 W. Slaughter Lane',
        ),
        'errors': None,
    },
    {
        'id': 'invalid-no-case-number',
        'page': None,
        'description': """
        APD is asking any businesses in the area of East Cesar Chavez and Adam L. Chapa Sr. streets
        to check their surveillance cameras between 2 and 2:10 a.m. on Oct. 10, 2018, for this suspect vehicle.
        See video of suspect vehicle here --&gt; https://youtu.be/ezxaRW79PnI
        """,
        'expected': None,
        'errors': 1,
    },
    {
        'id': 'multiple-fatalities',
        'page': 'traffic-fatality-50-3',
        'description': """
        Case:          19-2291933 Date:           Saturday, August 17, 2019 Time:          10:20 p.m.
        Location:    4500 FM 2222/Mount Bonnell Road    Deceased 1:  Cedric Benson | Black male | 12/28/1982
        Deceased 2:  Aamna Najam | Asian female | 01/26/1992
        """,
        'expected': model.Report(
            case='19-2291933',
            crash=50,
            date=datetime.date(2019, 8, 17),
            fatalities=[
                model.Fatality(
                    age=36,
                    dob=datetime.date(1982, 12, 28),
                    ethnicity=model.Ethnicity.black,
                    first='Cedric',
                    gender=model.Gender.male,
                    last='Benson',
                ),
                model.Fatality(
                    age=27,
                    dob=datetime.date(1992, 1, 26),
                    ethnicity=model.Ethnicity.asian,
                    first='Aamna',
                    gender=model.Gender.female,
                    last='Najam',
                ),
            ],
            location='4500 FM 2222/Mount Bonnell Road',
            time=datetime.time(22, 20),
        ),
        'errors': None,
    },
    {
        'id': 'empty-description',
        'page': None,
        'description': '',
        'expected': model.Report(case='19-123456', date=datetime.datetime.now().date()),
        'errors': 1,
    },
    {
        'id': 'with-arrested',
        'page': None,
        'description': 'Case:           19-2661710 Date:            Monday, September 23, 2019 '
        'Time:            8:23 p.m. Location:      9000 block of S. Congress Avenue '
        'Deceased:    Christian Livingston | White male | 01/09/1993  '
        'Arrested:      Debrah Callison | White female | 69 years of age',
        'expected': model.Report(
            case='19-2661710',
            date=datetime.date(2019, 9, 23),
            fatalities=[
                model.Fatality(
                    age=26,
                    dob=datetime.date(1993, 1, 9),
                    ethnicity=model.Ethnicity.white,
                    first='Christian',
                    gender=model.Gender.male,
                    last='Livingston',
                ),
            ],
            location='9000 block of S. Congress Avenue',
            time=datetime.time(20, 23),
        ),
        'errors': 0,
    },
]


class TestParseTwitter:
    """Group the test cases for parsing the Twitter data."""

    @pytest.mark.parametrize('input_,expected', [
        pytest.param('Traffic Fatality #73', '73', id='extract crash number'),
        pytest.param('', '', id='empty'),
    ])
    def test_parse_twitter_title_00(self, input_, expected):
        """Ensure the Twitter title gets parsed correct."""
        actual = twitter.parse_title(input_)
        assert actual == expected

    @pytest.mark.parametrize(
        'description,expected,errors',
        [
            pytest.param(s['description'].replace('\n', ' ').strip(), s['expected'], s['errors'], id=s['id'])
            for s in twitter_scenarios
        ],
    )
    def test_parse_twitter_description_00(self, description, expected, errors):
        """Ensure the Twitter description gets parsed correctly."""
        actual, err = twitter.parse_description(description)
        if errors or err:
            assert errors == len(err)
        else:
            # The twitter description does not contain the crash number so we must reset it
            # without altering the test suite.
            x = expected.copy(deep=True)
            x.crash = 0
            assert actual == x

    @pytest.mark.parametrize(
        'page,expected,errors',
        [pytest.param(s['page'], s['expected'], s['errors'], id=s['id']) for s in twitter_scenarios if s.get('page')],
    )
    def test_parse_twitter_00(self, page, expected, errors):
        """Ensure information are properly extracted from the twitter fields in a detail page."""
        p = load_test_page(page)
        actual, err = twitter.parse(p)
        if errors or err:
            assert errors == len(err)
        else:
            assert actual == expected

    @pytest.mark.parametrize('input_,expected', (
        ('<meta name="twitter:description" content="Case:           18-3551763 Date:            December 21, 2018 '
         'Time:            8:20 p.m. Location:     9500 N Mopac SB" />',
         'Case:           18-3551763 Date:            December 21, 2018 Time:            8:20 p.m. '
         'Location:     9500 N Mopac SB'),
        ('<meta name="twitter:description" content="Case:           19-0161105" />', 'Case:           19-0161105'),
    ))
    def test_extract_twitter_description_meta_00(self, input_, expected):
        """Ensure we can extract the twitter tittle from the meta tag."""
        actual = twitter.match_description_meta(input_)
        assert actual == expected

    @pytest.mark.parametrize(
        'input_,expected',
        [
            pytest.param(
                '<meta name="twitter:title" content="Traffic Fatality #2" />',
                'Traffic Fatality #2',
                id='regular-title',
            ),
        ],
    )
    def test_extract_twitter_tittle_meta_00(self, input_, expected):
        """Ensure we can extract the twitter tittle from the meta tag."""
        actual = twitter.match_title_meta(input_)
        assert actual == expected

    @pytest.mark.parametrize(
        'input_,expected',
        [
            pytest.param(
                {'D.O.B.': '01/01/2000'},
                {'DOB': '01/01/2000'},
                id='normalize-dob',
            ),
            pytest.param(
                {'Deceased': 'A person'},
                {'Deceased': 'A person'},
                id='with-fatality-error',
            ),
        ],
    )
    def test_normalize_tokens(self, input_, expected):
        """Ensure the description is tokenized correctly."""
        twitter.normalize_tokens(input_)
        assert input_ == expected
