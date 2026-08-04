"""Dataframe validation and batch DC3 processing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import pandas as pd

from dc3.core import classify_dc3, describe_dc3, thermal_sensation_label
from dc3.exceptions import DC3ValidationError
from dc3.preprocessing import (
    normalize_acceptability,
    normalize_preference,
    normalize_thermal_sensation,
)
from dc3.schema import ALL_FIELDS, REQUIRED_FIELDS


@dataclass(frozen=True)
class ValidationReport:
    """Summary of whether a dataframe can be processed.

    Attributes
    ----------
    valid:
        Whether all required mappings and source columns exist.
    missing_required_fields:
        Required canonical fields absent from the mapping.
    missing_columns:
        Source dataframe columns referenced by the mapping but not present.
    mapped_fields:
        Canonical fields that are mapped to source columns.
    row_count:
        Number of rows in the dataframe.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       import pandas as pd
       from dc3 import validate_dataframe

       df = pd.DataFrame(
           {
               "TS": [0],
               "TP": ["no_change"],
               "TA": [1],
           }
       )

       report = validate_dataframe(
           df,
           columns={
               "thermal_sensation": "TS",
               "thermal_preference": "TP",
               "thermal_acceptability": "TA",
           },
       )
       print(report.valid)
       print(report.row_count)

    Expected output:

    .. code-block:: text

       True
       1
    """

    valid: bool
    missing_required_fields: tuple[str, ...]
    missing_columns: tuple[str, ...]
    mapped_fields: tuple[str, ...]
    row_count: int


def validate_dataframe(df: pd.DataFrame, columns: Mapping[str, str]) -> ValidationReport:
    """Validate a dataframe and user column mapping before processing.

    Parameters
    ----------
    df:
        Source pandas dataframe.
    columns:
        Mapping from canonical DC3 field names to source dataframe columns.
        Required keys are ``thermal_sensation``, ``thermal_preference``, and
        ``thermal_acceptability``.

    Returns
    -------
    ValidationReport
        Validation summary. A report with ``valid=True`` can be passed to
        :func:`process_dataframe`.

    .. note::

       Optional fields such as ``country``, ``city``, ``season``, and
       environmental variables can also be mapped. Unknown canonical field
       names raise ``DC3ValidationError`` so misspellings are caught early.

    Examples
    --------
    Valid mapping:

    .. code-block:: python

       # python -m pip install dc3model_v1
       import pandas as pd
       from dc3 import validate_dataframe

       df = pd.DataFrame(
           {
               "Thermal sensation": [0, 1],
               "Thermal preference": ["no_change", "cooler"],
               "Thermal acceptability": [1, 1],
           }
       )
       columns = {
           "thermal_sensation": "Thermal sensation",
           "thermal_preference": "Thermal preference",
           "thermal_acceptability": "Thermal acceptability",
       }

       report = validate_dataframe(df, columns)
       print(report.valid)
       print(report.mapped_fields)

    Expected output:

    .. code-block:: text

       True
       ('thermal_sensation', 'thermal_preference', 'thermal_acceptability')

    Missing mapping:

    .. code-block:: python

       import pandas as pd
       from dc3 import validate_dataframe

       df = pd.DataFrame({"TS": [0]})
       report = validate_dataframe(df, columns={"thermal_sensation": "TS"})
       print(report.valid)
       print(report.missing_required_fields)

    Expected output:

    .. code-block:: text

       False
       ('thermal_preference', 'thermal_acceptability')
    """

    if not isinstance(df, pd.DataFrame):
        raise DC3ValidationError("df must be a pandas DataFrame")
    if not isinstance(columns, Mapping):
        raise DC3ValidationError("columns must be a mapping of canonical field names to dataframe columns")

    unknown_fields = sorted(set(columns) - set(ALL_FIELDS))
    if unknown_fields:
        raise DC3ValidationError(f"unknown canonical field(s): {', '.join(unknown_fields)}")

    missing_required_fields = tuple(field for field in REQUIRED_FIELDS if field not in columns)
    missing_columns = tuple(
        source_column for source_column in columns.values() if source_column not in df.columns
    )
    mapped_fields = tuple(field for field in ALL_FIELDS if field in columns)

    return ValidationReport(
        valid=not missing_required_fields and not missing_columns,
        missing_required_fields=missing_required_fields,
        missing_columns=missing_columns,
        mapped_fields=mapped_fields,
        row_count=len(df),
    )


def process_dataframe(
    df: pd.DataFrame,
    columns: Mapping[str, str],
    *,
    keep_invalid: bool = True,
) -> pd.DataFrame:
    """Return a dataframe with DC3 classifications and validation metadata.

    Invalid rows are retained by default with ``dc3_valid=False`` and a clear
    ``dc3_error`` message. Set ``keep_invalid=False`` to drop invalid rows from
    the returned dataframe.

    Parameters
    ----------
    df:
        Source pandas dataframe.
    columns:
        Mapping from canonical DC3 field names to source dataframe columns.
    keep_invalid:
        Default is ``True``. Invalid rows remain in the returned dataframe
        with ``dc3_valid=False``. Set to ``False`` to return only valid rows.

    Returns
    -------
    pandas.DataFrame
        Original columns plus DC3 outputs such as ``dc3_label``, ``dc3_code``,
        ``observed_comfort``, ``is_z_class``, and ``dc3_error``.

    Examples
    --------
    Small dataframe:

    .. code-block:: python

       # python -m pip install dc3model_v1
       import pandas as pd
       from dc3 import process_dataframe

       df = pd.DataFrame(
           {
               "TS": [0, 1, 0],
               "TP": ["no_change", "cooler", "no_change"],
               "TA": [1, 1, 0],
               "Country": ["India", "India", "India"],
           }
       )
       columns = {
           "thermal_sensation": "TS",
           "thermal_preference": "TP",
           "thermal_acceptability": "TA",
           "country": "Country",
       }

       processed = process_dataframe(df, columns)
       print(processed[["dc3_label", "dc3_code", "observed_comfort", "is_z_class"]].to_string(index=False))

    Expected output:

    .. code-block:: text

        dc3_label  dc3_code  observed_comfort  is_z_class
                D        11              True       False
               E-        13             False       False
                Z        22             False        True

    Drop invalid rows:

    .. code-block:: python

       import pandas as pd
       from dc3 import process_dataframe

       df = pd.DataFrame({"TS": [0, None], "TP": ["no_change", "warmer"], "TA": [1, 1]})
       columns = {
           "thermal_sensation": "TS",
           "thermal_preference": "TP",
           "thermal_acceptability": "TA",
       }

       processed = process_dataframe(df, columns, keep_invalid=False)
       print(len(processed))

    Expected output:

    .. code-block:: text

       1
    """

    report = validate_dataframe(df, columns)
    if not report.valid:
        problems = []
        if report.missing_required_fields:
            problems.append(f"missing required field mapping(s): {', '.join(report.missing_required_fields)}")
        if report.missing_columns:
            problems.append(f"missing dataframe column(s): {', '.join(report.missing_columns)}")
        raise DC3ValidationError("; ".join(problems))

    processed = df.copy()
    rows = [
        _process_row(row, columns)
        for _, row in processed.iterrows()
    ]
    derived = pd.DataFrame(rows, index=processed.index)
    processed = pd.concat([processed, derived], axis=1)

    if keep_invalid:
        return processed
    return processed[processed["dc3_valid"]].copy()


def summarise_dc3(df: pd.DataFrame, *, label_column: str = "dc3_label") -> pd.DataFrame:
    """Summarise DC3 class counts and percentages for a processed dataframe.

    Parameters
    ----------
    df:
        Processed dataframe that contains a DC3 label column.
    label_column:
        Default is ``"dc3_label"``. Change this when summarising a dataframe
        that uses a custom label column name.

    Returns
    -------
    pandas.DataFrame
        Columns: ``dc3_label``, ``count``, and ``percentage``.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       import pandas as pd
       from dc3 import process_dataframe, summarise_dc3

       df = pd.DataFrame({"TS": [0, 0, 1], "TP": ["no_change", "no_change", "cooler"], "TA": [1, 0, 1]})
       columns = {
           "thermal_sensation": "TS",
           "thermal_preference": "TP",
           "thermal_acceptability": "TA",
       }

       processed = process_dataframe(df, columns)
       summary = summarise_dc3(processed)
       print(summary.sort_values("dc3_label").to_string(index=False))

    Expected output:

    .. code-block:: text

        dc3_label  count  percentage
               E-      1   33.333333
                D      1   33.333333
                Z      1   33.333333
    """

    if label_column not in df.columns:
        raise DC3ValidationError(f"{label_column!r} is not present in the dataframe")
    total = len(df)
    counts = df[label_column].fillna("INVALID").value_counts(dropna=False).rename_axis("dc3_label")
    summary = counts.reset_index(name="count")
    summary["percentage"] = 0.0 if total == 0 else summary["count"] / total * 100
    return summary


def _process_row(row: pd.Series, columns: Mapping[str, str]) -> dict:
    try:
        sensation_raw = row[columns["thermal_sensation"]]
        preference_raw = row[columns["thermal_preference"]]
        acceptability_raw = row[columns["thermal_acceptability"]]

        sensation = normalize_thermal_sensation(sensation_raw)
        preference = normalize_preference(preference_raw)
        acceptability = normalize_acceptability(acceptability_raw)
        label = classify_dc3(sensation.value, preference.value, acceptability.value)
        description = describe_dc3(label)
        notes = [
            note
            for note in (sensation.note, preference.note, acceptability.note)
            if note
        ]

        return {
            "observed_comfort": description["observed_comfort"],
            "dc3_label": description["label"],
            "dc3_code": description["code"],
            "thermal_sensation_normalized": sensation.value,
            "thermal_sensation_label": thermal_sensation_label(sensation.value),
            "thermal_preference_normalized": preference.value,
            "thermal_acceptability_normalized": acceptability.value,
            "preference_group": description["preference_group"],
            "comfort_zone": description["comfort_zone"],
            "recommended_direction": description["recommended_direction"],
            "is_z_class": description["is_z_class"],
            "dc3_normalization_note": "; ".join(notes) if notes else None,
            "dc3_valid": True,
            "dc3_error": None,
        }
    except Exception as exc:
        return {
            "observed_comfort": None,
            "dc3_label": None,
            "dc3_code": None,
            "thermal_sensation_normalized": None,
            "thermal_sensation_label": None,
            "thermal_preference_normalized": None,
            "thermal_acceptability_normalized": None,
            "preference_group": None,
            "comfort_zone": None,
            "recommended_direction": None,
            "is_z_class": None,
            "dc3_normalization_note": None,
            "dc3_valid": False,
            "dc3_error": str(exc),
        }
