"""Lightweight evaluation helpers for DC3 outputs."""

from __future__ import annotations

import pandas as pd


def class_distribution(labels) -> pd.DataFrame:
    """Return count and percentage by class label."""

    series = pd.Series(labels, name="label")
    total = len(series)
    counts = series.fillna("INVALID").value_counts(dropna=False).rename_axis("label")
    result = counts.reset_index(name="count")
    result["percentage"] = 0.0 if total == 0 else result["count"] / total * 100
    return result

