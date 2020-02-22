"""Define the ScrAPD models."""
import datetime
from enum import Enum
import re
from typing import List

from pydantic import BaseModel
from pydantic import Extra
from pydantic import validator

from scrapd.core import date_utils
from scrapd.core import regex


class ModelConfig:
    """Represents the Pydantic model configuration."""

    validate_assignment = True
    extra = Extra.ignore


class Gender(Enum):
    """Define a person's gender."""

    undefined = 'Undefined'
    male = 'Male'
    female = 'Female'


class Ethnicity(Enum):
    """Define a person's ethinicity."""

    undefined = 'Undefined'
    asian = 'Asian'
    black = 'Black'
    eastern = 'Eastern'
    hispanic = 'Hispanic'
    other = 'Other'
    white = 'White'


# @dataclass(config=DataclassConfig)
class Fatality(BaseModel):
    """Define a a person who died in a crash."""

    age: int = 0
    dob: datetime.date = None
    ethnicity: Ethnicity = Ethnicity.undefined
    first: str = ''
    gender: Gender = Gender.undefined
    generation: str = ''
    last: str = ''
    middle: str = ''

    class Config(ModelConfig):
        """Represents the Pydantic model configuration."""

    @validator('age', pre=True, always=True)
    def must_be_positive(cls, v):  # pylint: disable=no-self-argument
        """Ensure a field is positive."""
        if v < 0:
            raise ValueError('must be positive')
        return v


# @dataclass(config=DataclassConfig)
class Report(BaseModel):
    """Define a report."""

    case: str
    crash: int = 0
    date: datetime.date = None
    fatalities: List[Fatality] = []
    link: str = ''
    latitude: float = 0.0
    location: str = ''
    longitude: float = 0.0
    notes: str = ''
    time: datetime.time = None

    class Config(ModelConfig):
        """Represents the Pydantic model configuration."""

    def compute_fatalities_age(self):
        """Compute the ages of all fatalities in a report."""
        for f in self.fatalities:
            # Skip if the fatality already has an age, or if there is no dob.
            if f.age or not f.dob:
                continue

            # Compute the age.
            f.age = date_utils.compute_age(self.date, f.dob)

    def update(self, other, strict=False):
        """
        Update a model in place with values from another one.

        Updates only the empty values of the `self` instance with the non-empty values of the `other` instance.

        :param Report other: report to update with
        :param bool strict: strict mode
        """
        # Do nothing if there is no other instance to update from.
        if not other:
            return

        # Ensure other instance has the right type.
        if not isinstance(other, Report):
            raise TypeError(f'other instance is not of type "Report": {type(other)}')

        # Define the list of attrs.
        required_attrs = ['case']
        attrs = ['crash', 'date', 'fatalities', 'link', 'latitude', 'location', 'longitude', 'notes', 'time']

        # When strict...
        if strict:
            # The case number must be identical.
            if not all([getattr(self, attr) == getattr(other, attr) for attr in required_attrs]):
                raise ValueError(
                    f'in strict mode the required attributes "({", ".join(required_attrs)})" must be identical')
        else:
            # Otherwise the required attributes are overridden.
            for attr in required_attrs:
                setattr(self, attr, getattr(other, attr))

        # Set the non-empty attributes of `other` into the empty attributes of the current instance.
        for attr in attrs:
            # Fatalities are a special case because we cannot simply update their attributes individually.
            # Therefore it is all or nothing, but we want to make sure we do not update it with empty values.
            if attr == 'fatalities':
                if getattr(other, attr):
                    setattr(self, attr, getattr(other, attr))
            elif not getattr(self, attr) and getattr(other, attr):
                setattr(self, attr, getattr(other, attr))

    @validator('case')
    def valid_case_number(cls, v):  # pylint: disable=no-self-argument
        """Ensure a case number is valid."""
        pattern = re.compile(r"(\d{2}-\d{3,7})")
        if not regex.match_pattern(v, pattern):
            raise ValueError('invalid format: "{v}"')
        return v

    @validator('date')
    def valid_date(cls, v):  # pylint: disable=no-self-argument
        """Ensure a case number is valid."""
        if v.year < 2000:
            raise ValueError(f'invalid date: "{v}"')
        return v
