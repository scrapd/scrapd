"""Test the regex module."""
import pytest

from scrapd.core import regex


@pytest.mark.parametrize('input_,expected', (
    ('<p><strong>Case:         </strong>19-0881844</p>', '19-0881844'),
    ('<p><strong>Case:</strong>           18-3640187</p>', '18-3640187'),
    ('<strong>Case:</strong></span><span style="color: rgb(32, 32, 32); '
     'font-family: &quot;Verdana&quot;,sans-serif; font-size: 10.5pt; '
     'mso-fareast-font-family: &quot;Times New Roman&quot;; '
     'mso-ansi-language: EN-US; mso-fareast-language: EN-US; mso-bidi-language: AR-SA; '
     'mso-bidi-font-family: &quot;Times New Roman&quot;;">           19-0161105</span></p>', '19-0161105'),
    ('<p><strong>Case:</strong>            18-1591949 </p>', '18-1591949'),
    ('<p><strong>Case:</strong>            18-590287<br />', '18-590287'),
))
def test_parse_case_field_00(input_, expected):
    """Ensure a case field gets parsed correctly."""
    actual = regex.match_case_field(input_)
    assert actual == expected


@pytest.mark.parametrize(
    'input_, expected',
    (('<span property="dc:title" content="Traffic Fatality #12" class="rdf-meta element-hidden"></span>', '12'), ))
def test_parse_crashes_field_00(input_, expected):
    """Ensure the crashes field gets parsed correctly."""
    actual = regex.match_crash_field(input_)
    assert actual == expected


@pytest.mark.parametrize('input_,expected', (
    (
        '>Location:</span></strong>     West William Cannon Drive and Ridge Oak Road</p>',
        'West William Cannon Drive and Ridge Oak Road',
    ),
    (
        '>Location:</strong>     183 service road westbound and Payton Gin Rd.</p>',
        '183 service road westbound and Payton Gin Rd.',
    ),
    (
        '<p>	<strong>Location:  </strong>8900 block of N Capital of Texas Highway   </p>',
        '8900 block of N Capital of Texas Highway   ',
    ),
))
def test_parse_location_field_00(input_, expected):
    """Ensure."""
    actual = regex.match_location_field(input_)
    assert actual == expected
