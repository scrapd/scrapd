"""Define the ScrAPD models."""
import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel
from pydantic import Extra
from pydantic import validator

from scrapd.core import date_utils


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
        # A crash date is required to compute fatality's ages.
        if not self.date:
            return

        for f in self.fatalities:
            # Skip if the fatality already has an age, or if there is no dob.
            if f.age or not f.dob:
                continue

            # Compute the age.
            f.age = date_utils.compute_age(self.date, f.dob)

    def update(self, other):
        """Update a model with values from another one."""
        if not other:
            return

        attrs = ['case', 'crash', 'date', 'fatalities', 'link', 'latitude', 'location', 'longitude', 'notes', 'time']
        for attr in attrs:
            # Case is a special case.
            if attr == 'case':
                setattr(self, attr, getattr(other, attr))
                continue
            if not getattr(self, attr):
                setattr(self, attr, getattr(other, attr))
