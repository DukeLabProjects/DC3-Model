import pandas as pd
import pytest

from dc3 import (
    DC3ValidationError,
    dc3_class_order,
    dc3_color_map,
    dc3_distribution,
    dc3_matrix,
    environmental_summary,
    observed_comfort_distribution,
    z_class_records,
    z_class_match_table,
    z_class_summary,
)
from dc3.viz import plot_z_class_matches


def test_dc3_class_order_contains_all_model_states():
    labels = dc3_class_order()
    assert len(labels) == 22
    assert labels[:3] == ["A-", "A", "A+"]
    assert labels[-1] == "Z"


def test_dc3_color_map_matches_class_order():
    colors = dc3_color_map()
    assert list(colors) == dc3_class_order()
    assert colors["A-"] == "#2166ac"
    assert colors["D"] == "#1a9850"
    assert colors["G+"] == "#a50026"
    assert colors["Z"] == "#475569"


def test_dc3_distribution_includes_zero_count_classes():
    df = pd.DataFrame({"dc3_label": ["D", "D", "E-", None]})
    distribution = dc3_distribution(df)

    counts = dict(zip(distribution["dc3_label"], distribution["count"], strict=False))
    assert counts["D"] == 2
    assert counts["E-"] == 1
    assert counts["A-"] == 0
    assert counts["INVALID"] == 1


def test_dc3_matrix_counts_7_by_3_state_space():
    df = pd.DataFrame({"dc3_label": ["A-", "D", "D", "G+", "Z", None]})
    matrix = dc3_matrix(df)

    assert list(matrix.columns) == ["thermal_sensation_label", "cooler", "no_change", "warmer"]
    assert len(matrix) == 7
    d_row = matrix[matrix["thermal_sensation_label"] == "D"].iloc[0]
    assert d_row["no_change"] == 2
    g_row = matrix[matrix["thermal_sensation_label"] == "G"].iloc[0]
    assert g_row["warmer"] == 1


def test_environmental_summary_groups_numeric_columns():
    df = pd.DataFrame(
        {
            "dc3_label": ["D", "D", "E-"],
            "Air temperature": [24, "25", 28],
            "Relative humidity": [50, 55, 70],
        }
    )

    summary = environmental_summary(df, ["Air temperature", "Relative humidity"])

    temp_d = summary[
        (summary["dc3_label"] == "D") & (summary["variable"] == "Air temperature")
    ].iloc[0]
    assert temp_d["count"] == 2
    assert temp_d["mean"] == 24.5


def test_z_class_helpers():
    df = pd.DataFrame(
        {
            "dc3_label": ["D", "Z", "E-"],
            "is_z_class": [False, True, False],
        }
    )

    assert z_class_summary(df)["z_class_rows"] == 1
    assert z_class_records(df)["dc3_label"].tolist() == ["Z"]


def test_observed_comfort_distribution():
    df = pd.DataFrame({"observed_comfort": [True, True, False, None]})
    distribution = observed_comfort_distribution(df)
    counts = dict(zip(distribution["observed_comfort"], distribution["count"], strict=False))
    assert counts["comfortable"] == 2
    assert counts["uncomfortable"] == 1
    assert counts["unknown"] == 1


def test_z_class_match_table_uses_internal_columns():
    df = pd.DataFrame(
        {
            "is_z_class": [False, True, True],
            "thermal_sensation_normalized": [0, 0, 1],
            "thermal_sensation_label": ["D", "D", "E"],
            "thermal_preference_normalized": ["no_change", "no_change", "no_change"],
            "thermal_acceptability_normalized": [1, 0, 0],
        }
    )
    table = z_class_match_table(df)
    assert table["count"].sum() == 2
    assert set(table["thermal_sensation_label"]) == {"D", "E"}


def test_plot_z_class_matches_accepts_mixed_numeric_and_missing_values():
    table = pd.DataFrame(
        {
            "thermal_sensation_normalized": [0.0, 1.0],
            "thermal_sensation_label": ["D", None],
            "thermal_preference_normalized": ["no_change", "no_change"],
            "thermal_acceptability_normalized": [0.0, 0.0],
            "count": [3, 1],
            "percentage": [75.0, 25.0],
        }
    )

    fig = plot_z_class_matches(table)

    assert fig is not None
    assert list(fig.data[0].x) == [
        "0 | D | no_change | 0",
        "1 | missing | no_change | 0",
    ]
    assert list(fig.data[0].y) == [3.0, 1.0]


def test_viz_helpers_raise_clear_errors_for_missing_columns():
    with pytest.raises(DC3ValidationError):
        dc3_distribution(pd.DataFrame({"label": ["D"]}))
    with pytest.raises(DC3ValidationError):
        environmental_summary(pd.DataFrame({"dc3_label": ["D"]}), ["Air temperature"])
