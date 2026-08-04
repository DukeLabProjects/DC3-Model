"""Input normalisation helpers for single records and datasets."""

from __future__ import annotations

import math
import re
from typing import Any

from dc3.exceptions import DC3InputError
from dc3.schema import (
    NormalizedValue,
    PREFERENCE_COOLER,
    PREFERENCE_NO_CHANGE,
    PREFERENCE_WARMER,
    THERMAL_SENSATION_DESCRIPTIONS,
)


_MISSING_TEXT = {"", "na", "n/a", "nan", "none", "null", "missing", "-"}

_PREFERENCE_SYNONYMS = {
    PREFERENCE_COOLER: {
        "cooler",
        "cool",
        "colder",
        "cold",
        "prefercooler",
        "prefercold",
        "prefercolder",
        "wantcooler",
        "wantcolder",
        "lesswarm",
        "lesshot",
        "decrease",
        "decreasetemperature",
        "lower",
        "lowertemperature",
        "-1",
    },
    PREFERENCE_NO_CHANGE: {
        "nochange",
        "no_change",
        "same",
        "neutral",
        "comfortable",
        "ok",
        "okay",
        "satisfied",
        "unchanged",
        "neither",
        "none",
        "0",
    },
    PREFERENCE_WARMER: {
        "warmer",
        "warm",
        "hotter",
        "hot",
        "preferwarmer",
        "preferwarm",
        "preferhotter",
        "wantwarmer",
        "wanthotter",
        "lesscool",
        "lesscold",
        "increase",
        "increasetemperature",
        "higher",
        "highertemperature",
        "1",
        "+1",
    },
}

_ACCEPTABLE_TRUE = {
    "1",
    "true",
    "t",
    "yes",
    "y",
    "acceptable",
    "accept",
    "accepted",
    "comfortable",
    "satisfied",
    "ok",
    "okay",
}

_ACCEPTABLE_FALSE = {
    "0",
    "false",
    "f",
    "no",
    "n",
    "unacceptable",
    "notacceptable",
    "reject",
    "rejected",
    "uncomfortable",
    "dissatisfied",
}

_SENSATION_TEXT = {
    "cold": -3,
    "verycold": -3,
    "cool": -2,
    "slightlycool": -1,
    "slightcool": -1,
    "littlecool": -1,
    "neutral": 0,
    "neither": 0,
    "comfortable": 0,
    "slightlywarm": 1,
    "slightwarm": 1,
    "littlewarm": 1,
    "warm": 2,
    "hot": 3,
    "veryhot": 3,
}


def is_missing(value: Any) -> bool:
    """Return whether a value should be treated as missing."""

    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and _compact(value) in _MISSING_TEXT:
        return True
    return False


def normalize_thermal_sensation(value: Any) -> NormalizedValue:
    """Normalise thermal sensation to an integer in the range ``-3`` to ``3``.

    Numeric values on the ASHRAE seven-point range are accepted directly.
    Decimal values such as those present in ASHRAE DB II are discretised to
    the nearest integer state. Common text labels such as ``"slightly cool"``,
    ``"neutral"``, and ``"hot"`` are also accepted.
    """

    if is_missing(value):
        raise DC3InputError("thermal_sensation is missing")

    raw = value
    if isinstance(value, bool):
        raise DC3InputError("thermal_sensation must be one of -3, -2, -1, 0, 1, 2, 3")

    note = None
    if isinstance(value, int):
        sensation = value
    elif isinstance(value, float):
        sensation, note = _discretise_sensation_number(value, raw)
    else:
        text = str(value).strip()
        compact = _compact(text)
        if compact in _SENSATION_TEXT:
            sensation = _SENSATION_TEXT[compact]
        else:
            match = re.search(r"[-+]?\d+(?:\.\d+)?", text)
            if not match:
                raise DC3InputError(f"thermal_sensation {raw!r} is not recognised")
            number = float(match.group(0))
            sensation, note = _discretise_sensation_number(number, raw)

    if sensation not in THERMAL_SENSATION_DESCRIPTIONS:
        raise DC3InputError("thermal_sensation must be one of -3, -2, -1, 0, 1, 2, 3")

    changed = raw != sensation
    return NormalizedValue(
        value=sensation,
        raw=raw,
        changed=changed,
        note=note or ("normalised thermal sensation" if changed else None),
    )


def normalize_preference(value: Any) -> NormalizedValue:
    """Normalise thermal preference to ``cooler``, ``no_change``, or ``warmer``."""

    if is_missing(value):
        raise DC3InputError("thermal_preference is missing")

    raw = value
    compact = _compact(str(value))
    for canonical, variants in _PREFERENCE_SYNONYMS.items():
        if compact in variants:
            changed = raw != canonical
            return NormalizedValue(
                value=canonical,
                raw=raw,
                changed=changed,
                note="normalised thermal preference" if changed else None,
            )

    raise DC3InputError(
        "thermal_preference must mean cooler, no_change, or warmer; "
        f"received {raw!r}"
    )


def normalize_acceptability(value: Any) -> NormalizedValue:
    """Normalise thermal acceptability to ``1`` for acceptable or ``0`` otherwise."""

    if is_missing(value):
        raise DC3InputError("thermal_acceptability is missing")

    raw = value
    if isinstance(value, bool):
        normalised = 1 if value else 0
    elif isinstance(value, int) and value in (0, 1):
        normalised = value
    elif isinstance(value, float) and value in (0.0, 1.0):
        normalised = int(value)
    else:
        compact = _compact(str(value))
        if compact in _ACCEPTABLE_TRUE:
            normalised = 1
        elif compact in _ACCEPTABLE_FALSE:
            normalised = 0
        else:
            raise DC3InputError(
                "thermal_acceptability must mean acceptable/1 or unacceptable/0; "
                f"received {raw!r}"
            )

    changed = raw != normalised
    return NormalizedValue(
        value=normalised,
        raw=raw,
        changed=changed,
        note="normalised thermal acceptability" if changed else None,
    )


def _compact(value: str) -> str:
    return re.sub(r"[^a-z0-9+-]+", "", value.strip().lower())


def _discretise_sensation_number(value: float, raw: Any) -> tuple[int, str | None]:
    if math.isnan(value) or value < -3 or value > 3:
        raise DC3InputError("thermal_sensation must be one of -3, -2, -1, 0, 1, 2, 3")
    if value.is_integer():
        return int(value), None
    rounded = int(math.copysign(math.floor(abs(value) + 0.5), value))
    rounded = max(-3, min(3, rounded))
    return rounded, f"discretised thermal sensation {raw!r} to {rounded}"
