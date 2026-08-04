Model Specification
===================

This page documents the DC3 model rules implemented from Duke et al. (2026).
The reference citation is provided in :doc:`references`.

Observed Comfort
----------------

Observed Comfort, abbreviated as OC, is a binary operational label.

An observation is comfortable only when both statements are true:

.. code-block:: text

   thermal_preference == "no_change"
   thermal_acceptability == 1

Every other combination is treated as uncomfortable for control purposes.
This includes records where the environment is marked acceptable but the
occupant still requests warmer or cooler conditions.

Thermal Sensation Axis
----------------------

The DC3 scale uses seven thermal sensation levels.

.. list-table::
   :header-rows: 1

   * - Thermal sensation
     - DC3 letter
     - Meaning
   * - -3
     - A
     - cold
   * - -2
     - B
     - cool
   * - -1
     - C
     - slightly cool
   * - 0
     - D
     - neutral
   * - 1
     - E
     - slightly warm
   * - 2
     - F
     - warm
   * - 3
     - G
     - hot

Preference Suffix
-----------------

The suffix encodes occupant preference.

.. list-table::
   :header-rows: 1

   * - Condition
     - Example
     - Meaning
   * - no_change and acceptable
     - D
     - maintain the current state
   * - preference for cooler
     - E-
     - move toward cooler conditions
   * - preference for warmer
     - C+
     - move toward warmer conditions
   * - no_change and unacceptable
     - Z
     - review the response or survey wording

Z-Class
-------

Following the Z-class interpretation in Duke et al. (2026), ``Z`` is preserved
as a flag category. It appears when a user reports
``no_change`` preference while also reporting the environment as
unacceptable. The package does not silently reclassify ``Z`` because the
Duke et al. (2026) framework treats it as a heterogeneous category that may
reflect survey wording, semantic mismatch, or genuinely mixed occupant
responses.

Numeric Encoding
----------------

Each non-Z state has a structured numeric code:

.. code-block:: text

   dc3_code = 3 * thermal_sensation_index + preference_group

where:

.. code-block:: text

   thermal_sensation_index = 0..6
   cooler preference = 1
   no_change / comfortable = 2
   warmer preference = 3
   Z = 22

Examples:

.. list-table::
   :header-rows: 1

   * - Label
     - Code
     - Interpretation
   * - A-
     - 1
     - cold and prefers cooler
   * - D
     - 11
     - neutral, no change, acceptable
   * - G+
     - 21
     - hot and prefers warmer
   * - Z
     - 22
     - inconsistent or mixed response flag

Interpretation Of High ML Accuracy
----------------------------------

When machine learning models use thermal sensation and thermal preference
to predict DC3, they are partly learning to reconstruct the deterministic
rules used to create the DC3 label. The documentation and reports should
therefore distinguish between:

``rule reconstruction``
   Predicting labels from variables that directly define those labels.

``environment-only inference``
   Predicting comfort states from environmental measurements such as air
   temperature, relative humidity, and air velocity.
