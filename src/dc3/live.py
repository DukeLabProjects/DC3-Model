"""Utilities for live and repeated DC3 processing workflows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import pandas as pd

from dc3.batch import process_dataframe


@dataclass(frozen=True)
class LiveSnapshot:
    """Processed result from one live polling cycle."""

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
    """Process the latest live dataframe snapshot through the DC3 engine."""

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
    """Read a CSV file as a live snapshot source."""

    return pd.read_csv(path)


def read_excel_snapshot(path: str | Path) -> pd.DataFrame:
    """Read an Excel file as a live snapshot source."""

    return pd.read_excel(path)


def read_sql_snapshot(connection_url: str, query: str) -> pd.DataFrame:
    """Read a SQL query as a live snapshot source.

    This function intentionally accepts a SQLAlchemy connection URL so it can
    support SQLite, PostgreSQL, Supabase Postgres, and other SQL databases
    through the same interface.
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

