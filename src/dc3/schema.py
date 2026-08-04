"""Shared DC3 constants and schema definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

THERMAL_SENSATION_TO_LABEL = {
    -3: "A",
    -2: "B",
    -1: "C",
    0: "D",
    1: "E",
    2: "F",
    3: "G",
}

LABEL_TO_THERMAL_SENSATION = {label: value for value, label in THERMAL_SENSATION_TO_LABEL.items()}

THERMAL_SENSATION_DESCRIPTIONS = {
    -3: "cold",
    -2: "cool",
    -1: "slightly cool",
    0: "neutral",
    1: "slightly warm",
    2: "warm",
    3: "hot",
}

PREFERENCE_COOLER = "cooler"
PREFERENCE_NO_CHANGE = "no_change"
PREFERENCE_WARMER = "warmer"

PREFERENCE_GROUPS = {
    PREFERENCE_COOLER: 1,
    PREFERENCE_NO_CHANGE: 2,
    PREFERENCE_WARMER: 3,
}

GROUP_TO_PREFERENCE = {value: key for key, value in PREFERENCE_GROUPS.items()}

REQUIRED_FIELDS = (
    "thermal_sensation",
    "thermal_preference",
    "thermal_acceptability",
)

OPTIONAL_FIELDS = (
    "country",
    "country_code",
    "air_temperature",
    "operative_temperature",
    "radiant_temperature",
    "globe_temperature",
    "relative_humidity",
    "air_velocity",
    "city",
    "latitude",
    "longitude",
    "season",
    "building_type",
    "cooling_strategy",
    "cooling_operation_mode",
    "heating_strategy",
    "koppen_climate",
    "climate",
    "year",
    "age",
    "sex",
    "clo",
    "met",
    "pmv",
    "ppd",
    "set",
    "thermal_comfort",
    "database",
    "publication",
    "data_contributor",
)

ALL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS


@dataclass(frozen=True)
class NormalizedValue:
    """A normalised value together with trace information.

    Attributes
    ----------
    value:
        The canonical value used by the DC3 engine.
    raw:
        The original value supplied by the user or dataset.
    changed:
        Whether normalisation changed the value representation.
    note:
        Optional human-readable explanation of the normalisation.
    """

    value: Any
    raw: Any
    changed: bool = False
    note: str | None = None
