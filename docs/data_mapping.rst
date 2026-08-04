Data Mapping And Validation
===========================

The required DC3 fields mirror the subjective inputs used by Duke et al.
(2026): thermal sensation, thermal preference, and thermal acceptability.

Why Mapping Exists
------------------

User datasets rarely use the same column names. DC3 Model therefore asks
users to map their own columns onto canonical DC3 field names.

Minimum Required Fields
-----------------------

Deterministic classification requires:

``thermal_sensation``
   Thermal sensation vote. Valid values are ``-3`` through ``3``. Common
   text values such as ``cold``, ``slightly cool``, ``neutral``,
   ``slightly warm``, and ``hot`` are also accepted. Decimal values within
   the ASHRAE seven-point range are discretised to the nearest integer state;
   the processed row records this in ``dc3_normalization_note``.

``thermal_preference``
   Occupant preference. Canonical values are ``cooler``, ``no_change``,
   and ``warmer``. Common variants such as ``prefer cooler``, ``no change``,
   ``same``, and ``want warmer`` are normalised.

``thermal_acceptability``
   Acceptability flag. Canonical values are ``1`` for acceptable and ``0``
   for unacceptable. Text values such as ``acceptable``, ``unacceptable``,
   ``yes``, and ``no`` are accepted.

Example Mapping
---------------

.. code-block:: python

   columns = {
       "thermal_sensation": "TS",
       "thermal_preference": "Preference",
       "thermal_acceptability": "Acceptability",
   }

   processed = process_dataframe(df, columns)

Generated Columns
-----------------

``process_dataframe`` appends these columns:

``observed_comfort``
   Boolean OC result.

``dc3_label``
   Human-readable DC3 class such as ``D``, ``E-``, or ``Z``.

``dc3_code``
   Numeric DC3 code.

``thermal_sensation_normalized``
   Canonical integer sensation value.

``thermal_sensation_label``
   DC3 letter ``A`` through ``G``.

``thermal_preference_normalized``
   Canonical preference value.

``thermal_acceptability_normalized``
   Canonical acceptability value.

``preference_group``
   Numeric preference group for non-Z labels.

``comfort_zone``
   Broad interpretive group such as ``most_comfortable_zone``,
   ``comfortable``, ``transitional``, or ``z_class``.

``recommended_direction``
   ``maintain``, ``cooler``, ``warmer``, or ``review_response``.

``is_z_class``
   Whether the row is a Z-class response.

``dc3_normalization_note``
   Normalisation trace such as decimal thermal sensation discretisation.

``dc3_valid``
   Whether classification succeeded.

``dc3_error``
   Error message when classification failed.

Invalid Rows
------------

The engine is designed to preserve information. Invalid rows are kept by
default and marked with validation metadata. This is useful in the app because
users can inspect problematic records instead of losing them silently.

Optional Filter Fields
----------------------

The app and batch APIs can also map optional fields for filtering and grouped
analysis:

``country``
   Country or region where the feedback was collected.

``city``
   City, campus, site, or local zone.

``season``
   Season label supplied by the dataset.

``building_type``
   Building category such as office, classroom, residential, or mixed use.

``cooling_strategy``
   Building cooling strategy, for example AC, mixed mode, fan, or natural
   ventilation.

``cooling_operation_mode``, ``heating_strategy``
   Additional control strategy metadata.

``koppen_climate``, ``climate``
   Climate classification fields for cross-climate analysis.

``year``, ``age``, ``sex``
   Time and participant metadata when available.

``air_temperature``, ``operative_temperature``, ``radiant_temperature``, ``globe_temperature``, ``relative_humidity``, ``air_velocity``
   Environmental measurements used for summaries, filtering, and comparisons.

``clo``, ``met``, ``pmv``, ``ppd``, ``set``, ``thermal_comfort``
   Optional comfort-analysis fields.

``database``, ``publication``, ``data_contributor``
   Source provenance fields, useful for reference datasets such as ASHRAE DB
   II.

DC3 Codebook
------------

Use :func:`dc3.dc3_codebook` to output the DC3 label and numeric equivalence
table.

.. code-block:: python

   from dc3 import dc3_codebook

   rows = dc3_codebook()
   table = dc3_codebook(as_dataframe=True)

The table includes labels such as ``A-``, ``A``, ``A+`` through ``G+`` and
the reserved ``Z`` class, with numeric codes ``1`` through ``22``.
