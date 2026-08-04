from io import BytesIO
import zipfile

import pandas as pd

from dc3 import (
    ashrae_default_mapping,
    city_coordinates,
    classify_dc3,
    create_ashrae_subset_zip,
    dc3_codebook,
    dc3_distribution,
    dc3_matrix,
    decode_dc3,
    describe_dc3,
    encode_dc3,
    enrich_geography,
    environmental_summary,
    load_ashrae_db2,
    load_demo_data,
    observed_comfort,
    observed_comfort_distribution,
    plot_dc3_distribution,
    process_dataframe,
    process_live_snapshot,
    summarise_dc3,
    thermal_sensation_label,
    z_class_match_table,
    z_class_summary,
)


def test_core_documentation_examples():
    label = classify_dc3(
        thermal_sensation=0,
        thermal_preference="no_change",
        thermal_acceptability=1,
    )

    assert label == "D"
    assert encode_dc3(label) == 11
    assert decode_dc3(11)["label"] == "D"
    assert describe_dc3("E-")["recommended_direction"] == "cooler"
    assert observed_comfort("no_change", 1) is True
    assert observed_comfort("cooler", 1) is False
    assert thermal_sensation_label("hot") == "G"
    assert dc3_codebook()[10]["dc3_label"] == "D"


def test_small_dataframe_documentation_example():
    df = pd.DataFrame(
        {
            "TS": [0, 1, 0],
            "TP": ["no_change", "cooler", "no_change"],
            "TA": [1, 1, 0],
            "Country": ["India", "India", "India"],
            "Air temperature": [24.0, 28.0, 25.5],
        }
    )
    columns = {
        "thermal_sensation": "TS",
        "thermal_preference": "TP",
        "thermal_acceptability": "TA",
        "country": "Country",
        "air_temperature": "Air temperature",
    }

    processed = process_dataframe(df, columns)
    summary = summarise_dc3(processed)

    assert processed["dc3_label"].tolist() == ["D", "E-", "Z"]
    assert processed["dc3_code"].tolist() == [11, 13, 22]
    assert processed["observed_comfort"].tolist() == [True, False, False]
    assert set(summary["dc3_label"]) == {"D", "E-", "Z"}


def test_dataset_documentation_examples():
    sample = load_ashrae_db2(nrows=3)
    assert len(sample) == 3
    assert "Thermal sensation" in sample.columns

    selected = load_ashrae_db2(nrows=2, columns=["Country", "City", "Thermal sensation"])
    assert set(selected.columns) == {"Country", "City", "Thermal sensation"}

    mapping = ashrae_default_mapping()
    assert mapping["thermal_sensation"] == "Thermal sensation"
    assert mapping["thermal_acceptability"] == "Thermal sensation acceptability"

    demo = load_demo_data()
    processed = process_dataframe(
        demo,
        {
            "thermal_sensation": "Thermal sensation",
            "thermal_preference": "Thermal preference",
            "thermal_acceptability": "Thermal acceptability",
        },
    )
    assert demo.shape == (7, 11)
    assert processed["dc3_label"].head(3).tolist() == ["C+", "D", "E-"]


def test_ashrae_zip_documentation_example():
    df = load_ashrae_db2(nrows=2)
    archive_bytes = create_ashrae_subset_zip(
        df,
        dataset_name="sample_ashrae",
        manifest={"country_filter": "none"},
    )

    with zipfile.ZipFile(BytesIO(archive_bytes)) as archive:
        assert sorted(archive.namelist()) == ["ATTRIBUTION.txt", "manifest.json", "sample_ashrae.csv"]


def test_geography_documentation_examples():
    lat, lon = city_coordinates("India", "Delhi")
    assert round(lat, 3) == 28.614
    assert round(lon, 3) == 77.209

    df = pd.DataFrame({"Country": ["India"], "City": ["Delhi"]})
    enriched, mapping = enrich_geography(df, {"country": "Country", "city": "City"})

    assert mapping["country_code"] == "dc3_country_code"
    assert round(enriched.loc[0, "dc3_latitude"], 3) == 28.614
    assert enriched.loc[0, "dc3_country_code"] == "IND"


def test_analytics_documentation_examples():
    df = pd.DataFrame({"dc3_label": ["D", "D", "E-", "Z"]})
    distribution = dc3_distribution(df, include_zero_count_classes=False)
    assert distribution["count"].tolist() == [2, 1, 1]

    matrix = dc3_matrix(pd.DataFrame({"dc3_label": ["D", "D+", "E-", "Z"]}))
    row_d = matrix[matrix["thermal_sensation_label"] == "D"].iloc[0]
    assert row_d["no_change"] == 1
    assert row_d["warmer"] == 1

    env = environmental_summary(
        pd.DataFrame(
            {
                "dc3_label": ["D", "D", "E-"],
                "Air temperature": [24.0, 26.0, 28.0],
            }
        ),
        ["Air temperature"],
    )
    assert env.loc[env["dc3_label"] == "D", "mean"].iloc[0] == 25.0

    comfort = observed_comfort_distribution(pd.DataFrame({"observed_comfort": [True, False, False, None]}))
    assert comfort["count"].tolist() == [1, 2, 1]


def test_z_class_and_live_documentation_examples():
    df = pd.DataFrame({"TS": [0, 0, 1], "TP": ["no_change", "no_change", "cooler"], "TA": [1, 0, 1]})
    columns = {
        "thermal_sensation": "TS",
        "thermal_preference": "TP",
        "thermal_acceptability": "TA",
    }
    processed = process_dataframe(df, columns)

    assert z_class_summary(processed) == {
        "total_rows": 3,
        "z_class_rows": 1,
        "z_class_percentage": 33.33333333333333,
    }
    assert z_class_match_table(processed)["thermal_sensation_label"].tolist() == ["D"]

    snapshot = process_live_snapshot(df, columns, last_rows=1)
    assert snapshot.raw_rows == 1
    assert snapshot.processed["dc3_label"].tolist() == ["E-"]


def test_plot_documentation_example():
    distribution = dc3_distribution(
        pd.DataFrame({"dc3_label": ["D", "E-", "Z"]}),
        include_zero_count_classes=False,
    )
    fig = plot_dc3_distribution(distribution)
    assert fig.data[0].type == "bar"
