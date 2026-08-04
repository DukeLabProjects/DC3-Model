import pandas as pd

from dc3 import process_live_snapshot


def test_process_live_snapshot_limits_rows_and_returns_counts():
    df = pd.DataFrame(
        {
            "TS": [-1, 0, 1],
            "Pref": ["warmer", "no_change", "cooler"],
            "Accept": [0, 1, 1],
        }
    )
    snapshot = process_live_snapshot(
        df,
        {
            "thermal_sensation": "TS",
            "thermal_preference": "Pref",
            "thermal_acceptability": "Accept",
        },
        last_rows=2,
    )

    assert snapshot.raw_rows == 2
    assert snapshot.processed_rows == 2
    assert snapshot.valid_rows == 2
    assert snapshot.processed["dc3_label"].tolist() == ["D", "E-"]
