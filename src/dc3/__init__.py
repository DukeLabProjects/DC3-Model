"""Public API for DC3 Model."""

from dc3.batch import ValidationReport, process_dataframe, summarise_dc3, validate_dataframe
from dc3.core import (
    DC3_STATE_TABLE,
    decode_dc3,
    describe_dc3,
    dc3_codebook,
    encode_dc3,
    observed_comfort,
    classify_dc3,
    thermal_sensation_label,
)
from dc3.datasets import (
    ASHRAE_DB2_ATTRIBUTION,
    ashrae_db2_path,
    ashrae_default_mapping,
    create_ashrae_subset_zip,
    load_ashrae_db2,
    load_demo_data,
    subset_ashrae_db2,
)
from dc3.exceptions import DC3Error, DC3InputError, DC3ValidationError
from dc3.geography import city_coordinates, country_to_iso3, enrich_geography
from dc3.live import (
    LiveSnapshot,
    process_live_snapshot,
    read_csv_snapshot,
    read_excel_snapshot,
    read_sql_snapshot,
)
from dc3.viz import (
    dc3_class_order,
    dc3_color_map,
    dc3_distribution,
    dc3_matrix,
    environmental_summary,
    z_class_records,
    z_class_summary,
    observed_comfort_distribution,
    plot_observed_comfort_distribution,
    plot_z_class_matches,
    export_figure,
    z_class_match_table,
)

__all__ = [
    "DC3Error",
    "DC3InputError",
    "DC3ValidationError",
    "LiveSnapshot",
    "DC3_STATE_TABLE",
    "ASHRAE_DB2_ATTRIBUTION",
    "ValidationReport",
    "ashrae_db2_path",
    "ashrae_default_mapping",
    "classify_dc3",
    "create_ashrae_subset_zip",
    "city_coordinates",
    "country_to_iso3",
    "decode_dc3",
    "describe_dc3",
    "dc3_class_order",
    "dc3_color_map",
    "dc3_distribution",
    "dc3_codebook",
    "dc3_matrix",
    "encode_dc3",
    "environmental_summary",
    "enrich_geography",
    "export_figure",
    "load_ashrae_db2",
    "load_demo_data",
    "observed_comfort",
    "observed_comfort_distribution",
    "plot_observed_comfort_distribution",
    "plot_z_class_matches",
    "process_dataframe",
    "process_live_snapshot",
    "read_csv_snapshot",
    "read_excel_snapshot",
    "read_sql_snapshot",
    "summarise_dc3",
    "subset_ashrae_db2",
    "thermal_sensation_label",
    "validate_dataframe",
    "z_class_records",
    "z_class_match_table",
    "z_class_summary",
]

__version__ = "0.1.0"
