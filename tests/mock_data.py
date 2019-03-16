"""Define the data for the mocks."""

twitter_title_00 = "Traffic Fatality #73"
twitter_description_00 = """
Case:           18-3640187 Date:            December 30, 2018 Time:            2:24 a.m. Location:     1400 E. Highway
 71 eastbound Deceased:   Corbin Sabillon-Garcia, White male, DOB 02/09/80   The preliminary investigation shows that a
 2003 Ford F150 was traveling northbound on the US Highway 183 northbound ramp to E. Highway 71, eastbound. The truck
 went across the E. Highway 71 and US Highway 183 ramp, rolled and came to a stop north of the roadway.
"""
twitter_description_01 = "Case:           19-0161105"
twitter_description_02 = "Case:            18-160882 Date:             Tuesday, January 16, 2018 Time:             5:14 p.m. Location:      1500 W. Slaughter Lane Deceased:     Eva Marie Gonzales, W/F, DOB: 01-22-1961 (passenger)"
twitter_description_03 = "APD is asking any businesses in the area of East Cesar Chavez and Adam L. Chapa Sr. streets to check their surveillance cameras between 2 and 2:10 a.m. on Oct. 10, 2018, for this suspect vehicle. See video of suspect vehicle here --&gt; https://youtu.be/ezxaRW79PnI"
details_page_notes_01 = "<><>"
details_page_notes_02 = """>Deceased:</strong>   Corbin Sabillon-Garcia, White male, DOB 02/09/80<br />
	 <br />
	The preliminary investigation shows that a 2003 Ford F150 was traveling northbound on the US Highway 183 northbound ramp to E. Highway 71, eastbound. The truck went across the E. Highway 71 and US Highway 183 ramp, rolled and came to a stop north of the roadway.</p>
<p>	The passenger was ejected from the vehicle and was pronounced deceased on scene at 2:43 a.m.
The driver was transported to St. David’s South Austin Hospital. <br />
	 <br />
	APD is investigating this case. Anyone with information regarding this case should call APD’s
    Vehicular Homicide Unit Detectives at (512) 974-3761. You can also submit tips by downloading
    APD’s mobile app, Austin PD, for free on
    <a href="https://austintexas.us5.list-manage.com/track/click?u=1861810ce1dca1a4c1673747c&amp;id=6b5f339843&amp;e=bcdeacc118">iPhone</a>
    and <a href="https://austintexas.us5.list-manage.com/track/click?u=1861810ce1dca1a4c1673747c&amp;id=c80053e607&amp;e=bcdeacc118">Android</a>.<br />
	 <br />
	This is Austin’s 73rd fatal traffic crash of 2018, resulting in 74 fatalities this year. At this time in 2017, there were 71 fatal traffic crashes and 76 traffic fatalities.<br />
	 <br /><strong><em>These statements are based on the initial assessment of the fatal crash and investigation is still pending. Fatality information may change.</em></strong></p>
"""

details_page_notes_02_expected = (
    'The passenger was ejected from the vehicle and was pronounced deceased '
    'on scene at 2:43 a.m. The driver was transported to St. David’s South Austin Hospital. '
    'APD is investigating this case. Anyone with information regarding this case should call '
    'APD’s Vehicular Homicide Unit Detectives at (512) 974-3761. You can also submit tips by '
    'downloading APD’s mobile app, Austin PD, for free on iPhone and Android. This is Austin’s '
    '73rd fatal traffic crash of 2018, resulting in 74 fatalities this year. At this time in 2017, '
    'there were 71 fatal traffic crashes and 76 traffic fatalities. These statements are based on '
    'the initial assessment of the fatal crash and investigation is still pending. Fatality information may change.')

duplicated_entry_list_01 = [
    {
        'Case': '18-0280382',
        'Fatal crashes this year': '4',
        'Date': '01/28/2018',
        'Location': '3600 S. Mopac Frontage Rd Sb',
        'Time': '5:00 a.m.',
        'DOB': '11/25/1975',
        'Gender': 'male',
        'Ethnicity': 'Black',
        'Last Name': 'Kagai',
        'First Name': 'Charles',
        'Notes': 'The preliminary investigation shows that a silver, 2011 Toyota 4Runner'
        ' was traveling southbound on the frontage road of Mopac in the 3600 block when it left the roadway. The 4Runner continued southbound in the grass median until it hit several'
        ' trees that eventually stopped the vehicle. The vehicle caught fire as a result of the crash killing the driver who was the only occupant.',
        'Age': 42,
        'Link': 'http://austintexas.gov/news/traffic-fatality-4-5'
    },
    {
        'Case': '18-0280382',
        'Fatal crashes this year': '4',
        'Date': '01/28/2018',
        'Location': '3600 S. Mopac Frontage Rd Sb',
        'Time': '5:00 a.m.',
        'DOB': '11/25/1975',
        'Gender': 'male',
        'Ethnicity': 'Black',
        'Last Name': 'Kagai',
        'First Name': 'Charles'
    },
    {
        'Case': '18-2450389',
        'Fatal crashes this year': '47',
        'Date': '09/02/2018',
        'Location': '12200 Dessau Rd',
        'Time': '4:21 a.m.',
        'DOB': '06/16/1978',
        'Gender': 'male',
        'Ethnicity': 'Black',
        'Last Name': 'Reed-Harper',
        'First Name': 'Anthony',
        'Notes': 'APD is investigating this case. Anyone with information regarding this case is asked to call the APD Vehicular Homicide Unit Detectives at (512) 974-5576. You can also submit tips by downloading APD’s mobile app, Austin PD, for free on iPhone and Android. This is Austin’s forty-seventh fatal traffic crash of 2018, resulting in forty-eight fatalities this year.',
        'Age': 40,
        'Link': 'http://austintexas.gov/news/traffic-fatality-47-5'
    },
    {
        'Case': '18-2450389',
        'Fatal crashes this year': '47',
        'Date': '09/02/2018',
        'Location': '12200 Dessau Rd.',
        'Time': '4:21 a.m.',
        'DOB': '06/16/1978',
        'Gender': 'male',
        'Ethnicity': 'Black',
        'Last Name': 'Reed-Harper',
        'First Name': 'Anthony',
        'Notes': 'APD is investigating this case. Anyone with information regarding this case is asked to call the APD Vehicular Homicide Unit Detectives at (512) 974-5576. You can also submit tips by downloading APD’s mobile app, Austin PD, for free on iPhone and Android. This is Austin’s forty-seventh fatal traffic crash of 2018, resulting in forty-eight fatalities this year. At this time in 2017, there were forty-one fatal traffic crashes and forty-three traffic fatalities. These statements are based on the initial assessment of the fatal crash and investigation is still pending. Fatality information may change.',
        'Age': 40,
        'Link': 'http://austintexas.gov/news/traffic-fatality-47-5'
    }
]

duplicated_entry_list_expected_01 = [
    {
        'Case': '18-0280382',
        'Fatal crashes this year': '4',
        'Date': '01/28/2018',
        'Location': '3600 S. Mopac Frontage Rd Sb',
        'Time': '5:00 a.m.',
        'DOB': '11/25/1975',
        'Gender': 'male',
        'Ethnicity': 'Black',
        'Last Name': 'Kagai',
        'First Name': 'Charles',
        'Notes': 'The preliminary investigation shows that a silver, 2011 Toyota 4Runner was traveling southbound on the frontage road of Mopac in the 3600 block when it left the roadway. The 4Runner continued southbound in the grass median until it hit several trees that eventually stopped the vehicle. The vehicle caught fire as a result of the crash killing the driver who was the only occupant.',
        'Age': 42,
        'Link': 'http://austintexas.gov/news/traffic-fatality-4-5'
    },
    {
        'Case': '18-2450389',
        'Fatal crashes this year': '47',
        'Date': '09/02/2018',
        'Location': '12200 Dessau Rd.',
        'Time': '4:21 a.m.',
        'DOB': '06/16/1978',
        'Gender': 'male',
        'Ethnicity': 'Black',
        'Last Name': 'Reed-Harper',
        'First Name': 'Anthony',
        'Notes': 'APD is investigating this case. Anyone with information regarding this case is asked to call the APD Vehicular Homicide Unit Detectives at (512) 974-5576. You can also submit tips by downloading APD’s mobile app, Austin PD, for free on iPhone and Android. This is Austin’s forty-seventh fatal traffic crash of 2018, resulting in forty-eight fatalities this year. At this time in 2017, there were forty-one fatal traffic crashes and forty-three traffic fatalities. These statements are based on the initial assessment of the fatal crash and investigation is still pending. Fatality information may change.',
        'Age': 40,
        'Link': 'http://austintexas.gov/news/traffic-fatality-47-5'
    }
]
