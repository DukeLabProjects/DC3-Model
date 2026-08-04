Data Sources
============

Packaged ASHRAE DB II
---------------------

The packaged ASHRAE Global Thermal Comfort Database II file is available in
the app as the default startup dataset. The package keeps an attribution file
with the dataset export and provides country/city subset ZIP downloads that
include:

- selected CSV records,
- ``ATTRIBUTION.txt``,
- ``manifest.json`` with row counts and selected fields.

The ASHRAE DB II fields are recognised automatically where possible. This
lets the app prefill the required DC3 mapping and common metadata fields while
still allowing users to override the mapping.

Uploaded Files
--------------

The upload control is shown only when ``Upload file`` is selected as the data
source. Users may upload one or more ``.csv``, ``.xlsx``, or ``.xls`` files.
Multiple uploaded files are staged for convenience, but the app analyses one
selected file at a time. This avoids unsafe automatic merging when files do
not share the same schema or when shared DC3 columns would create a sparse
combined dataset. When more than one file is uploaded, the sidebar shows a
``File to analyse`` selector.

The active file is tagged with a ``dc3_source_file`` column so exported records
can be traced back to the file they came from.

Uploaded data is not stored permanently by the app. Saved analysis states
store lightweight UI settings only, not full uploaded datasets.

Missing Data
------------

The app and package are designed to report missing data clearly. Missing
required mappings or missing source columns are reported during validation.
Rows with missing or invalid required DC3 values can be retained with
``dc3_valid=False`` and a ``dc3_error`` message when ``Keep invalid rows`` is
enabled. Optional metadata and environmental fields may contain missing values;
filters and visual summaries either preserve them, label them as missing, or
coerce them to numeric missing values depending on the selected view.

Recommended Minimum Columns
---------------------------

A dataset must include fields that can be mapped to:

- thermal sensation,
- thermal preference,
- thermal acceptability.

Recommended optional fields include:

- country,
- city,
- season,
- building type,
- building cooling strategy,
- air temperature,
- relative humidity,
- air speed,
- globe temperature,
- mean radiant temperature,
- latitude and longitude for city maps when a location is not recognised by
  the internal offline lookup.
