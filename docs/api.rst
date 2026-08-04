API Reference
=============

The public API implements the DC3 model described by Duke et al. (2026).

Core
----

.. autosummary::
   :toctree: generated

   dc3.observed_comfort
   dc3.thermal_sensation_label
   dc3.classify_dc3
   dc3.encode_dc3
   dc3.decode_dc3
   dc3.describe_dc3
   dc3.dc3_codebook

Batch
-----

.. autosummary::
   :toctree: generated

   dc3.validate_dataframe
   dc3.process_dataframe
   dc3.summarise_dc3
   dc3.ValidationReport

Datasets
--------

.. autosummary::
   :toctree: generated

   dc3.load_demo_data
   dc3.load_ashrae_db2
   dc3.ashrae_db2_path
   dc3.ashrae_default_mapping
   dc3.subset_ashrae_db2
   dc3.create_ashrae_subset_zip

Geography
---------

.. autosummary::
   :toctree: generated

   dc3.country_to_iso3
   dc3.city_coordinates
   dc3.enrich_geography

Analytics
---------

.. autosummary::
   :toctree: generated

   dc3.dc3_class_order
   dc3.dc3_color_map
   dc3.dc3_distribution
   dc3.dc3_matrix
   dc3.environmental_summary
   dc3.observed_comfort_distribution
   dc3.z_class_match_table
   dc3.z_class_summary
   dc3.z_class_records

Plot Export
-----------

.. autosummary::
   :toctree: generated

   dc3.export_figure

Live
----

.. autosummary::
   :toctree: generated

   dc3.process_live_snapshot
   dc3.read_csv_snapshot
   dc3.read_excel_snapshot
   dc3.read_sql_snapshot
   dc3.LiveSnapshot

Exceptions
----------

.. autosummary::
   :toctree: generated

   dc3.DC3Error
   dc3.DC3InputError
   dc3.DC3ValidationError
