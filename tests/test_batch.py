import pandas as pd
import pytest

from dc3 import DC3ValidationError, process_dataframe, summarise_dc3, validate_dataframe


MAPPING = {
    "thermal_sensation": "TS",
    "thermal_preference": "Pref",
    "thermal_acceptability": "Accept",
}


def test_validate_dataframe_reports_mapping_problems():
    df = pd.DataFrame({"TS": [0]})
    report = validate_dataframe(df, {"thermal_sensation": "TS"})
    assert report.valid is False
    assert report.missing_required_fields == ("thermal_preference", "thermal_acceptability")


def test_validate_dataframe_accepts_country_optional_field():
    df = pd.DataFrame(
        {
            "TS": [0],
            "Pref": ["no_change"],
            "Accept": [1],
            "Country": ["India"],
            "ISO3": ["IND"],
            "lat": [28.6139],
            "lon": [77.2090],
        }
    )
    report = validate_dataframe(
        df,
        {
            **MAPPING,
            "country": "Country",
            "country_code": "ISO3",
            "latitude": "lat",
            "longitude": "lon",
        },
    )
    assert report.valid is True
    assert "country" in report.mapped_fields
    assert "country_code" in report.mapped_fields
    assert "latitude" in report.mapped_fields
    assert "longitude" in report.mapped_fields


def test_validate_dataframe_rejects_unknown_fields():
    df = pd.DataFrame({"TS": [0]})
    with pytest.raises(DC3ValidationError):
        validate_dataframe(df, {"thermal_sensation": "TS", "unknown": "Column"})


def test_process_dataframe_adds_dc3_outputs_and_keeps_invalid_rows():
    df = pd.DataFrame(
        {
            "TS": [0, "slightly warm", 3, None],
            "Pref": ["no change", "prefer cooler", "no_change", "warmer"],
            "Accept": ["acceptable", 1, 0, 1],
        }
    )

    processed = process_dataframe(df, MAPPING)

    assert list(processed["dc3_label"])[:3] == ["D", "E-", "Z"]
    assert processed.loc[0, "dc3_code"] == 11
    assert processed.loc[1, "thermal_preference_normalized"] == "cooler"
    assert processed.loc[2, "is_z_class"] == True
    assert processed.loc[3, "dc3_valid"] == False
    assert "thermal_sensation is missing" in processed.loc[3, "dc3_error"]


def test_process_dataframe_records_decimal_sensation_normalisation_note():
    df = pd.DataFrame(
        {
            "TS": [-0.5],
            "Pref": ["warmer"],
            "Accept": [1],
        }
    )

    processed = process_dataframe(df, MAPPING)

    assert processed.loc[0, "thermal_sensation_normalized"] == -1
    assert "discretised thermal sensation" in processed.loc[0, "dc3_normalization_note"]


def test_process_dataframe_can_drop_invalid_rows():
    df = pd.DataFrame(
        {
            "TS": [0, None],
            "Pref": ["no_change", "warmer"],
            "Accept": [1, 1],
        }
    )

    processed = process_dataframe(df, MAPPING, keep_invalid=False)

    assert len(processed) == 1
    assert processed.iloc[0]["dc3_label"] == "D"


def test_summarise_dc3():
    df = pd.DataFrame({"dc3_label": ["D", "D", "E-", None]})
    summary = summarise_dc3(df)
    counts = dict(zip(summary["dc3_label"], summary["count"], strict=False))
    assert counts["D"] == 2
    assert counts["INVALID"] == 1
