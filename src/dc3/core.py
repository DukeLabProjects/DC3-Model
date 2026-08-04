"""Deterministic DC3 classification and encoding logic."""

from __future__ import annotations

from dc3.exceptions import DC3InputError
from dc3.preprocessing import (
    normalize_acceptability,
    normalize_preference,
    normalize_thermal_sensation,
)
from dc3.schema import (
    GROUP_TO_PREFERENCE,
    LABEL_TO_THERMAL_SENSATION,
    PREFERENCE_COOLER,
    PREFERENCE_GROUPS,
    PREFERENCE_NO_CHANGE,
    PREFERENCE_WARMER,
    THERMAL_SENSATION_DESCRIPTIONS,
    THERMAL_SENSATION_TO_LABEL,
)

DC3_STATE_TABLE = {
    f"{label}{suffix}": 3 * index + group
    for index, label in enumerate(["A", "B", "C", "D", "E", "F", "G"])
    for suffix, group in (("-", 1), ("", 2), ("+", 3))
}
DC3_STATE_TABLE["Z"] = 22

CODE_TO_LABEL = {code: label for label, code in DC3_STATE_TABLE.items()}


def observed_comfort(thermal_preference, thermal_acceptability) -> bool:
    """Return the binary Observed Comfort result for one observation.

    The DC3 paper defines an observation as comfortable only when the
    occupant reports no desired thermal change and marks the environment as
    acceptable. Every other combination is treated as uncomfortable for
    operational control purposes.
    """

    preference = normalize_preference(thermal_preference).value
    acceptability = normalize_acceptability(thermal_acceptability).value
    return preference == PREFERENCE_NO_CHANGE and acceptability == 1


def thermal_sensation_label(thermal_sensation) -> str:
    """Return the DC3 letter label ``A`` through ``G`` for thermal sensation."""

    sensation = normalize_thermal_sensation(thermal_sensation).value
    return THERMAL_SENSATION_TO_LABEL[sensation]


def classify_dc3(thermal_sensation, thermal_preference, thermal_acceptability) -> str:
    """Classify one observation into a DC3 label.

    Parameters are normalised before classification, so common input variants
    such as ``"no change"``, ``"acceptable"``, and ``"slightly warm"`` are
    accepted.
    """

    sensation = normalize_thermal_sensation(thermal_sensation).value
    preference = normalize_preference(thermal_preference).value
    acceptability = normalize_acceptability(thermal_acceptability).value

    if preference == PREFERENCE_NO_CHANGE and acceptability == 0:
        return "Z"

    base_label = THERMAL_SENSATION_TO_LABEL[sensation]
    if preference == PREFERENCE_COOLER:
        return f"{base_label}-"
    if preference == PREFERENCE_WARMER:
        return f"{base_label}+"
    if preference == PREFERENCE_NO_CHANGE and acceptability == 1:
        return base_label

    raise DC3InputError("could not classify DC3 state from the supplied inputs")


def encode_dc3(label: str) -> int:
    """Encode a DC3 label into its numeric code."""

    normalised = _normalise_label(label)
    try:
        return DC3_STATE_TABLE[normalised]
    except KeyError as exc:
        raise DC3InputError(f"unknown DC3 label {label!r}") from exc


def decode_dc3(code: int) -> dict:
    """Decode a numeric DC3 code into model components."""

    if isinstance(code, bool):
        raise DC3InputError("DC3 code must be an integer from 1 to 22")

    try:
        numeric_code = int(code)
    except (TypeError, ValueError) as exc:
        raise DC3InputError(f"DC3 code {code!r} is not an integer") from exc

    if numeric_code not in CODE_TO_LABEL:
        raise DC3InputError("DC3 code must be an integer from 1 to 22")

    label = CODE_TO_LABEL[numeric_code]
    return describe_dc3(label)


def describe_dc3(label: str) -> dict:
    """Return a structured description for a DC3 label."""

    label = _normalise_label(label)
    if label == "Z":
        return {
            "label": "Z",
            "code": 22,
            "thermal_sensation": None,
            "thermal_sensation_label": None,
            "thermal_sensation_description": None,
            "preference": PREFERENCE_NO_CHANGE,
            "preference_group": None,
            "observed_comfort": False,
            "is_z_class": True,
            "comfort_zone": "z_class",
            "recommended_direction": "review_response",
        }

    if label not in DC3_STATE_TABLE:
        raise DC3InputError(f"unknown DC3 label {label!r}")

    letter = label[0]
    suffix = label[1:]
    sensation = LABEL_TO_THERMAL_SENSATION[letter]
    preference = _preference_from_suffix(suffix)
    preference_group = PREFERENCE_GROUPS[preference]
    is_comfortable = suffix == ""

    return {
        "label": label,
        "code": DC3_STATE_TABLE[label],
        "thermal_sensation": sensation,
        "thermal_sensation_label": letter,
        "thermal_sensation_description": THERMAL_SENSATION_DESCRIPTIONS[sensation],
        "preference": preference,
        "preference_group": preference_group,
        "observed_comfort": is_comfortable,
        "is_z_class": False,
        "comfort_zone": _comfort_zone(sensation, is_comfortable),
        "recommended_direction": _recommended_direction(preference),
    }


def dc3_codebook(*, as_dataframe: bool = False):
    """Return the full DC3 label/code equivalence table.

    Parameters
    ----------
    as_dataframe:
        When true, return a pandas dataframe. By default a list of dictionaries
        is returned so the core codebook has no hard dependency on pandas.
    """

    rows = []
    for label in DC3_STATE_TABLE:
        description = describe_dc3(label)
        rows.append(
            {
                "dc3_label": description["label"],
                "dc3_code": description["code"],
                "thermal_sensation": description["thermal_sensation"],
                "thermal_sensation_label": description["thermal_sensation_label"],
                "thermal_sensation_description": description["thermal_sensation_description"],
                "preference": description["preference"],
                "preference_group": description["preference_group"],
                "observed_comfort": description["observed_comfort"],
                "comfort_zone": description["comfort_zone"],
                "recommended_direction": description["recommended_direction"],
                "is_z_class": description["is_z_class"],
            }
        )

    if as_dataframe:
        import pandas as pd

        return pd.DataFrame(rows)
    return rows


def _normalise_label(label: str) -> str:
    if label is None:
        raise DC3InputError("DC3 label is missing")
    normalised = str(label).strip().upper().replace(" ", "")
    if normalised in {"Z", "Z-CLASS", "ZCLASS"}:
        return "Z"
    if len(normalised) == 1 and normalised in LABEL_TO_THERMAL_SENSATION:
        return normalised
    if len(normalised) == 2 and normalised[0] in LABEL_TO_THERMAL_SENSATION and normalised[1] in {"-", "+"}:
        return normalised
    raise DC3InputError(f"unknown DC3 label {label!r}")


def _preference_from_suffix(suffix: str) -> str:
    if suffix == "-":
        return PREFERENCE_COOLER
    if suffix == "+":
        return PREFERENCE_WARMER
    if suffix == "":
        return PREFERENCE_NO_CHANGE
    raise DC3InputError(f"unknown DC3 suffix {suffix!r}")


def _comfort_zone(sensation: int, is_comfortable: bool) -> str:
    if is_comfortable and sensation in {-1, 0, 1}:
        return "most_comfortable_zone"
    if is_comfortable:
        return "comfortable"
    return "transitional"


def _recommended_direction(preference: str) -> str:
    if preference == PREFERENCE_COOLER:
        return "cooler"
    if preference == PREFERENCE_WARMER:
        return "warmer"
    if preference == PREFERENCE_NO_CHANGE:
        return "maintain"
    raise DC3InputError(f"unknown preference {preference!r}")
