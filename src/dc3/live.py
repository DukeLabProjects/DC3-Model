"""Utilities for live and repeated DC3 processing workflows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import pandas as pd

from dc3.batch import process_dataframe


@dataclass(frozen=True)
class LiveSnapshot:
    """Processed result from one live polling cycle.

    Attributes
    ----------
    raw_rows:
        Number of source rows considered in this snapshot.
    processed_rows:
        Number of rows returned after processing.
    valid_rows:
        Rows with ``dc3_valid=True``.
    invalid_rows:
        Rows with ``dc3_valid=False``.
    z_class_rows:
        Rows that matched the Z-class rule.
    processed:
        Processed dataframe for this snapshot.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       import pandas as pd
       from dc3 import process_live_snapshot

       df = pd.DataFrame({"TS": [0], "TP": ["no_change"], "TA": [1]})
       snapshot = process_live_snapshot(
           df,
           columns={
               "thermal_sensation": "TS",
               "thermal_preference": "TP",
               "thermal_acceptability": "TA",
           },
       )

       print(snapshot.valid_rows)
       print(snapshot.processed["dc3_label"].tolist())

    Expected output:

    .. code-block:: text

       1
       ['D']
    """

    raw_rows: int
    processed_rows: int
    valid_rows: int
    invalid_rows: int
    z_class_rows: int
    processed: pd.DataFrame


def process_live_snapshot(
    df: pd.DataFrame,
    columns: Mapping[str, str],
    *,
    keep_invalid: bool = True,
    last_rows: int | None = None,
) -> LiveSnapshot:
    """Process the latest live dataframe snapshot through the DC3 engine.

    Parameters
    ----------
    df:
        Dataframe snapshot from a CSV file, Excel file, SQL query, sensor
        buffer, or other polling source.
    columns:
        Canonical DC3 field mapping.
    keep_invalid:
        Default is ``True``. Passed to :func:`dc3.process_dataframe`.
    last_rows:
        Default is ``None``. When provided, only the latest ``last_rows``
        records are processed.

    Returns
    -------
    LiveSnapshot
        Summary counts plus the processed dataframe.

    Examples
    --------
    Process the full snapshot:

    .. code-block:: python

       # python -m pip install dc3model_v1
       import pandas as pd
       from dc3 import process_live_snapshot

       df = pd.DataFrame(
           {
               "TS": [0, 1, 0],
               "TP": ["no_change", "cooler", "no_change"],
               "TA": [1, 1, 0],
           }
       )
       columns = {
           "thermal_sensation": "TS",
           "thermal_preference": "TP",
           "thermal_acceptability": "TA",
       }
       snapshot = process_live_snapshot(df, columns)
       print(snapshot.raw_rows, snapshot.valid_rows, snapshot.z_class_rows)

    Expected output:

    .. code-block:: text

       3 3 1

    Process only the latest row:

    .. code-block:: python

       import pandas as pd
       from dc3 import process_live_snapshot

       df = pd.DataFrame({"TS": [0, 1], "TP": ["no_change", "cooler"], "TA": [1, 1]})
       columns = {
           "thermal_sensation": "TS",
           "thermal_preference": "TP",
           "thermal_acceptability": "TA",
       }
       snapshot = process_live_snapshot(df, columns, last_rows=1)
       print(snapshot.processed["dc3_label"].tolist())

    Expected output:

    .. code-block:: text

       ['E-']
    """

    raw = df.tail(last_rows).copy() if last_rows else df.copy()
    processed = process_dataframe(raw, columns, keep_invalid=keep_invalid)
    valid_mask = processed["dc3_valid"].fillna(False).astype(bool)
    z_mask = processed["is_z_class"].fillna(False).astype(bool)
    return LiveSnapshot(
        raw_rows=len(raw),
        processed_rows=len(processed),
        valid_rows=int(valid_mask.sum()),
        invalid_rows=int((~valid_mask).sum()),
        z_class_rows=int(z_mask.sum()),
        processed=processed,
    )


def read_csv_snapshot(path: str | Path) -> pd.DataFrame:
    """Read a CSV file as a live snapshot source.

    Parameters
    ----------
    path:
        CSV file path.

    Returns
    -------
    pandas.DataFrame
        Dataframe read from the CSV file.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       from pathlib import Path
       import pandas as pd
       from dc3 import read_csv_snapshot

       path = Path("live_snapshot.csv")
       pd.DataFrame({"TS": [0], "TP": ["no_change"], "TA": [1]}).to_csv(path, index=False)
       df = read_csv_snapshot(path)
       print(df.shape)

    Expected output:

    .. code-block:: text

       (1, 3)
    """

    return pd.read_csv(path)


def read_excel_snapshot(path: str | Path) -> pd.DataFrame:
    """Read an Excel file as a live snapshot source.

    Parameters
    ----------
    path:
        Excel file path.

    Returns
    -------
    pandas.DataFrame
        Dataframe read from the first worksheet.

    Examples
    --------
    .. code-block:: python

       # python -m pip install "dc3model_v1[live]"
       from pathlib import Path
       import pandas as pd
       from dc3 import read_excel_snapshot

       path = Path("live_snapshot.xlsx")
       pd.DataFrame({"TS": [0], "TP": ["no_change"], "TA": [1]}).to_excel(path, index=False)
       df = read_excel_snapshot(path)
       print(df.shape)

    Expected output:

    .. code-block:: text

       (1, 3)
    """

    return pd.read_excel(path)


def read_sql_snapshot(connection_url: str, query: str) -> pd.DataFrame:
    """Read a SQL query as a live snapshot source.

    This function intentionally accepts a SQLAlchemy connection URL so it can
    support SQLite, PostgreSQL, Supabase Postgres, and other SQL databases
    through the same interface.

    Parameters
    ----------
    connection_url:
        SQLAlchemy connection URL, for example ``"sqlite:///comfort.db"``.
    query:
        SQL query that returns the latest feedback rows.

    Returns
    -------
    pandas.DataFrame
        Query result.

    Examples
    --------
    .. code-block:: python

       # python -m pip install "dc3model_v1[live]"
       import pandas as pd
       from sqlalchemy import create_engine
       from dc3 import read_sql_snapshot

       engine = create_engine("sqlite:///dc3_live_example.db")
       pd.DataFrame({"TS": [0], "TP": ["no_change"], "TA": [1]}).to_sql(
           "feedback",
           engine,
           index=False,
           if_exists="replace",
       )

       df = read_sql_snapshot("sqlite:///dc3_live_example.db", "SELECT * FROM feedback")
       print(df.shape)

    Expected output:

    .. code-block:: text

       (1, 3)
    """

    try:
        from sqlalchemy import create_engine
    except ImportError as exc:
        raise ImportError(
            "Database live snapshots require optional live dependencies. "
            "Install them with: python -m pip install -e .[live]"
        ) from exc

    engine = create_engine(connection_url)
    with engine.connect() as connection:
        return pd.read_sql_query(query, connection)
