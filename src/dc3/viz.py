"""Analytics and optional visualisation helpers for processed DC3 data.

The data-preparation helpers in this module only require pandas. Plotting
functions import Plotly lazily so DC3's core engine remains lightweight.
"""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from dc3.exceptions import DC3ValidationError


def dc3_class_order() -> list[str]:
    """Return the canonical display order for DC3 classes.

    Returns
    -------
    list[str]
        DC3 labels ordered from cold/left to hot/right, with ``Z`` placed last.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       from dc3 import dc3_class_order

       order = dc3_class_order()
       print(order[:3])
       print(order[-1])

    Expected output:

    .. code-block:: text

       ['A-', 'A', 'A+']
       Z
    """

    labels = []
    for letter in ["A", "B", "C", "D", "E", "F", "G"]:
        labels.extend([f"{letter}-", letter, f"{letter}+"])
    labels.append("Z")
    return labels


def dc3_color_map() -> dict[str, str]:
    """Return the DC3 class colour map used by Duke et al. style plots.

    Returns
    -------
    dict[str, str]
        Mapping from DC3 labels to hex colour strings.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       from dc3 import dc3_color_map

       colors = dc3_color_map()
       print(colors["A-"])
       print(colors["Z"])

    Expected output:

    .. code-block:: text

       #2166ac
       #475569
    """

    return dict(zip(dc3_class_order(), _dc3_palette(), strict=False))


def dc3_distribution(
    df: pd.DataFrame,
    *,
    label_column: str = "dc3_label",
    include_zero_count_classes: bool = True,
) -> pd.DataFrame:
    """Return count and percentage by DC3 class.

    Parameters
    ----------
    df:
        Processed dataframe containing a DC3 label column.
    label_column:
        Name of the column that stores DC3 labels.
    include_zero_count_classes:
        Default is ``True``. When true, all 22 canonical DC3 labels are included even if the
        dataset has no records in some classes. This is useful for dashboards
        because the axis does not jump around as filters are changed.

    Returns
    -------
    pandas.DataFrame
        Columns: ``dc3_label``, ``count``, and ``percentage``.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       import pandas as pd
       from dc3 import dc3_distribution

       df = pd.DataFrame({"dc3_label": ["D", "D", "E-", "Z"]})
       distribution = dc3_distribution(df, include_zero_count_classes=False)
       print(distribution.to_string(index=False))

    Expected output:

    .. code-block:: text

        dc3_label  count  percentage
                D      2        50.0
               E-      1        25.0
                Z      1        25.0
    """

    _require_columns(df, [label_column])
    labels = df[label_column].fillna("INVALID")
    total = len(labels)
    counts = labels.value_counts(dropna=False).to_dict()

    ordered_labels = dc3_class_order() if include_zero_count_classes else []
    ordered_labels.extend(
        sorted(label for label in counts if label not in set(ordered_labels))
    )

    rows = []
    for label in ordered_labels:
        count = int(counts.get(label, 0))
        rows.append(
            {
                "dc3_label": label,
                "count": count,
                "percentage": 0.0 if total == 0 else count / total * 100,
            }
        )

    return pd.DataFrame(rows)


def dc3_matrix(
    df: pd.DataFrame,
    *,
    label_column: str = "dc3_label",
) -> pd.DataFrame:
    """Return a 7-by-3 DC3 matrix of class counts.

    Rows represent thermal sensation letters ``A`` through ``G``. Columns
    represent preference direction: ``cooler``, ``no_change``, and ``warmer``.
    The ``Z`` class is intentionally excluded because it is a flag category
    rather than a point in the 7-by-3 state space.

    Parameters
    ----------
    df:
        Processed dataframe containing DC3 labels.
    label_column:
        Default is ``"dc3_label"``.

    Returns
    -------
    pandas.DataFrame
        Rows ``A`` through ``G`` with columns ``cooler``, ``no_change``, and
        ``warmer``.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       import pandas as pd
       from dc3 import dc3_matrix

       df = pd.DataFrame({"dc3_label": ["D", "D+", "E-", "Z"]})
       matrix = dc3_matrix(df)
       row_d = matrix[matrix["thermal_sensation_label"] == "D"]
       print(row_d[["cooler", "no_change", "warmer"]].to_string(index=False))

    Expected output:

    .. code-block:: text

        cooler  no_change  warmer
             0          1       1
    """

    _require_columns(df, [label_column])
    counts = df[label_column].fillna("INVALID").value_counts().to_dict()
    rows = []
    for letter in ["A", "B", "C", "D", "E", "F", "G"]:
        rows.append(
            {
                "thermal_sensation_label": letter,
                "cooler": int(counts.get(f"{letter}-", 0)),
                "no_change": int(counts.get(letter, 0)),
                "warmer": int(counts.get(f"{letter}+", 0)),
            }
        )
    return pd.DataFrame(rows)


def environmental_summary(
    df: pd.DataFrame,
    value_columns: Iterable[str],
    *,
    groupby: str = "dc3_label",
) -> pd.DataFrame:
    """Summarise numeric environmental columns by DC3 class or another group.

    Non-numeric values are coerced to missing values. Rows whose group is
    missing are omitted from grouped summaries.

    Parameters
    ----------
    df:
        Dataframe containing a grouping column and numeric environmental
        columns.
    value_columns:
        Iterable of numeric source columns to summarise.
    groupby:
        Default is ``"dc3_label"``. Column used for grouping.

    Returns
    -------
    pandas.DataFrame
        Summary with count, mean, median, min, max, 25th percentile, and 75th
        percentile for each variable/group pair.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       import pandas as pd
       from dc3 import environmental_summary

       df = pd.DataFrame(
           {
               "dc3_label": ["D", "D", "E-"],
               "Air temperature": [24.0, 26.0, 28.0],
           }
       )
       summary = environmental_summary(df, ["Air temperature"])
       print(summary[["dc3_label", "variable", "count", "mean"]].to_string(index=False))

    Expected output:

    .. code-block:: text

        dc3_label        variable  count  mean
                D Air temperature      2  25.0
               E- Air temperature      1  28.0
    """

    value_columns = list(value_columns)
    _require_columns(df, [groupby, *value_columns])
    if not value_columns:
        return pd.DataFrame(
            columns=[
                groupby,
                "variable",
                "count",
                "mean",
                "median",
                "min",
                "max",
                "q25",
                "q75",
            ]
        )

    working = df[[groupby, *value_columns]].copy()
    rows = []
    for column in value_columns:
        working[column] = pd.to_numeric(working[column], errors="coerce")
        grouped = working.dropna(subset=[groupby]).groupby(groupby, dropna=False)[column]
        summary = grouped.agg(["count", "mean", "median", "min", "max"]).reset_index()
        if summary.empty:
            continue
        q25 = grouped.quantile(0.25).rename("q25").reset_index()
        q75 = grouped.quantile(0.75).rename("q75").reset_index()
        summary = summary.merge(q25, on=groupby).merge(q75, on=groupby)
        summary.insert(1, "variable", column)
        rows.append(summary)

    if not rows:
        return pd.DataFrame(
            columns=[groupby, "variable", "count", "mean", "median", "min", "max", "q25", "q75"]
        )
    return pd.concat(rows, ignore_index=True)


def observed_comfort_distribution(
    df: pd.DataFrame,
    *,
    comfort_column: str = "observed_comfort",
) -> pd.DataFrame:
    """Return comfortable/uncomfortable counts and percentages.

    Parameters
    ----------
    df:
        Dataframe containing observed comfort values.
    comfort_column:
        Default is ``"observed_comfort"``.

    Returns
    -------
    pandas.DataFrame
        Three rows: comfortable, uncomfortable, and unknown.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       import pandas as pd
       from dc3 import observed_comfort_distribution

       df = pd.DataFrame({"observed_comfort": [True, False, False, None]})
       distribution = observed_comfort_distribution(df)
       print(distribution.to_string(index=False))

    Expected output:

    .. code-block:: text

        observed_comfort  count  percentage
             comfortable      1        25.0
           uncomfortable      2        50.0
                  unknown      1        25.0
    """

    _require_columns(df, [comfort_column])
    values = df[comfort_column].map(
        {
            True: "comfortable",
            False: "uncomfortable",
        }
    ).fillna("unknown")
    total = len(values)
    counts = values.value_counts().to_dict()
    rows = []
    for label in ["comfortable", "uncomfortable", "unknown"]:
        count = int(counts.get(label, 0))
        rows.append(
            {
                "observed_comfort": label,
                "count": count,
                "percentage": 0.0 if total == 0 else count / total * 100,
            }
        )
    return pd.DataFrame(rows)


def z_class_summary(df: pd.DataFrame, *, z_column: str = "is_z_class") -> dict:
    """Return count and percentage information for Z-class records.

    Parameters
    ----------
    df:
        Dataframe containing a Z-class boolean column.
    z_column:
        Default is ``"is_z_class"``.

    Returns
    -------
    dict
        Keys: ``total_rows``, ``z_class_rows``, and ``z_class_percentage``.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       import pandas as pd
       from dc3 import z_class_summary

       df = pd.DataFrame({"is_z_class": [False, True, False, True]})
       summary = z_class_summary(df)
       print(summary)

    Expected output:

    .. code-block:: text

       {'total_rows': 4, 'z_class_rows': 2, 'z_class_percentage': 50.0}
    """

    _require_columns(df, [z_column])
    total = len(df)
    z_count = int(df[z_column].fillna(False).astype(bool).sum())
    return {
        "total_rows": total,
        "z_class_rows": z_count,
        "z_class_percentage": 0.0 if total == 0 else z_count / total * 100,
    }


def z_class_match_table(
    df: pd.DataFrame,
    *,
    z_column: str = "is_z_class",
    group_columns: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Return grouped counts for records that match the Z-class rule.

    By default, the function groups Z-class records by the internally
    normalised sensation, preference, and acceptability columns. These are the
    fields that explain why the row matched the Z-class condition.

    Parameters
    ----------
    df:
        Processed dataframe containing Z-class flags and grouping columns.
    z_column:
        Default is ``"is_z_class"``.
    group_columns:
        Default is ``None``. When omitted, grouped by normalised sensation,
        sensation label, preference, and acceptability.

    Returns
    -------
    pandas.DataFrame
        Grouped Z-class counts and percentages.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       import pandas as pd
       from dc3 import process_dataframe, z_class_match_table

       df = pd.DataFrame({"TS": [0, 0, 1], "TP": ["no_change", "no_change", "cooler"], "TA": [0, 0, 1]})
       processed = process_dataframe(
           df,
           columns={
               "thermal_sensation": "TS",
               "thermal_preference": "TP",
               "thermal_acceptability": "TA",
           },
       )
       matches = z_class_match_table(processed)
       print(matches[["thermal_sensation_label", "count", "percentage"]].to_string(index=False))

    Expected output:

    .. code-block:: text

        thermal_sensation_label  count  percentage
                              D      2       100.0
    """

    default_groups = [
        "thermal_sensation_normalized",
        "thermal_sensation_label",
        "thermal_preference_normalized",
        "thermal_acceptability_normalized",
    ]
    group_columns = list(group_columns or default_groups)
    _require_columns(df, [z_column, *group_columns])
    z_rows = z_class_records(df, z_column=z_column)
    if z_rows.empty:
        return pd.DataFrame([dict.fromkeys(group_columns, None) | {"count": 0, "percentage": 0.0}])

    grouped = z_rows.groupby(group_columns, dropna=False).size().reset_index(name="count")
    grouped["percentage"] = grouped["count"] / len(z_rows) * 100
    return grouped.sort_values("count", ascending=False).reset_index(drop=True)


def z_class_records(df: pd.DataFrame, *, z_column: str = "is_z_class") -> pd.DataFrame:
    """Return only Z-class records from a processed dataframe.

    Parameters
    ----------
    df:
        Processed dataframe.
    z_column:
        Default is ``"is_z_class"``.

    Returns
    -------
    pandas.DataFrame
        Copy of rows where ``z_column`` is truthy.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       import pandas as pd
       from dc3 import z_class_records

       df = pd.DataFrame({"dc3_label": ["D", "Z"], "is_z_class": [False, True]})
       z_rows = z_class_records(df)
       print(z_rows["dc3_label"].tolist())

    Expected output:

    .. code-block:: text

       ['Z']
    """

    _require_columns(df, [z_column])
    return df[df[z_column].fillna(False).astype(bool)].copy()


def plot_dc3_distribution(distribution: pd.DataFrame):
    """Build a Plotly bar chart from :func:`dc3_distribution` output.

    Parameters
    ----------
    distribution:
        Dataframe returned by :func:`dc3_distribution`.

    Returns
    -------
    plotly.graph_objects.Figure
        Plotly bar chart figure.

    Examples
    --------
    .. code-block:: python

       # python -m pip install "dc3model_v1[viz]"
       import pandas as pd
       from dc3 import dc3_distribution, plot_dc3_distribution

       distribution = dc3_distribution(
           pd.DataFrame({"dc3_label": ["D", "E-", "Z"]}),
           include_zero_count_classes=False,
       )
       fig = plot_dc3_distribution(distribution)
       print(len(fig.data))

    Expected output:

    .. code-block:: text

       1
    """

    px = _require_plotly_express()
    _require_columns(distribution, ["dc3_label", "count"])
    fig = px.bar(
        distribution,
        x="dc3_label",
        y="count",
        category_orders={"dc3_label": dc3_class_order()},
        color="dc3_label",
        color_discrete_map=dc3_color_map(),
        labels={"dc3_label": "DC3 class", "count": "Count"},
    )
    fig.update_layout(showlegend=False)
    return fig


def plot_dc3_matrix(matrix: pd.DataFrame):
    """Build a Plotly heatmap from :func:`dc3_matrix` output.

    Parameters
    ----------
    matrix:
        Dataframe returned by :func:`dc3_matrix`.

    Returns
    -------
    plotly.graph_objects.Figure
        Plotly heatmap figure.

    Examples
    --------
    .. code-block:: python

       # python -m pip install "dc3model_v1[viz]"
       import pandas as pd
       from dc3 import dc3_matrix, plot_dc3_matrix

       matrix = dc3_matrix(pd.DataFrame({"dc3_label": ["D", "D+"]}))
       fig = plot_dc3_matrix(matrix)
       print(fig.data[0].type)

    Expected output:

    .. code-block:: text

       heatmap
    """

    go = _require_plotly_graph_objects()
    _require_columns(matrix, ["thermal_sensation_label", "cooler", "no_change", "warmer"])
    z_values = matrix[["cooler", "no_change", "warmer"]].to_numpy()
    return go.Figure(
        data=go.Heatmap(
            z=z_values,
            x=["cooler", "no_change", "warmer"],
            y=matrix["thermal_sensation_label"],
            colorscale="Viridis",
            text=z_values,
            texttemplate="%{text}",
            hovertemplate="Sensation: %{y}<br>Preference: %{x}<br>Count: %{z}<extra></extra>",
        )
    )


def plot_observed_comfort_distribution(distribution: pd.DataFrame):
    """Build a Plotly donut chart from observed comfort distribution output.

    Parameters
    ----------
    distribution:
        Dataframe returned by :func:`observed_comfort_distribution`.

    Returns
    -------
    plotly.graph_objects.Figure
        Plotly pie/donut figure.

    Examples
    --------
    .. code-block:: python

       # python -m pip install "dc3model_v1[viz]"
       import pandas as pd
       from dc3 import observed_comfort_distribution, plot_observed_comfort_distribution

       distribution = observed_comfort_distribution(pd.DataFrame({"observed_comfort": [True, False]}))
       fig = plot_observed_comfort_distribution(distribution)
       print(fig.data[0].type)

    Expected output:

    .. code-block:: text

       pie
    """

    px = _require_plotly_express()
    _require_columns(distribution, ["observed_comfort", "count"])
    return px.pie(
        distribution[distribution["count"] > 0],
        names="observed_comfort",
        values="count",
        hole=0.52,
        color="observed_comfort",
        color_discrete_map={
            "comfortable": "#2f9e44",
            "uncomfortable": "#e03131",
            "unknown": "#868e96",
        },
    )


def plot_z_class_matches(match_table: pd.DataFrame):
    """Build a Plotly bar chart for Z-class matching records.

    Parameters
    ----------
    match_table:
        Dataframe returned by :func:`z_class_match_table`.

    Returns
    -------
    plotly.graph_objects.Figure
        Plotly bar chart figure.

    Examples
    --------
    .. code-block:: python

       # python -m pip install "dc3model_v1[viz]"
       import pandas as pd
       from dc3 import plot_z_class_matches

       match_table = pd.DataFrame({"thermal_sensation_label": ["D"], "count": [2], "percentage": [100.0]})
       fig = plot_z_class_matches(match_table)
       print(fig.data[0].type)

    Expected output:

    .. code-block:: text

       bar
    """

    px = _require_plotly_express()
    _require_columns(match_table, ["count"])
    table = match_table.reset_index(drop=True)
    label_columns = [column for column in list(table.columns) if column not in {"count", "percentage"}]
    counts = _numeric_column_values(table, "count")
    if label_columns:
        signatures = _z_signatures(table, label_columns)
    else:
        signatures = ["Z-class"] * len(table.index)
    plot_table = pd.DataFrame({"z_signature": signatures, "count": counts})
    return px.bar(
        plot_table,
        x="z_signature",
        y="count",
        color="count",
        color_continuous_scale="Reds",
        labels={"z_signature": "Z-class matching signature", "count": "Count"},
    )


def export_figure(
    fig,
    *,
    format: str = "png",
    width: int = 1400,
    height: int = 900,
    scale: float = 2.0,
) -> bytes:
    """Export a Plotly figure as ``png``, ``svg``, or ``pdf`` bytes.

    Static export uses Plotly's Kaleido backend. Install visualisation
    dependencies with ``python -m pip install -e .[viz]``.

    Parameters
    ----------
    fig:
        Plotly figure object.
    format:
        Default is ``"png"``. Accepted values are ``"png"``, ``"svg"``, and
        ``"pdf"``.
    width:
        Default is ``1400`` pixels.
    height:
        Default is ``900`` pixels.
    scale:
        Default is ``2.0``. Higher values increase raster output resolution.

    Returns
    -------
    bytes
        Static figure file bytes.

    Examples
    --------
    .. code-block:: python

       # python -m pip install "dc3model_v1[viz]"
       import pandas as pd
       from dc3 import dc3_distribution, export_figure, plot_dc3_distribution

       distribution = dc3_distribution(
           pd.DataFrame({"dc3_label": ["D", "E-", "Z"]}),
           include_zero_count_classes=False,
       )
       fig = plot_dc3_distribution(distribution)
       png_bytes = export_figure(fig, format="png", width=800, height=500, scale=1.0)
       print(len(png_bytes) > 0)

    Expected output:

    .. code-block:: text

       True
    """

    fmt = format.lower().strip(".")
    if fmt not in {"png", "svg", "pdf"}:
        raise DC3ValidationError("format must be one of: png, svg, pdf")
    try:
        return fig.to_image(format=fmt, width=width, height=height, scale=scale)
    except ValueError as exc:
        raise ImportError(
            "Static plot export requires Kaleido. Install it with: "
            "python -m pip install -e .[viz]"
        ) from exc


def _dc3_palette() -> list[str]:
    return [
        "#2166ac",
        "#2c7bb6",
        "#3d95c4",
        "#57a9cd",
        "#74bdd4",
        "#91cbd8",
        "#a6d8cf",
        "#80cdc1",
        "#5ab4ac",
        "#2fb47c",
        "#1a9850",
        "#66bd63",
        "#a6d96a",
        "#d9ef8b",
        "#fee08b",
        "#fdae61",
        "#f46d43",
        "#e95c47",
        "#d73027",
        "#bd1f2d",
        "#a50026",
        "#475569",
    ]


def _display_value(value) -> str:
    try:
        missing = pd.isna(value)
    except (TypeError, ValueError):
        missing = False
    if isinstance(missing, bool) and missing:
        return "missing"
    if hasattr(missing, "item"):
        try:
            if bool(missing.item()):
                return "missing"
        except (TypeError, ValueError):
            pass
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _join_display_values(values) -> str:
    return " | ".join([str(_display_value(value)) for value in values])


def _numeric_column_values(table: pd.DataFrame, column: str) -> list[float]:
    column_position = _column_position(table, column)
    values: list[float] = []
    for row_position in range(len(table.index)):
        value = table.iat[row_position, column_position]
        try:
            values.append(float(value))
        except (TypeError, ValueError):
            values.append(0.0)
    return values


def _z_signatures(table: pd.DataFrame, label_columns: list[str]) -> list[str]:
    signatures: list[str] = []
    row_count = len(table.index)
    column_positions = [_column_position(table, column) for column in label_columns]
    for row_position in range(row_count):
        values = [table.iat[row_position, column_position] for column_position in column_positions]
        signatures.append(_join_display_values(values))
    return signatures


def _column_position(table: pd.DataFrame, column: str) -> int:
    position = table.columns.get_loc(column)
    if isinstance(position, slice):
        return int(position.start)
    if isinstance(position, int):
        return position
    try:
        return int(position)
    except (TypeError, ValueError):
        pass
    if hasattr(position, "nonzero"):
        matches = position.nonzero()[0]
        if len(matches):
            return int(matches[0])
    return int(position[0])


def _require_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise DC3ValidationError(f"missing required column(s): {', '.join(missing)}")


def _require_plotly_express():
    try:
        import plotly.express as px
    except ImportError as exc:
        raise ImportError(
            "Plotly visualisations require the optional 'viz' dependencies. "
            "Install them with: python -m pip install -e .[viz]"
        ) from exc
    return px


def _require_plotly_graph_objects():
    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise ImportError(
            "Plotly visualisations require the optional 'viz' dependencies. "
            "Install them with: python -m pip install -e .[viz]"
        ) from exc
    return go
