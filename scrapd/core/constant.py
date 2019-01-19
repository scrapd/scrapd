"""Define the scrapd constants."""
from abc import ABC


class Constant(ABC):
    """Define the constant class."""

    def __setattr__(self, *_):
        """Ensure the attributes are read only.."""
        raise AttributeError('This attribute is read only.')


class Fields(Constant):
    """Define the resource constants."""

    AGE = 'Age'
    CASE = 'Case'
    CRASHES = 'Fatal crashes this year'
    DATE = 'Date'
    DECEASED = 'Deceased'
    DOB = 'DOB'
    ETHNICITY = 'Ethnicity'
    FIRST_NAME = 'First Name'
    GENDER = 'Gender'
    LAST_NAME = 'Last Name'
    LINK = 'Link'
    LOCATION = 'Location'
    NOTES = 'Notes'
    TIME = 'Time'
