import zipfile
from io import BytesIO

from dc3 import (
    ASHRAE_DB2_ATTRIBUTION,
    ashrae_default_mapping,
    create_ashrae_subset_zip,
    load_ashrae_db2,
    process_dataframe,
)


def test_load_ashrae_db2_and_default_mapping_process_sample():
    df = load_ashrae_db2(nrows=25)
    mapping = ashrae_default_mapping()

    processed = process_dataframe(df, mapping)

    assert len(df) == 25
    assert "Country" in df.columns
    assert processed["dc3_valid"].any()
    assert "dc3_normalization_note" in processed.columns


def test_create_ashrae_subset_zip_contains_attribution_and_manifest():
    df = load_ashrae_db2(nrows=3)
    data = create_ashrae_subset_zip(df, dataset_name="sample")

    with zipfile.ZipFile(BytesIO(data)) as archive:
        names = set(archive.namelist())
        attribution = archive.read("ATTRIBUTION.txt").decode("utf-8")

    assert {"sample.csv", "ATTRIBUTION.txt", "manifest.json"} <= names
    assert "Dryad" in attribution
    assert ASHRAE_DB2_ATTRIBUTION.strip() in attribution
