import pytest

from dc3.exceptions import DC3InputError
from dc3.preprocessing import (
    normalize_acceptability,
    normalize_preference,
    normalize_thermal_sensation,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("-1", -1),
        ("slightly cool", -1),
        ("neutral", 0),
        ("slightly warm", 1),
        ("hot", 3),
        (2.0, 2),
        (-2.1, -2),
        (-0.5, -1),
        (0.5, 1),
    ],
)
def test_normalize_thermal_sensation(raw, expected):
    assert normalize_thermal_sensation(raw).value == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("prefer cooler", "cooler"),
        ("no change", "no_change"),
        ("same", "no_change"),
        ("want warmer", "warmer"),
        ("+1", "warmer"),
    ],
)
def test_normalize_preference(raw, expected):
    assert normalize_preference(raw).value == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("acceptable", 1),
        ("yes", 1),
        (True, 1),
        ("unacceptable", 0),
        ("no", 0),
        (False, 0),
    ],
)
def test_normalize_acceptability(raw, expected):
    assert normalize_acceptability(raw).value == expected


def test_missing_values_are_rejected():
    with pytest.raises(DC3InputError):
        normalize_thermal_sensation(None)
    with pytest.raises(DC3InputError):
        normalize_preference("")
    with pytest.raises(DC3InputError):
        normalize_acceptability("n/a")
