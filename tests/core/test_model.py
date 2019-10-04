"""Test the model module."""
import datetime
from enum import Enum

from faker import Faker
import pytest

from scrapd.core import model
from scrapd.core.constant import Fields

# Set faker object.
fake = Faker()

compute_age_scenarios = [
    {
        'input_': model.Report(
            case='19-123456',
            date=datetime.date(2019, 1, 16),
            fatalities=[
                model.Fatality(dob=datetime.date(1960, 2, 15)),
            ],
        ),
        'expected': [58],
        'id': 'single-regular',
    },
    {
        'input_': model.Report(
            case='19-123456',
            date=datetime.date(2019, 1, 16),
            fatalities=[
                model.Fatality(age=100),
            ],
        ),
        'expected': [100],
        'id': 'single-age-no_dob',
    },
    {
        'input_': model.Report(
            case='19-123456',
            date=datetime.date(2019, 1, 16),
            fatalities=[
                model.Fatality(),
            ],
        ),
        'expected': [0],
        'id': 'no-age-no_dob',
    },
]

update_model_scenarios = [
    {
        'input_': model.Report(case='19-123456', date=datetime.datetime.now().date()),
        'other': model.Report(case='19-123456', date=datetime.datetime.now().date()),
        'expected': model.Report(case='19-123456', date=datetime.datetime.now().date()),
        'id': 'simple',
    },
    {
        'input_': model.Report(case='19-123456', date=datetime.datetime.now().date(), link='link'),
        'other': None,
        'expected': model.Report(case='19-123456', date=datetime.datetime.now().date(), link='link'),
        'id': 'None',
    },
    {
        'input_': model.Report(case='19-123456', date=datetime.datetime.now().date(), link='link'),
        'other': model.Report(case='19-123456', date=datetime.datetime.now().date(), link='other link', crash=1),
        'expected': model.Report(case='19-123456', date=datetime.datetime.now().date(), link='link', crash=1),
        'id': 'complex',
    },
]


class TestFatalityModel:
    """Test the Fatality model."""

    def test_fatality_model_00(self):
        """Ensure an empty model works."""
        m = model.Fatality()
        assert m is not None
        for _, v in m.dict().items():
            assert isinstance(v, Enum) or not v

    def test_fatality_model_01(self):
        """Ensure a full model works."""
        m = model.Fatality(
            age=40,
            dob=datetime.datetime.now().date(),
            ethnicity=model.Ethnicity.undefined,
            first="first",
            gender=model.Gender.undefined,
            generation="generation",
            last="last",
            middle="middle",
        )
        assert m is not None
        for _, v in m.dict().items():
            assert v


class TestFatalityValidator:
    """Tests the Fatality model validators."""

    def test_age_must_be_positive(self):
        """Ensure the age field is always positive."""
        with pytest.raises(ValueError):
            model.Fatality(age=-1)


class TestReportModel:
    """Test the Report model."""

    def test_report_model_00(self):
        """Ensure an empty model works."""
        m = model.Report(case='19-123456', date=datetime.datetime.now().date())
        assert m is not None
        for k, v in m.dict().items():
            if k == Fields.CASE:
                continue
            assert isinstance(v, (Enum, datetime.date)) or not v

    def test_report_model_01(self):
        """Ensure a full model works."""
        m = model.Report(
            case='19-123456',
            date=datetime.datetime.now().date(),
            crash=1,
            latitude=30.222337,
            link=fake.uri(),
            location=fake.pystr(),
            longitude=-97.678343,
            notes=fake.paragraph(),
            time=datetime.datetime.now().time(),
            fatalities=[model.Fatality()],
        )
        assert m is not None
        for _, v in m.dict().items():
            assert v

    @pytest.mark.parametrize(
        'input_,expected',
        [pytest.param(s['input_'], s['expected'], id=s['id']) for s in compute_age_scenarios],
    )
    def test_compute_fatalities_age(self, input_, expected):
        """Ensure ages are computed correctly."""
        input_.compute_fatalities_age()
        assert [f.age for f in input_.fatalities] == expected

    @pytest.mark.parametrize(
        'input_,other,expected',
        [pytest.param(s['input_'], s['other'], s['expected'], id=s['id']) for s in update_model_scenarios],
    )
    def test_update_00(self, input_, other, expected):
        """Ensure models can be updated."""
        actual = input_.copy(deep=True)
        actual.update(other)
        assert actual == expected

    def test_update_01(self):
        """Ensure the case field gets updated."""
        actual = model.Report(case='19-123456', date=datetime.datetime.now().date())
        other = model.Report(case='19-123456', date=datetime.datetime.now().date())
        actual.update(other)
        assert actual == other

    def test_invalid_case_number(self):
        """Ensure the case number has a valid format."""
        with pytest.raises(ValueError):
            model.Report(case='123456', date=datetime.datetime.now().date())

    def test_invalid_date(self):
        """Ensure the report date is valid."""
        with pytest.raises(ValueError):
            model.Report(case='19-123456', date=datetime.date.min)
