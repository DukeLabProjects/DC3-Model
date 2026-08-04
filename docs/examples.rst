Examples
========

These examples are intentionally small enough to copy into a Python shell,
notebook, or script. The pip install command is shown as a comment because it
is normally run once before starting Python.

Single Datapoint
----------------

Classify one occupant feedback record and retrieve its numeric equivalence.

.. code-block:: python

   # python -m pip install dc3model_v1
   from dc3 import classify_dc3, encode_dc3, decode_dc3, describe_dc3

   label = classify_dc3(
       thermal_sensation=0,
       thermal_preference="no_change",
       thermal_acceptability=1,
   )
   code = encode_dc3(label)
   decoded = decode_dc3(code)
   description = describe_dc3(label)

   print(label)
   print(code)
   print(decoded["label"])
   print(description["observed_comfort"])

Expected output:

.. code-block:: text

   D
   11
   D
   True

Small Dataframe
---------------

Process a dataframe with the three required DC3 fields. Optional fields such
as country, city, season, and environmental measurements can remain in the
dataframe and be used later for filtering or summaries.

.. code-block:: python

   # python -m pip install dc3model_v1
   import pandas as pd
   from dc3 import process_dataframe, summarise_dc3

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

   print(processed[["dc3_label", "dc3_code", "observed_comfort", "is_z_class"]].to_string(index=False))
   print(summary.sort_values("dc3_label").to_string(index=False))

Expected output:

.. code-block:: text

    dc3_label  dc3_code  observed_comfort  is_z_class
            D        11              True       False
           E-        13             False       False
            Z        22             False        True
    dc3_label  count  percentage
            D      1   33.333333
           E-      1   33.333333
            Z      1   33.333333

Validation Before Processing
----------------------------

Use ``validate_dataframe`` when a user maps columns manually.

.. code-block:: python

   # python -m pip install dc3model_v1
   import pandas as pd
   from dc3 import validate_dataframe

   df = pd.DataFrame({"TS": [0], "TP": ["no_change"], "TA": [1]})
   report = validate_dataframe(
       df,
       columns={
           "thermal_sensation": "TS",
           "thermal_preference": "TP",
           "thermal_acceptability": "TA",
       },
   )

   print(report.valid)
   print(report.mapped_fields)

Expected output:

.. code-block:: text

   True
   ('thermal_sensation', 'thermal_preference', 'thermal_acceptability')

Packaged ASHRAE DB II Sample
----------------------------

The package includes ASHRAE DB II as reference/test data. Use the default
mapping so the source columns are mapped to DC3 canonical fields.

.. code-block:: python

   # python -m pip install dc3model_v1
   from dc3 import load_ashrae_db2, ashrae_default_mapping, process_dataframe

   df = load_ashrae_db2(nrows=25)
   processed = process_dataframe(df, ashrae_default_mapping())

   print(df.shape[0])
   print(processed["dc3_valid"].sum() > 0)
   print({"dc3_label", "dc3_code", "observed_comfort"} <= set(processed.columns))

Expected output:

.. code-block:: text

   25
   True
   True

Subset ASHRAE Data And Export Attribution ZIP
---------------------------------------------

When sharing ASHRAE-derived subsets, use the package ZIP helper so the
attribution file travels with the data.

.. code-block:: python

   # python -m pip install dc3model_v1
   from io import BytesIO
   import zipfile
   from dc3 import create_ashrae_subset_zip, subset_ashrae_db2

   subset = subset_ashrae_db2(countries=["India"], nrows=5000)
   archive_bytes = create_ashrae_subset_zip(
       subset.head(3),
       dataset_name="india_sample",
       manifest={"country_filter": "India"},
   )

   with zipfile.ZipFile(BytesIO(archive_bytes)) as archive:
       print(sorted(archive.namelist()))

Expected output:

.. code-block:: text

   ['ATTRIBUTION.txt', 'india_sample.csv', 'manifest.json']

Environmental Summary
---------------------

Summarise environmental variables by DC3 class.

.. code-block:: python

   # python -m pip install dc3model_v1
   import pandas as pd
   from dc3 import environmental_summary

   df = pd.DataFrame(
       {
           "dc3_label": ["D", "D", "E-"],
           "Air temperature": [24.0, 26.0, 28.0],
           "Relative humidity": [50.0, 55.0, 60.0],
       }
   )
   summary = environmental_summary(df, ["Air temperature", "Relative humidity"])
   print(summary[["dc3_label", "variable", "count", "mean"]].head(3).to_string(index=False))

Expected output:

.. code-block:: text

    dc3_label          variable  count  mean
            D   Air temperature      2  25.0
           E-   Air temperature      1  28.0
            D Relative humidity      2  52.5

Observed Comfort And Z-Class
----------------------------

Observed comfort and Z-class summaries are computed from processed records.

.. code-block:: python

   # python -m pip install dc3model_v1
   import pandas as pd
   from dc3 import (
       observed_comfort_distribution,
       process_dataframe,
       z_class_match_table,
       z_class_summary,
   )

   df = pd.DataFrame({"TS": [0, 0, 1], "TP": ["no_change", "no_change", "cooler"], "TA": [1, 0, 1]})
   columns = {
       "thermal_sensation": "TS",
       "thermal_preference": "TP",
       "thermal_acceptability": "TA",
   }
   processed = process_dataframe(df, columns)

   print(observed_comfort_distribution(processed).to_string(index=False))
   print(z_class_summary(processed))
   print(z_class_match_table(processed)[["thermal_sensation_label", "count"]].to_string(index=False))

Geography Enrichment
--------------------

Country codes and known ASHRAE city coordinates can be derived offline.

.. code-block:: python

   # python -m pip install dc3model_v1
   import pandas as pd
   from dc3 import enrich_geography

   df = pd.DataFrame({"Country": ["India"], "City": ["Delhi"]})
   enriched, mapping = enrich_geography(df, {"country": "Country", "city": "City"})

   print(mapping)
   print(enriched[["dc3_country_code", "dc3_latitude", "dc3_longitude"]].round(3).to_string(index=False))

Expected output:

.. code-block:: text

   {'country': 'Country', 'city': 'City', 'country_code': 'dc3_country_code', 'latitude': 'dc3_latitude', 'longitude': 'dc3_longitude'}
    dc3_country_code  dc3_latitude  dc3_longitude
                 IND        28.614         77.209

Live Snapshot
-------------

``process_live_snapshot`` is useful when the same mapping is reused for
polling, database snapshots, or repeated uploads.

.. code-block:: python

   # python -m pip install dc3model_v1
   import pandas as pd
   from dc3 import process_live_snapshot

   df = pd.DataFrame({"TS": [0, 1], "TP": ["no_change", "cooler"], "TA": [1, 1]})
   columns = {
       "thermal_sensation": "TS",
       "thermal_preference": "TP",
       "thermal_acceptability": "TA",
   }

   snapshot = process_live_snapshot(df, columns, last_rows=1)
   print(snapshot.raw_rows)
   print(snapshot.processed["dc3_label"].tolist())

Expected output:

.. code-block:: text

   1
   ['E-']

Plot Figure
-----------

Plotting helpers require the optional ``viz`` dependencies. In notebooks,
use ``fig.show()``. In scripts, you can export figures through
``export_figure``.

.. code-block:: python

   # python -m pip install "dc3model_v1[viz]"
   import pandas as pd
   from dc3 import dc3_distribution, plot_dc3_distribution

   distribution = dc3_distribution(
       pd.DataFrame({"dc3_label": ["D", "E-", "Z"]}),
       include_zero_count_classes=False,
   )
   fig = plot_dc3_distribution(distribution)
   print(fig.data[0].type)

Expected output:

.. code-block:: text

   bar
