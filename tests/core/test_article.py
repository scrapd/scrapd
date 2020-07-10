"""Test the article module."""
import datetime

import pytest

from scrapd.core import article
from scrapd.core import model
from tests.test_common import load_test_page

page_scenarios = [
    {
        'id': 'single fatality',
        'page': 'traffic-fatality-2-3',
        'expected': model.Report(
            case='19-0161105',
            crash=2,
            date=datetime.date(2019, 1, 16),
            fatalities=[
                model.Fatality(
                    age=58,
                    dob=datetime.date(1960, 2, 15),
                    ethnicity=model.Ethnicity.white,
                    first='Ann',
                    gender=model.Gender.female,
                    last='Bottenfield-Seago',
                ),
            ],
            location='West William Cannon Drive and Ridge Oak Road',
            notes='The preliminary investigation shows that the grey, 2003 Volkwagen '
            'Jetta being driven by Ann Bottenfield-Seago failed to yield at a '
            'stop sign while attempting to turn westbound on to West William '
            'Cannon Drive from Ridge Oak Road. The Jetta collided with a black, '
            '2017 Chevrolet truck that was eastbound in the inside lane of West '
            'William Cannon Drive. Bottenfield-Seago was pronounced deceased at '
            'the scene. The passenger in the Jetta and the driver of the truck '
            'were both transported to a local hospital with non-life threatening '
            'injuries. No charges are expected to be filed.',
            time=datetime.time(15, 42),
        ),
        'errors': None,
    },
    {
        'id': 'multi-fatalities',
        'page': 'traffic-fatality-50-3',
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
            notes='The preliminary investigation yielded testimony from witnesses who reported seeing the '
            'BMW motorcycle driven by Cedric Benson traveling at a high rate of speed westbound in the left '
            'lane of FM 2222. A white, 2014 Dodge van was stopped at the T-intersection of Mount Bonnell Road '
            'and FM 2222. After checking for oncoming traffic, the van attempted to turn left on to FM 2222 '
            'when it was struck by the oncoming motorcycle.\n\n\tThe driver of the van was evaluated by EMS '
            'on scene and refused transport. The passenger of the van and a bystander at the scene attempted '
            'to render aid to Mr. Benson and his passenger Aamna Najam. Cedric Benson and Aamna Najam were both '
            'pronounced on scene.\n\n\tThe van driver remained on scene and is cooperating with the ongoing '
            'investigation.\n\n\tThe family of Cedric Benson respectfully requests privacy during this difficult '
            'time and asks that media refrain from contacting them.',
            time=datetime.time(22, 20),
        ),
        'errors': None,
    },
    {
        'id': 'new-format-00',
        'page': 'fatality-crash-20-2',
        'expected': model.Report(
            case='20-0530341',
            crash=20,
            date=datetime.date(2020, 2, 22),
            fatalities=[
                model.Fatality(
                    age=36,
                    dob=datetime.date(1984, 1, 17),
                    ethnicity=model.Ethnicity.white,
                    first='Calvin',
                    gender=model.Gender.male,
                    last='Bench',
                    middle='Charles',
                ),
            ],
            location='7800 FM 969',
            notes='The preliminary investigation shows that a 2005, red Honda Accord was exiting a private drive in '
            'the 7800 block of FM 969 and attempting to turn westbound onto FM 969. A 2020, silver Chevrolet Equinox '
            'was traveling eastbound in the outside lane of FM 969 and struck the driver’s side with its front.\n\nThe '
            'driver of the Honda, Calvin Charles Bench, was pronounced deceased at the scene.\n\nThe driver of the '
            'Chevrolet was arrested for DWI. Although he was arrested for DWI, his intoxication was not a contributing '
            'factor in the crash.',
            time=datetime.time(4, 54),
        ),
        'errors': None,
    },
    {
        'id': 'new-format-01',
        'page': 'fatality-crash-5-2',
        'expected': model.Report(
            case='20-0151955',
            crash=5,
            date=datetime.date(2020, 1, 15),
            fatalities=[
                model.Fatality(
                    age=18,
                    dob=datetime.date(2001, 12, 20),
                    ethnicity=model.Ethnicity.hispanic,
                    first='Fabian',
                    gender=model.Gender.male,
                    last='Morales',
                ),
            ],
            location='7600 block of Bluff Springs Rd.',
            notes='The preliminary investigation shows that a silver, 2012 Chevrolet truck and a red, 2005, Infinity '
            'sedan were in the parking lot near the 7600 block of Bluff Springs Rd. when they decided to have a road '
            'race. The Chevrolet truck and the Infiniti drove south near the 8200 block of Bluff Springs Rd. to start '
            'the race. The Chevrolet truck was in the left lane and the Infiniti was in the right lanes of northbound '
            'Bluff Springs Rd. As they raced, the Infiniti pulled way ahead of the Chevrolet truck. As the Infiniti '
            'approached the 7600 block of Bluff Springs Rd., the Infiniti attempted to turn left into the parking lot '
            'where they had previously been sitting. The Chevrolet truck hit the driver’s side of the Infiniti as it '
            'was attempting the turn. The Infiniti spun several times and came to final rest against a pole on the '
            'west side of the roadway. The driver of the Infiniti was transported to St. David’s South Austin Hospital '
            'where he died as a result of his injuries at 12:18 a.m. on Thursday, January 16, 2020. The driver of the '
            'Chevrolet truck initially fled the scene after the crash but returned to the scene later.\n'
            '\tJorge Luis Lopez-Dominguez was arrested and has been charged with two second degree felonies, racing on a '
            'highway and fail to stop and render aid. His total bond amount is $100,000.',
            time=datetime.time(23, 19),
        ),
        'errors': None,
    },
    {
        'id': 'double-deceased',
        'page': 'fatality-crash-41-2',
        'expected': model.Report(
            case='20-1850221',
            crash=41,
            date=datetime.date(2020, 7, 3),
            fatalities=[
                model.Fatality(),
            ],
            location='9600 Block of E. U.S. 290 eastbound',
            notes='',
            time=datetime.time(5, 49),
        ),
        'errors': 2,
    },
]

deceased_tag_scenarios = [
    {
        'input': '''
                <p> <strong><span style='font-family: "Verdana",sans-serif;'>Deceased:</span></strong>   
                Ann Bottenfield-Seago, White female, DOB 02/15/1960</p>
                ''',
        'expected': [
            'Ann Bottenfield-Seago, White female, DOB 02/15/1960',
        ],
        'id': 'regular',
    },
    {
        'input': '''
        <p>	<strong>Deceased 1:&nbsp; </strong>Cedric Benson | Black male | 12/28/1982</p>
        <p>	<strong>Deceased 2:&nbsp; </strong>Aamna Najam | Asian female | 01/26/1992</p>
        ''',
        'expected': [
            'Cedric Benson | Black male | 12/28/1982',
            'Aamna Najam | Asian female | 01/26/1992',
        ],
        'id': 'multi-fatality',
    },
    {
        'input': '',
        'expected': [],
        'id': 'empty',
    },
    {
        'input': '''
            <strong>Deceased:</strong>&nbsp; &nbsp; Brianna Nicole Polzine, White female (10-28-93)<br>
	        &nbsp;<br><strong>Arrested:</strong>&nbsp;&nbsp;&nbsp;&nbsp; Justin Dakota Ayers, White male (26 years of age)<br>
	        &nbsp;&nbsp;<br>''',
        'expected': ['Brianna Nicole Polzine, White female (10-28-93)'],
        'id': 'with-arrested-00',
    },
    {
        'input': '''
            <strong>Deceased:</strong>&nbsp; &nbsp; &nbsp;Robert Copeland, White male, (D.O.B. 11-7-57)<br>
	        &nbsp;<br><strong>Arrested:</strong> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Rafael Padilla, Hispanic male (28 years of age)<br>
	        &nbsp;<br>
        ''',
        'expected': ['Robert Copeland, White male, (D.O.B. 11-7-57)'],
        'id': 'with-arrested-01',
    },
    {
        'input': '''
            <strong>Deceased:&nbsp; </strong>&nbsp;&nbsp;&nbsp;Risean Deontay Lee Green | Black male | 10/16/1991<br>
	        &nbsp;<br><strong>Arrested: &nbsp;</strong>&nbsp; &nbsp; Amanda Overman, White female, 30 years of age<br>
	        &nbsp;<br>
        ''',
        'expected': ['Risean Deontay Lee Green | Black male | 10/16/1991'],
        'id': 'with-arrested-02',
    },
]


class TestPageParseContent:
    """Group the test cases for the `parsing.parse_page_content` function."""

    @pytest.mark.parametrize(
        'page,expected,errors',
        [pytest.param(s['page'], s['expected'], s['errors'], id=s['id']) for s in page_scenarios if s.get('page')])
    def test_parse_page_content_00(self, page, expected, errors):
        """Ensure location information is properly extracted from the page."""
        p = load_test_page(page)
        actual, err = article.parse_content(p)
        if errors or err:
            assert errors == len(err)
        else:
            assert actual.dict() == expected.dict()

    def test_parse_page_content_01(self):
        """Ensure a missing case number raises an exception."""
        with pytest.raises(ValueError):
            article.parse_content('There is no case number here.')

    @pytest.mark.parametrize('page,expected,errors', [
        pytest.param(
            '<p><strong>Case: </strong>19-2291933</p>'
            '<p><strong>Date: </strong>Saturday, August 17, 2019</p>'
            '<p><strong>Deceased 1:&nbsp; </strong>Cedric Benson | Black male | 12/28/1982</p>',
            model.Report(case="19-2291933", date=datetime.date(2019, 8, 17)),
            4,
            id='case-deceased-no-notes',
        ),
        pytest.param(
            '<p><strong>Case: </strong>19-2291933</p>'
            '<p><strong>Date: </strong>Saturday, August 17, 2019</p>',
            model.Report(case="19-2291933", date=datetime.date(2019, 8, 17)),
            4,
            id='no-deceased',
        ),
    ])
    def test_parse_page_content_02(self, page, expected, errors):
        """Ensure special cases are handled."""
        actual, err = article.parse_content(page)
        if errors or err:
            assert errors == len(err)
        else:
            assert actual == expected

    @pytest.mark.parametrize('page,expected,errors', [
        pytest.param(
            '<p><strong>Case:</strong>18-1591949</p>',
            model.Report(case="18-1591949", date=datetime.datetime.now().date()),
            4,
            id='case-field-only',
        ),
    ])
    def test_parse_page_content_03(self, page, expected, errors):
        """Ensure special cases are handled."""
        with pytest.raises(ValueError, match='a date is mandatory'):
            actual, err = article.parse_content(page)

    @pytest.mark.parametrize(
        'input_,expected',
        [pytest.param(s['input'], s['expected'], id=s['id']) for s in deceased_tag_scenarios],
    )
    def test_parse_deceased_tag(self, input_, expected):
        """Ensure the deceased tag is parsed correctly."""
        soup = article.to_soup(input_.replace("<br>", "</br>"))
        tag = article.get_deceased_tag(soup)
        for i, t in enumerate(tag):
            actual = article.parse_deceased_tag(t)
            assert actual == expected[i]
