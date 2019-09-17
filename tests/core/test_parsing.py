"""Test the parsing module."""
import datetime

import asynctest
from faker import Faker
import pytest
from tenacity import RetryError
from tenacity import stop_after_attempt

from scrapd.core import apd
from scrapd.core import parsing
from scrapd.core.constant import Fields
from tests import mock_data
from tests.test_common import scenario_ids
from tests.test_common import scenario_inputs
from tests.test_common import TEST_DATA_DIR
from tests.core.test_apd import load_test_page

# Set faker object.
fake = Faker()

parse_multiple_scenarios = {
    'traffic-fatality-50-3': {
        Fields.GENDER: "female",
        Fields.DOB: datetime.date(1992, 1, 26)
    },
    'traffic-fatality-15-4': {
        Fields.DOB: datetime.date(1991, 11, 13)
    }
}

parse_twitter_fields_scenarios = {
    'traffic-fatality-2-3': {
        Fields.CASE: '19-0161105',
        Fields.CRASHES: '2',
    },
    'traffic-fatality-73-2': {
        Fields.CASE: '18-3640187',
        Fields.CRASHES: '73',
        Fields.DATE: datetime.date(2018, 12, 30),
        Fields.DOB: datetime.date(1980, 2, 9),
        Fields.LOCATION: '1400 E. Highway 71 eastbound',
        Fields.NOTES: 'The preliminary investigation shows that a 2003 Ford F150 was '
        'traveling northbound on the US Highway 183 northbound ramp to E. '
        'Highway 71, eastbound. The truck went across the E. Highway 71 and '
        'US Highway 183 ramp, rolled and came to a stop north of the '
        'roadway.',
        Fields.TIME: datetime.time(2, 24),
    },
    'traffic-fatality-72-1': {
        Fields.CASE: '18-3551763',
        Fields.CRASHES: '72',
        Fields.DATE: datetime.date(2018, 12, 21),
        Fields.LOCATION: '9500 N Mopac SB',
        Fields.TIME: datetime.time(20, 20),
    },
    'traffic-fatality-71-2': {
        Fields.CASE: '18-3381590',
        Fields.CRASHES: '71',
        Fields.DATE: datetime.date(2018, 12, 4),
        Fields.LOCATION: '183 service road westbound and Payton Gin Rd.',
        Fields.TIME: datetime.time(20, 39),
    },
}

parse_page_content_scenarios = {
    'traffic-fatality-2-3': {
        **parse_twitter_fields_scenarios['traffic-fatality-2-3'],
        Fields.AGE: 58,
        Fields.CRASHES: '2',
        Fields.DOB: datetime.date(1960, 2, 15),
        Fields.DATE: datetime.date(2019, 1, 16),
        Fields.ETHNICITY: 'White',
        Fields.FIRST_NAME: 'Ann',
        Fields.GENDER: 'female',
        Fields.LAST_NAME: 'Bottenfield-Seago',
        Fields.LOCATION: 'West William Cannon Drive and Ridge Oak Road',
        Fields.TIME: datetime.time(15, 42),
    },
    'traffic-fatality-73-2': {
        Fields.AGE: 38,
        Fields.CASE: '18-3640187',
        Fields.CRASHES: '73',
        Fields.DOB: datetime.date(1980, 2, 9),
        Fields.DATE: datetime.date(2018, 12, 30),
        Fields.ETHNICITY: 'White',
        Fields.FIRST_NAME: 'Corbin',
        Fields.GENDER: 'male',
        Fields.LAST_NAME: 'Sabillon-Garcia',
        Fields.LOCATION: '1400 E. Highway 71 eastbound',
        Fields.TIME: datetime.time(2, 24),
    },
    'traffic-fatality-20-4': {
        Fields.CASE: '19-1080319',
        Fields.DATE: datetime.date(2019, 4, 18),
        Fields.CRASHES: '20',
        Fields.LOCATION: '8000 block of West U.S. 290',
        Fields.TIME: datetime.time(6, 53),
        Fields.ETHNICITY: 'Hispanic',
        Fields.GENDER: 'male',
        Fields.AGE: 19,
    },
    'traffic-fatality-72-1': {
        **parse_twitter_fields_scenarios['traffic-fatality-72-1'],
        Fields.AGE: 22,
        Fields.DOB: datetime.date(1996, 3, 29),
        Fields.ETHNICITY: 'White',
        Fields.FIRST_NAME: 'Elijah',
        Fields.GENDER: 'male',
        Fields.LAST_NAME: 'Perales',
    },
    'traffic-fatality-71-2': {
        **parse_twitter_fields_scenarios['traffic-fatality-71-2'],
        Fields.DOB: datetime.date(1964, 6, 1),
        Fields.FIRST_NAME: 'Barkat',
        Fields.LAST_NAME: 'Umatia',
        Fields.ETHNICITY: 'Other',
        Fields.GENDER: 'male',
        Fields.AGE: 54,
    },
}

parse_page_scenarios = {
    'traffic-fatality-2-3': {
        **parse_page_content_scenarios['traffic-fatality-2-3'],
        **parse_twitter_fields_scenarios['traffic-fatality-2-3'],
    },
    'traffic-fatality-71-2': {
        **parse_page_content_scenarios['traffic-fatality-71-2'],
        **parse_twitter_fields_scenarios['traffic-fatality-71-2'],
    },
    'traffic-fatality-72-1': {
        **parse_page_content_scenarios['traffic-fatality-72-1'],
        **parse_twitter_fields_scenarios['traffic-fatality-72-1'],
    },
    'traffic-fatality-73-2': {
        **parse_page_content_scenarios['traffic-fatality-73-2'],
        **parse_twitter_fields_scenarios['traffic-fatality-73-2'],
    },
}


@pytest.mark.parametrize('input_,expected', (
    (
        mock_data.twitter_title_00,
        {
            'Fatal crashes this year': '73'
        },
    ),
    (None, {}),
))
def test_parse_twitter_title_00(input_, expected):
    """Ensure the Twitter title gets parsed correct."""
    actual = parsing.parse_twitter_title(input_)
    assert actual == expected


@pytest.mark.parametrize('input_,expected', (
    (
        mock_data.twitter_description_00,
        {
            'Case': '18-3640187',
            'Date': datetime.date(2018, 12, 30),
            'DOB': datetime.date(1980, 2, 9),
            'Time': datetime.time(2, 24),
            'Location': '1400 E. Highway 71 eastbound',
            'Notes': 'The preliminary investigation shows that a 2003 Ford F150 was '
            'traveling northbound on the US Highway 183 northbound ramp to E. Highway 71, eastbound. '
            'The truck went across the E. Highway 71 and US Highway 183 ramp, rolled '
            'and came to a stop north of the roadway.',
            'Deceased': ['Corbin Sabillon-Garcia, White male,']
        },
    ),
    (None, {}),
))
def test_parse_twitter_description_00(input_, expected):
    """Ensure the Twitter description gets parsed correctly."""
    actual = parsing.parse_twitter_description(input_)
    assert actual == expected


def test_parse_twitter_description_01():
    """Ensure the Twitter description gets parsed correctly."""
    actual = parsing.parse_twitter_description(mock_data.twitter_description_01)
    expected = {
        Fields.CASE: '19-0161105',
    }
    assert actual == expected


def test_parse_twitter_description_02():
    """Ensure a DOB recognized as a field can be parsed."""
    actual = parsing.parse_twitter_description(mock_data.twitter_description_02)
    expected = {
        'Case': '18-160882',
        'DOB': datetime.date(1961, 1, 22),
        'Date': datetime.date(2018, 1, 16),
        'Location': '1500 W. Slaughter Lane',
        'Time': datetime.time(17, 14),
    }
    if 'Deceased' in actual:
        del actual['Deceased']
    assert actual == expected


def test_parse_twitter_description_03():
    """Ensure a DOB recognized as a field can be parsed."""
    actual = parsing.parse_twitter_description(mock_data.twitter_description_03)
    expected = {}
    assert actual == expected


def test_parse_twitter_description_without_notes():
    """
    Test that the parser finds the right number of deceased people.
    """
    twitter_description = ("'Case:         19-1321936 Date:          May 12, 2019 "
                           "Time:         11:34 p.m. Location:   12100 N. IH-35 NB Service road "
                           "Deceased:  First Middle Last, Black male, D.O.B. August 30, 1966'")
    d = parsing.parse_twitter_description(twitter_description)
    assert not d.get("D.O.B.")
    assert d["DOB"] == datetime.date(1966, 8, 30)


@pytest.mark.parametrize('page,start,end',
                         scenario_inputs(mock_data.note_fields_scenarios),
                         ids=scenario_ids(mock_data.note_fields_scenarios))
def test_parse_notes(page, start, end):
    """Ensure Notes field are parsed correctly."""
    soup = parsing.to_soup(page)
    deceased_field_list = parsing.parse_deceased_field(soup)
    notes = parsing.parse_notes_field(soup, deceased_field_list[-1])
    assert notes.startswith(start)
    assert notes.endswith(end)


@pytest.mark.parametrize('page,start,end', (
    ('traffic-fatality-2-3', 'The preliminary investigation shows that the grey',
     'No charges are expected to be filed.'),
    ('traffic-fatality-4-6', 'The preliminary investigation shows that a black, Ford', 'scene at 01:48 a.m.'),
    ('traffic-fatality-15-4', 'The preliminary investigation indicated that Garrett',
     'seatbelts. No charges are expected to be filed.'),
    ('traffic-fatality-16-4', 'The preliminary investigation revealed that the 2017', 'injuries on April 4, 2019.'),
    ('traffic-fatality-17-4', 'The preliminary investigation revealed that the 2010', 'at the time of the crash.'),
    ('traffic-fatality-20-4', 'The preliminary investigation revealed that a 2016',
     'pronounced deceased at the scene.'),
    ('traffic-fatality-25-4', 'Suspect Vehicle:  dark colored', 'damage to its right, front end.'),
    ('traffic-fatality-71-2', 'The preliminary investigation shows that a 2004 Honda sedan',
     'at the scene at 8:50 p.m.'),
    ('traffic-fatality-72-1', 'The preliminary investigation shows that the 2016 Indian',
     'whether charges will be filed.'),
    ('traffic-fatality-73-2', 'The preliminary investigation shows that a 2003 Ford F150',
     'St. David’s South Austin Hospital.'),
))
def test_parse_notes_field(page, start, end):
    page_text = load_test_page(page)
    parsed_content, r = parsing.parse_page_content(page_text)
    notes = parsed_content[Fields.NOTES]
    assert notes.startswith(start)
    assert notes.endswith(end)


def test_no_DOB_field_when_DOB_not_provided():
    """
    Test that "Hispanic male, 19 years of age" does not
    generate a DOB field.
    """
    page_fd = TEST_DATA_DIR / 'traffic-fatality-20-4'
    page = page_fd.read_text()
    parsed_content = next(parsing.parse_page(page, 'fake_url'))
    assert not parsed_content.get(Fields.DOB)


@pytest.mark.parametrize('page,before,after', (('traffic-fatality-50-3', '1982', 'Aa'), ))
def test_extract_deceased_field_twitter(page, before, after):
    """
    Ensure that parsing of the Twitter fields results in two different
    records about deceased people, and that one ends and the next begins
    in the right place.
    """
    page_text = load_test_page(page)
    parsed_content = parsing.parse_twitter_fields(page_text)
    deceased = parsed_content[Fields.DECEASED]
    assert deceased[0].endswith(before)
    assert deceased[-1].startswith(after)


@pytest.mark.parametrize(
    'text_field,before,after',
    (('Sam Driver | Black female | 01/02/1982 Deceased Lee Passenger | Hispanic female | 02/01/1928', '1982', 'Lee'), ))
def test_twitter_deceased_field_to_list(text_field, before, after):
    """
    Test that if the Deceased field contains some text, the word "Deceased", and
    some more text, it gets broken up into multiple records about multiple deceased people.
    """
    multiple_deceased = parsing.twitter_deceased_field_to_list(text_field)
    assert multiple_deceased[0].endswith(before)
    assert multiple_deceased[-1].startswith(after)


@pytest.mark.parametrize('page,start,end', (
    ('traffic-fatality-15-4', 'Garre', '13/1991'),
    ('traffic-fatality-50-3', 'Cedric', '| 01/26/1992'),
))
def test_extract_deceased_field_from_page(page, start, end):
    page_text = load_test_page(page)
    parsed_content, _ = parsing.parse_page_content(page_text)
    deceased = parsed_content[Fields.DECEASED]
    assert deceased[0].startswith(start)
    assert deceased[-1].endswith(end)


@pytest.mark.parametrize('filename,expected', [(k, v) for k, v in parse_page_content_scenarios.items()])
def test_parse_page_content_00(filename, expected):
    """Ensure information are properly extracted from the content detail page.
           Don't compare notes if parsed from details page."""
    page_fd = TEST_DATA_DIR / filename
    page = page_fd.read_text()
    actual = next(parsing.parse_page(page, 'fake_url'))
    if 'Notes' in actual and 'Notes' not in expected:
        del actual['Notes']
    if 'Deceased' in actual and 'Deceased' not in expected:
        del actual['Deceased']
    assert actual == expected


def test_parse_page_content_01(mocker):
    """Ensure a `process_deceased_field` exception is caught and does not propagate."""
    page_fd = TEST_DATA_DIR / 'traffic-fatality-2-3'
    page = page_fd.read_text()
    mocker.patch('scrapd.core.person.process_deceased_field', side_effect=ValueError)
    result, err = parsing.parse_page_content(page)
    if 'Deceased' in result:
        del result['Deceased']
    assert len(result) == 6


def test_parse_page_content_02(mocker):
    """Ensure a log entry is created if there is no deceased field."""
    result, err = parsing.parse_page_content('Case: 01-2345678')
    assert result


def test_parse_page_content_03():
    """Ensure a missing case number raises an exception."""
    with pytest.raises(ValueError):
        parsing.parse_page_content('The is no case number here.')


@pytest.mark.parametrize('filename,expected', [(k, v) for k, v in parse_twitter_fields_scenarios.items()])
def test_parse_twitter_fields_00(filename, expected):
    """Ensure information are properly extracted from the twitter fields on detail page."""
    page_fd = TEST_DATA_DIR / filename
    page = page_fd.read_text()
    actual = parsing.parse_twitter_fields(page)
    if 'Deceased' in actual and 'Deceased' not in expected:
        del actual['Deceased']
    assert actual == expected


@pytest.mark.parametrize('filename,expected', [(k, v) for k, v in parse_page_scenarios.items()])
def test_parse_page_00(filename, expected):
    """Ensure information are properly extracted from the page.
       Don't compare notes if parsed from details page."""
    page_fd = TEST_DATA_DIR / filename
    page = page_fd.read_text()
    actual = next(parsing.parse_page(page, fake.uri()))
    if 'Notes' in actual and 'Notes' not in expected:
        del actual['Notes']
    assert actual == expected


parse_location_scenarios = {
    'traffic-fatality-50-3': '4500 FM 2222/Mount Bonnell Road',
}


def test_parse_page_with_missing_data():
    records = parsing.parse_page("Case:    19-1234567", fake.uri())
    with pytest.raises(StopIteration):
        next(records)


@pytest.mark.parametrize('filename,expected', [(k, v) for k, v in parse_location_scenarios.items()])
def test_parse_page_get_location(filename, expected):
    """Ensure location information is properly extracted from the page."""
    page_fd = TEST_DATA_DIR / filename
    page = page_fd.read_text()
    actual = parsing.parse_page(page, fake.uri())
    assert next(actual)['Location'] == expected


@pytest.mark.parametrize('filename,expected', [(k, v) for k, v in parse_page_scenarios.items()])
def test_parse_page_01(mocker, filename, expected):
    """Ensuri
    ng ."""
    data = {}
    parsing_errors = ['one error']
    page_fd = TEST_DATA_DIR / filename
    page = page_fd.read_text()
    pc = mocker.patch('scrapd.core.parsing.parse_page_content', return_value=(data, parsing_errors))
    _ = parsing.parse_page(page, fake.uri())
    assert pc.called_once


@asynctest.patch("scrapd.core.apd.fetch_detail_page", return_value='Not empty page')
@pytest.mark.asyncio
async def test_fetch_and_parse_01(page, mocker):
    """Ensure a page that cannot be parsed returns an exception."""
    mocker.patch("scrapd.core.parsing.parse_page", return_value={})
    with pytest.raises(RetryError):
        apd.fetch_and_parse.retry.stop = stop_after_attempt(1)
        await apd.fetch_and_parse(None, 'url')


@pytest.mark.parametrize('input_,expected', (
    (pytest.param('<p>	<strong>Deceased: </strong> Luis Fernando Martinez-Vertiz | Hispanic male | 04/03/1994</p>',
                  ['Luis Fernando Martinez-Vertiz | Hispanic male | 04/03/1994'],
                  id="p, strong, pipes")),
    (pytest.param('<p>	<strong>Deceased: </strong> Cecil Wade Walker, White male, D.O.B. 3-7-70</p>',
                  ['Cecil Wade Walker, White male, D.O.B. 3-7-70'],
                  id="p, strong, commas")), (pytest.param(
                      '<p style="margin-left:.25in;">'
                      '<strong>Deceased:&nbsp;</strong> Halbert Glen Hendricks | Black male | 9-24-78</p>',
                      ['Halbert Glen Hendricks | Black male | 9-24-78'],
                      id="p with style, strong, pipes")), (pytest.param('', [], id="Deceased tag not found")),
    (pytest.param(
        '<p>	<strong>Deceased:&nbsp; </strong>Hispanic male, 19 years of age<br>'
        '&nbsp;<br>'
        'The preliminary investigation revealed that a 2016, black Toyota 4Runner was exiting a private driveway at '
        '8000 W. Hwy. 290. Signs are posted for right turn only and the driver of the 4Runner failed to comply and '
        'made a left turn. A 2008, gray Ford Mustang was traveling westbound in the inside lane and attempted to avoid '
        'the 4Runner but struck its front end. The Mustang continued into eastbound lanes of traffic and was struck by '
        'a 2013, maroon Dodge Ram.<br>'
        '&nbsp;<br>'
        'The driver of the Mustang was pronounced deceased at the scene.<br>'
        '&nbsp;<br>'
        'Anyone with information regarding this case should call APD’s Vehicular Homicide Unit Detectives at '
        '(512) 974-6935. You can also submit tips by downloading APD’s mobile app, Austin PD, for free on '
        '<a href="https://austintexas.us5.list-manage.com/track/click?u=1861810ce1dca1a4c1673747c&amp;'
        'id=26ced4f341&amp;e=bcdeacc118">iPhone</a> and <a href="https://austintexas.us5.list-manage.com/track/click'
        '?u=1861810ce1dca1a4c1673747c&amp;id=3abaf7d912&amp;e=bcdeacc118">Android</a>.&nbsp;</p>',
        ['Hispanic male, 19 years of age'],
        id='XX years of age of age format + included in notes paragraph')),
    (pytest.param(
        '<p>	<strong><span style="font-family: &quot;Verdana&quot;,sans-serif;">Deceased:</span></strong>&nbsp; '
        '&nbsp;Ann Bottenfield-Seago, White female, DOB 02/15/1960<br>'
        '&nbsp;<br>'
        'The preliminary investigation shows that the grey, 2003 Volkwagen Jetta being driven by '
        'Ann Bottenfield-Seago failed to yield at a stop sign while attempting to turn westbound on to West William '
        'Cannon Drive from Ridge Oak Road. The Jetta collided with a black, 2017 Chevrolet truck that was eastbound in '
        'the inside lane of West William Cannon Drive. Bottenfield-Seago was pronounced deceased at the scene. The '
        'passenger in the Jetta and the driver of the truck were both transported to a local hospital with non-life '
        'threatening injuries. No charges are expected to be filed.<br>'
        '&nbsp;<br>'
        'APD is investigating this case. Anyone with information regarding this case should call APD’s Vehicular '
        'Homicide Unit Detectives at (512) 974-3761. You can also submit tips by downloading APD’s mobile app, '
        'Austin PD, for free on <a href="https://austintexas.us5.list-manage.com/track/click?'
        'u=1861810ce1dca1a4c1673747c&amp;id=d8c2ad5a29&amp;e=bcdeacc118"><span style="color: rgb(197, 46, 38); '
        'text-decoration: none; text-underline: none;">iPhone</span></a> and '
        '<a href="https://austintexas.us5.list-manage.com/track/click?'
        'u=1861810ce1dca1a4c1673747c&amp;id=5fcb8ff99e&amp;e=bcdeacc118"><span style="color: rgb(197, 46, 38); '
        'text-decoration: none; text-underline: none;">Android</span></a>.<br>'
        '&nbsp;<br>'
        'This is Austin’s second fatal traffic crash of 2018, resulting&nbsp;in two fatalities this year. At this time '
        'in 2018, there were two fatal traffic crashes and three traffic fatalities.<br>'
        '&nbsp;<br><strong><i><span style="font-family: &quot;Verdana&quot;,sans-serif;">These statements are based '
        'on the initial assessment of the fatal crash and investigation is still pending. Fatality information may '
        'change.</span></i></strong></p>',
        ['Ann Bottenfield-Seago, White female, DOB 02/15/1960'],
        id='included in notes paragraph',
    )), (pytest.param(
        '<p>	<strong>Deceased:   </strong>David John Medrano,<strong> </strong>Hispanic male, D.O.B. 6-9-70</p>',
        ['David John Medrano, Hispanic male, D.O.B. 6-9-70'],
        id='stray strong in the middle',
    )), (pytest.param(
        '<p>	<strong>Deceased 1:&nbsp; </strong>Cedric Benson | Black male | 12/28/1982</p>'
        '<p>	<strong>Deceased 2:&nbsp; </strong>Aamna Najam | Asian female | 01/26/1992</p>',
        ['Cedric Benson | Black male | 12/28/1982', 'Aamna Najam | Asian female | 01/26/1992'],
        id='double deceased',
    )), (pytest.param('<p> <strong>Deceased:   </strong>Ernesto Gonzales Garcia, H/M, (DOB: 11/15/1977) </p>',
                      ['Ernesto Gonzales Garcia, H/M, (DOB: 11/15/1977)'],
                      id='colon after DOB'))))
def test_parse_deceased_field_00(input_, expected):
    """Ensure the deceased field gets parsed correctly."""
    field = parsing.to_soup(input_)
    deceased_str = parsing.parse_deceased_field(field)
    assert deceased_str == expected


@pytest.mark.parametrize('filename,expected', [(k, v) for k, v in parse_multiple_scenarios.items()])
def test_multiple_deceased(filename, expected):
    """
    Ensure that the second record yielded by parsing.parse_page
    is the second deceased person from a collision.
    """
    page_text = load_test_page(filename)
    content_parser = parsing.parse_page(page_text, 'fake_url')
    _ = next(content_parser)
    second_person = next(content_parser)
    for key in expected:
        assert second_person[key] == expected[key]


@pytest.mark.parametrize('input_,expected', (
    (
        {
            'Time': 345
        },
        {
            'Time': 345
        },
    ),
    (
        {
            'Time': ['123', '345']
        },
        {
            'Time': '123 345'
        },
    ),
    (
        {
            'Time': ' '
        },
        {},
    ),
    (
        {
            'Time': None
        },
        {},
    ),
))
def test_sanitize_fatality_entity(input_, expected):
    """Ensure field values are sanitized."""
    actual = parsing.sanitize_fatality_entity(input_)
    assert actual == expected
