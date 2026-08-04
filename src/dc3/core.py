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

    Parameters
    ----------
    thermal_preference:
        Thermal preference vote. Accepted values include ``"cooler"``,
        ``"warmer"``, ``"no_change"``, ``"no change"``, ``-1``, ``0``,
        and ``1``.
    thermal_acceptability:
        Acceptability vote. Accepted values include ``1``, ``0``,
        ``True``, ``False``, ``"acceptable"``, and ``"unacceptable"``.

    Returns
    -------
    bool
        ``True`` when the occupant is observed as comfortable.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       from dc3 import observed_comfort

       print(observed_comfort("no_change", 1))
       print(observed_comfort("cooler", 1))

    Expected output:

    .. code-block:: text

       True
       False
    """

    preference = normalize_preference(thermal_preference).value
    acceptability = normalize_acceptability(thermal_acceptability).value
    return preference == PREFERENCE_NO_CHANGE and acceptability == 1


def thermal_sensation_label(thermal_sensation) -> str:
    """Return the DC3 letter label ``A`` through ``G`` for thermal sensation.

    Parameters
    ----------
    thermal_sensation:
        Thermal sensation vote on the ASHRAE 7-point scale. Accepted values
        include integers from ``-3`` to ``3`` and common labels such as
        ``"cold"``, ``"neutral"``, and ``"hot"``.

    Returns
    -------
    str
        The DC3 sensation letter. ``A`` is coldest, ``D`` is neutral, and
        ``G`` is hottest.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       from dc3 import thermal_sensation_label

       print(thermal_sensation_label(-3))
       print(thermal_sensation_label("neutral"))
       print(thermal_sensation_label("hot"))

    Expected output:

    .. code-block:: text

       A
       D
       G
    """

    sensation = normalize_thermal_sensation(thermal_sensation).value
    return THERMAL_SENSATION_TO_LABEL[sensation]


def classify_dc3(thermal_sensation, thermal_preference, thermal_acceptability) -> str:
    """Classify one observation into a DC3 label.

    Parameters are normalised before classification, so common input variants
    such as ``"no change"``, ``"acceptable"``, and ``"slightly warm"`` are
    accepted.

    Parameters
    ----------
    thermal_sensation:
        Thermal sensation vote on the 7-point scale, from cold ``-3`` to hot
        ``3``.
    thermal_preference:
        Desired direction of change: ``"cooler"``, ``"no_change"``, or
        ``"warmer"``. Text variants such as ``"no change"`` are accepted.
    thermal_acceptability:
        Acceptability vote. Use ``1``/``True`` for acceptable and
        ``0``/``False`` for unacceptable.

    Returns
    -------
    str
        DC3 label such as ``"D"``, ``"E-"``, or ``"Z"``.

    .. note::

       ``Z`` is returned when the occupant asks for no change but marks the
       condition unacceptable. This is preserved as a review/flag class.

    Examples
    --------
    Single datapoint:

    .. code-block:: python

       # python -m pip install dc3model_v1
       from dc3 import classify_dc3

       label = classify_dc3(
           thermal_sensation=0,
           thermal_preference="no_change",
           thermal_acceptability=1,
       )
       print(label)

    Expected output:

    .. code-block:: text

       D

    Z-class datapoint:

    .. code-block:: python

       from dc3 import classify_dc3

       print(classify_dc3(0, "no_change", 0))

    Expected output:

    .. code-block:: text

       Z
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
    """Encode a DC3 label into its numeric code.

    Parameters
    ----------
    label:
        DC3 class label, for example ``"A-"``, ``"D"``, ``"G+"``, or
        ``"Z"``.

    Returns
    -------
    int
        Numeric DC3 code from ``1`` to ``22``.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       from dc3 import encode_dc3

       print(encode_dc3("D"))
       print(encode_dc3("Z"))

    Expected output:

    .. code-block:: text

       11
       22
    """

    normalised = _normalise_label(label)
    try:
        return DC3_STATE_TABLE[normalised]
    except KeyError as exc:
        raise DC3InputError(f"unknown DC3 label {label!r}") from exc


def decode_dc3(code: int) -> dict:
    """Decode a numeric DC3 code into model components.

    Parameters
    ----------
    code:
        Integer DC3 code from ``1`` to ``22``.

    Returns
    -------
    dict
        Structured DC3 description with label, thermal sensation,
        preference, observed comfort, and recommended direction.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       from dc3 import decode_dc3

       decoded = decode_dc3(11)
       print(decoded["label"])
       print(decoded["thermal_sensation"])
       print(decoded["observed_comfort"])

    Expected output:

    .. code-block:: text

       D
       0
       True
    """

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
    """Return a structured description for a DC3 label.

    Parameters
    ----------
    label:
        DC3 class label such as ``"C+"``, ``"D"``, or ``"Z"``.

    Returns
    -------
    dict
        Model components for the label, including ``code``,
        ``observed_comfort``, ``comfort_zone``, and
        ``recommended_direction``.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       from dc3 import describe_dc3

       description = describe_dc3("E-")
       print(description["code"])
       print(description["thermal_sensation_description"])
       print(description["recommended_direction"])

    Expected output:

    .. code-block:: text

       13
       slightly warm
       cooler
    """

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
        Default is ``False``. When ``True``, return a pandas dataframe. By
        default, a list of dictionaries is returned so the core codebook has
        no hard dependency on pandas.

    Returns
    -------
    list[dict] or pandas.DataFrame
        Complete codebook for labels ``A-`` through ``G+`` and ``Z``.

    Examples
    --------
    Default list output:

    .. code-block:: python

       # python -m pip install dc3model_v1
       from dc3 import dc3_codebook

       codebook = dc3_codebook()
       print(len(codebook))
       print(codebook[10]["dc3_label"], codebook[10]["dc3_code"])

    Expected output:

    .. code-block:: text

       22
       D 11

    Dataframe output:

    .. code-block:: python

       from dc3 import dc3_codebook

       codebook = dc3_codebook(as_dataframe=True)
       print(codebook.loc[codebook["dc3_label"] == "Z", "dc3_code"].iloc[0])

    Expected output:

    .. code-block:: text

       22
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
