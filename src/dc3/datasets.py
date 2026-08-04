"""Sample and reference dataset helpers."""

from __future__ import annotations

import json
import zipfile
from importlib import resources
from io import BytesIO
from pathlib import Path
from typing import Iterable, Mapping

import pandas as pd

ASHRAE_DB2_FILENAME = "ashrae_db2.csv"

ASHRAE_DB2_ATTRIBUTION = """ASHRAE Global Thermal Comfort Database II attribution

Dataset citation:
Parkinson, Thomas; Tartarini, Federico; Foeldvary Licina, Veronika et al.
(2022). ASHRAE global database of thermal comfort field measurements
[Dataset]. Dryad. https://doi.org/10.6078/D1F671

Primary reference:
Foeldvary Licina, V. et al. (2018). Development of the ASHRAE Global
Thermal Comfort Database II. Building and Environment, 142, 502-512.
https://doi.org/10.1016/j.buildenv.2018.06.022

Source:
Dryad dataset page: https://datadryad.org/dataset/doi:10.6078/D1F671
Official repository: https://github.com/CenterForTheBuiltEnvironment/ashrae-db-II

Notes:
The ASHRAE Global Thermal Comfort Database II combines indoor environmental
measurements with right-here-right-now subjective occupant evaluations from
buildings around the world. Any redistributed subset or derived work should
retain this attribution note and follow the source dataset license/terms.
"""

ASHRAE_DEFAULT_MAPPING = {
    "thermal_sensation": "Thermal sensation",
    "thermal_preference": "Thermal preference",
    "thermal_acceptability": "Thermal sensation acceptability",
    "country": "Country",
    "city": "City",
    "season": "Season",
    "building_type": "Building type",
    "cooling_strategy": "Cooling startegy_building level",
    "cooling_operation_mode": "Cooling startegy_operation mode for MM buildings",
    "heating_strategy": "Heating strategy_building level",
    "koppen_climate": "Koppen climate classification",
    "climate": "Climate",
    "year": "Year",
    "age": "Age",
    "sex": "Sex",
    "air_temperature": "Air temperature (C)",
    "operative_temperature": "Operative temperature (C)",
    "radiant_temperature": "Radiant temperature (C)",
    "globe_temperature": "Globe temperature (C)",
    "relative_humidity": "Relative humidity (%)",
    "air_velocity": "Air velocity (m/s)",
    "clo": "Clo",
    "met": "Met",
    "pmv": "PMV",
    "ppd": "PPD",
    "set": "SET",
    "thermal_comfort": "Thermal comfort",
    "database": "Database",
    "publication": "Publication (Citation)",
    "data_contributor": "Data contributor",
}


def ashrae_db2_path() -> Path:
    """Return the packaged ASHRAE DB II CSV path.

    The path is suitable for local file operations when the package is installed
    from source or as an editable install. For zipped wheels, prefer
    :func:`load_ashrae_db2`, which uses importlib resources directly.
    """

    return Path(resources.files("dc3.data").joinpath(ASHRAE_DB2_FILENAME))


def load_ashrae_db2(
    *,
    nrows: int | None = None,
    columns: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Load the packaged ASHRAE Global Thermal Comfort Database II CSV.

    Parameters
    ----------
    nrows:
        Optional number of rows to load. Useful for examples and quick UI tests.
    columns:
        Optional source column subset to read.
    """

    csv_resource = resources.files("dc3.data").joinpath(ASHRAE_DB2_FILENAME)
    read_kwargs = {
        "nrows": nrows,
        "usecols": list(columns) if columns is not None else None,
        "low_memory": False,
    }
    with resources.as_file(csv_resource) as path:
        return _read_csv_with_fallback(path, **read_kwargs)


def ashrae_default_mapping() -> dict[str, str]:
    """Return canonical DC3 field mappings for the packaged ASHRAE DB II file."""

    return dict(ASHRAE_DEFAULT_MAPPING)


def subset_ashrae_db2(
    *,
    countries: Iterable[str] | None = None,
    filters: Mapping[str, Iterable[str]] | None = None,
    nrows: int | None = None,
) -> pd.DataFrame:
    """Load and filter the packaged ASHRAE DB II dataset.

    ``filters`` maps raw ASHRAE column names to accepted values. Values are
    compared as strings so that categorical data with mixed source types can be
    filtered consistently.
    """

    df = load_ashrae_db2(nrows=nrows)
    if countries:
        selected = {str(country) for country in countries}
        df = df[df["Country"].astype(str).isin(selected)]
    for column, accepted in (filters or {}).items():
        if column not in df.columns:
            continue
        accepted_values = {str(value) for value in accepted}
        if accepted_values:
            df = df[df[column].astype(str).isin(accepted_values)]
    return df.copy()


def create_ashrae_subset_zip(
    df: pd.DataFrame,
    *,
    dataset_name: str = "ashrae_dc3_subset",
    manifest: Mapping | None = None,
) -> bytes:
    """Return a ZIP archive containing a CSV subset and attribution note."""

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(f"{dataset_name}.csv", df.to_csv(index=False))
        archive.writestr("ATTRIBUTION.txt", ASHRAE_DB2_ATTRIBUTION)
        archive.writestr(
            "manifest.json",
            json.dumps(
                {
                    "dataset": "ASHRAE Global Thermal Comfort Database II",
                    "rows": int(len(df)),
                    "columns": list(df.columns),
                    **dict(manifest or {}),
                },
                indent=2,
                default=str,
            ),
        )
    return buffer.getvalue()


def load_demo_data() -> pd.DataFrame:
    """Return a tiny synthetic dataset for examples and documentation."""

    return pd.DataFrame(
        {
            "Thermal sensation": [-1, 0, 1, 2, "slightly warm", "cold", None],
            "Thermal preference": ["warmer", "no change", "cooler", "cooler", "no_change", "no change", "warmer"],
            "Thermal acceptability": [0, 1, 1, 0, "acceptable", "unacceptable", 1],
            "Country": ["India", "India", "India", "India", "India", "India", "India"],
            "City": ["Mumbai", "Bangalore", "Chennai", "Delhi", "Hyderabad", "Shimla", "Mumbai"],
            "Season": ["Summer", "Winter", "Summer", "Autumn", "Spring", "Winter", "Summer"],
            "Building type": ["Office", "Office", "Classroom", "Office", "Residential", "Office", "Classroom"],
            "Building cooling strategy": ["Mixed mode", "AC", "Fan", "AC", "Natural ventilation", "Mixed mode", "Fan"],
            "Air temperature": [22.1, 24.0, 26.3, 29.1, 25.8, 20.2, 23.5],
            "Relative humidity": [55, 50, 64, 70, 61, 45, 52],
            "Air velocity": [0.12, 0.08, 0.3, 0.18, 0.22, 0.1, 0.16],
        }
    )


def _read_csv_with_fallback(path: str | Path, **kwargs) -> pd.DataFrame:
    encodings = ("utf-8", "utf-8-sig", "cp1252", "latin1")
    last_error: Exception | None = None
    clean_kwargs = {key: value for key, value in kwargs.items() if value is not None}
    for encoding in encodings:
        try:
            return pd.read_csv(path, encoding=encoding, **clean_kwargs)
        except UnicodeDecodeError as exc:
            last_error = exc
    if last_error:
        raise last_error
    return pd.read_csv(path, **clean_kwargs)
