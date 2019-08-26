"""Define the data for the mocks."""

twitter_title_00 = "Traffic Fatality #73"
twitter_description_00 = """
Case:           18-3640187 Date:            December 30, 2018 Time:            2:24 a.m. Location:     1400 E. Highway
 71 eastbound Deceased:   Corbin Sabillon-Garcia, White male, DOB 02/09/80   The preliminary investigation shows that a
 2003 Ford F150 was traveling northbound on the US Highway 183 northbound ramp to E. Highway 71, eastbound. The truck
 went across the E. Highway 71 and US Highway 183 ramp, rolled and came to a stop north of the roadway.
"""
twitter_description_01 = "Case:           19-0161105"
twitter_description_02 = (
    "Case:            18-160882 Date:             Tuesday, January 16, 2018 "
    "Time:             5:14 p.m. Location:      1500 W. Slaughter Lane Deceased:     Eva Marie Gonzales, W/F, "
    "DOB: 01-22-1961 (passenger)")
twitter_description_03 = (
    "APD is asking any businesses in the area of East Cesar Chavez and Adam L. Chapa Sr. streets "
    "to check their surveillance cameras between 2 and 2:10 a.m. on Oct. 10, 2018, for this suspect vehicle. "
    "See video of suspect vehicle here --&gt; https://youtu.be/ezxaRW79PnI")
note_fields_scenarios = [
    (
        (
            '<p>	<strong><span style="font-family: &quot;Verdana&quot;,sans-serif;">Deceased:</span></strong>&nbsp; &nbsp;'
            'Ann Bottenfield-Seago, White female, DOB 02/15/1960<br>'
            '&nbsp;<br>'
            'The preliminary investigation shows that the grey, 2003 Volkwagen Jetta being driven by Ann Bottenfield-Seago '
            'failed to yield at a stop sign while attempting to turn westbound on to West William Cannon Drive from Ridge Oak '
            'Road. The Jetta collided with a black, 2017 Chevrolet truck that was eastbound in the inside lane of West William '
            'Cannon Drive. Bottenfield-Seago was pronounced deceased at the scene. The passenger in the Jetta and the driver '
            'of the truck were both transported to a local hospital with non-life threatening injuries. No charges are '
            'expected to be filed.<br>'
            '&nbsp;<br>'
            'APD is investigating this case. Anyone with information regarding this case should call APD’s Vehicular Homicide '
            'Unit Detectives at (512) 974-3761. You can also submit tips by downloading APD’s mobile app, Austin PD, for free '
            'on <a href="https://austintexas.us5.list-manage.com/track/click?'
            'u=1861810ce1dca1a4c1673747c&amp;id=d8c2ad5a29&amp;e=bcdeacc118"><span style="color: rgb(197, 46, 38); '
            'text-decoration: none; text-underline: none;">iPhone</span></a> and '
            '<a href="https://austintexas.us5.list-manage.com/track/click?'
            'u=1861810ce1dca1a4c1673747c&amp;id=5fcb8ff99e&amp;e=bcdeacc118"><span style="color: rgb(197, 46, 38); '
            'text-decoration: none; text-underline: none;">Android</span></a>.<br>'
            '&nbsp;<br>'
            'This is Austin’s second fatal traffic crash of 2018, resulting&nbsp;in two fatalities this year. At this time in '
            '2018, there were two fatal traffic crashes and three traffic fatalities.<br>'
            '&nbsp;<br><strong><i><span style="font-family: &quot;Verdana&quot;,sans-serif;">These statements are based on the '
            'initial assessment of the fatal crash and investigation is still pending. Fatality information may change.</span>'
            '</i></strong></p>',
            'The preliminary',
            'to be filed.',
        ),
        'One paragraph',
    ),
    (
        (
            '<div class="field-item even" property="content:encoded"><p><strong>Case:&nbsp;&nbsp; &nbsp; &nbsp; &nbsp; '
            '</strong>19-0921776</p>'
            '<p>	<strong>Date:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</strong>April 2, 2019</p>'
            '<p>	<strong>Time:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; </strong>10:01 p.m.</p>'
            '<p>	<strong>Location:&nbsp; &nbsp; </strong>517 E. Slaughter Lane</p>'
            '<p>	<strong>Deceased:&nbsp; </strong>Garrett Evan Davis | White male | 06/24/1991<br>'
            '&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Keaton Michael Carnley | White male | '
            '11/13/1991&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; '
            '&nbsp;&nbsp;&nbsp;<br>'
            '&nbsp;<br>'
            'The preliminary investigation indicated that Garrett Davis, the driver of the 2017 Subaru Forester, was '
            'traveling eastbound in the 500 block of E. Slaughter Lane when he attempted to turn left and collided with a '
            '1996 Chevrolet truck that was traveling westbound. Mr. Davis was attempting to enter the apartment complex on '
            'the south side of the road when he failed to yield right of way. The truck made contact with the passenger '
            'side of the Forester, killing both the driver and passenger, Keaton Carnley. There were no other occupants in '
            'the Subaru. The driver of the truck suffered minor injuries. All parties were wearing their seatbelts. No '
            'charges are expected to be filed.<br>'
            '&nbsp;<br>'
            'Anyone with information regarding this case should call APD’s Vehicular Homicide Unit Detectives at '
            '(512) 974-5594. You can also submit tips by downloading APD’s mobile app, Austin PD, for free on '
            '<a href="https://austintexas.us5.list-manage.com/track/click'
            '?u=1861810ce1dca1a4c1673747c&amp;id=8154f31561&amp;e=bcdeacc118">iPhone</a> and '
            '<a href="https://austintexas.us5.list-manage.com/track/click'
            '?u=1861810ce1dca1a4c1673747c&amp;id=aa72a05df5&amp;e=bcdeacc118">Android</a>.&nbsp;</p>'
            '<p>	This is Austin’s 15<sup>th</sup> fatal traffic crash of 2019, resulting in 15 fatalities this year. '
            'At this time in 2018, there were 15 fatal traffic crashes and 16 traffic fatalities.</p>'
            '<p>	<em><strong>These statements are from the initial assessment of the fatal crash and investigation is '
            'still pending. Fatality information may change.</strong></em><br>'
            '&nbsp;</p>'
            '</div>',
            'The preliminary investigation indicated that Garrett',
            'No charges are expected to be filed.',
        ),
        'Two deaths',
    ),
    (
        (
            '<p>	<strong>Deceased:&nbsp;</strong>&nbsp;Laura Wray, White female, DOB 12/31/1960&nbsp;</p>'
            '<p>	The preliminary investigation shows that a black, Ford F-150 was traveling southbound on IH-35. A '
            'pedestrian, identified as 58-year-old Laura Wray, was traveling eastbound near the 6900 block of N IH-35, when'
            ' the vehicle struck her. The victim was pronounced deceased at the scene at 01:48 a.m.</p>'
            '<p>	APD is investigating this case. Anyone with information regarding this case should call APD’s '
            'Vehicular Homicide Unit Detectives at (512) 974-3761. You can also submit tips by downloading APD’s mobile '
            'app, Austin PD, for free on iPhone and Android.</p>'
            '<p>	This is Austin’s fourth fatal traffic crash of 2019, resulting in four fatalities this year. At this '
            'time in 2018, there were three fatal traffic crashes and four traffic fatalities.</p>',
            'The preliminary',
            'scene at 01:48 a.m.',
        ),
        'Two paragraphs',
    ),
]
