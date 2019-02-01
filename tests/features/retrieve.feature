@integrations
Feature: Retrieve
  As a user, I want to retrieve fatality information from the APD news
  website http://austintexas.gov/department/news/296.

  Scenario: Retrieve information
    Given the user wants to store the results in <format>
    And retrieve the fatality details from <from_date> to <to_date>
    Then the generated file must contain <entry_count> entries

    Examples:
      | format | from_date   | to_date     | entry_count |
      | csv    | Jan 15 2019 | Jan 18 2019 | 2           |
      | json   | Jan 2018    | Dec 2018    | 71          |
      | python |             | Feb 2017    | 3           |
