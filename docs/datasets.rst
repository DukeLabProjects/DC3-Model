Reference Datasets
==================

ASHRAE Global Thermal Comfort Database II
-----------------------------------------

DC3 Model can ship with ``ashrae_db2.csv`` as a packaged reference dataset for
testing, demonstrations, and reproducible examples. The dataset is loaded with:

.. code-block:: python

   from dc3 import load_ashrae_db2, ashrae_default_mapping, process_dataframe

   df = load_ashrae_db2(nrows=10_000)
   mapping = ashrae_default_mapping()
   processed = process_dataframe(df, mapping)

The default mapping connects the ASHRAE DB II source columns to the canonical
DC3 fields:

``Thermal sensation``
   Mapped to ``thermal_sensation``. Decimal votes are discretised to the
   nearest DC3 seven-point state and recorded in ``dc3_normalization_note``.

``Thermal preference``
   Mapped to ``thermal_preference``.

``Thermal sensation acceptability``
   Mapped to ``thermal_acceptability``.

``Country``, ``City``, ``Season``, ``Building type``, ``Cooling startegy_building level``
   Mapped as optional grouping/filtering dimensions.

Additional optional dimensions include climate, Koppen class, sex, age, year,
heating strategy, operation mode, PMV, PPD, SET, Clo, Met, humidity, velocity,
and multiple temperature measurements.

Direct Data Access
------------------

The packaged ASHRAE DB II file is distributed inside ``dc3model_v1`` and can be
loaded directly after installation. Prefer ``load_ashrae_db2`` for normal
analysis because it reads the packaged resource without requiring users to know
where the package is installed:

.. code-block:: python

   from dc3 import load_ashrae_db2

   df = load_ashrae_db2()
   sample = load_ashrae_db2(nrows=1_000)

When a filesystem path is needed for inspection, provenance checks, or
integration with another tool, use ``ashrae_db2_path``:

.. code-block:: python

   from dc3 import ashrae_db2_path

   path = ashrae_db2_path()
   print(path)

The installed package also exposes ``ashrae_default_mapping`` so apps and
scripts can process the packaged dataset without manually rebuilding the
column map:

.. code-block:: python

   from dc3 import ashrae_default_mapping, load_ashrae_db2, process_dataframe

   df = load_ashrae_db2()
   processed = process_dataframe(df, ashrae_default_mapping())

Subset ZIP Export
-----------------

Use ``create_ashrae_subset_zip`` when a selected subset should be shared with
the data and attribution note together:

.. code-block:: python

   from pathlib import Path
   from dc3 import subset_ashrae_db2, create_ashrae_subset_zip

   subset = subset_ashrae_db2(countries=["India", "Japan"])
   archive = create_ashrae_subset_zip(
       subset,
       dataset_name="ashrae_india_japan",
       manifest={"countries": ["India", "Japan"]},
   )
   Path("ashrae_india_japan.zip").write_bytes(archive)

The ZIP contains:

- a CSV file,
- ``ATTRIBUTION.txt``,
- ``manifest.json``.

Attribution
-----------

The packaged attribution text is based on the Dryad dataset record by
Parkinson et al. (2022) and the database paper by Foldvary Licina et al.
(2018). See :doc:`references` for full citations and source links.
