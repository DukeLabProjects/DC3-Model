Model Specification
===================

This page documents the DC3 model rules implemented from Duke et al. (2026).
The reference citation is provided in :doc:`references`.

Notation
--------

For one occupant response, DC3 Model uses three subjective inputs:

``TS``
   Thermal sensation vote on the seven-point ASHRAE scale, where
   :math:`TS \in \{-3,-2,-1,0,1,2,3\}`.

``TP``
   Thermal preference, normalised to one of ``cooler``, ``no_change``,
   or ``warmer``.

``TA``
   Thermal acceptability, normalised to :math:`TA = 1` for acceptable and
   :math:`TA = 0` for unacceptable.

The package first normalises user input values, then applies the deterministic
rules below. The normalised values are retained in the processed dataframe so
users can audit how raw data were interpreted.

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

In compact form:

.. math::

   OC =
   \begin{cases}
   1, & TP = \mathrm{no\_change} \ \mathrm{and}\ TA = 1 \\
   0, & \mathrm{otherwise}
   \end{cases}

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

The letter mapping can be written as:

.. math::

   L(TS) =
   \begin{cases}
   A, & TS=-3 \\
   B, & TS=-2 \\
   C, & TS=-1 \\
   D, & TS=0 \\
   E, & TS=1 \\
   F, & TS=2 \\
   G, & TS=3
   \end{cases}

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

The suffix mapping is:

.. math::

   S(TP) =
   \begin{cases}
   -, & TP=\mathrm{cooler} \\
   \emptyset, & TP=\mathrm{no\_change} \\
   +, & TP=\mathrm{warmer}
   \end{cases}

Z-Class
-------

Following the Z-class interpretation in Duke et al. (2026), ``Z`` is preserved
as a flag category. It appears when a user reports
``no_change`` preference while also reporting the environment as
unacceptable. The package does not silently reclassify ``Z`` because the
Duke et al. (2026) framework treats it as a heterogeneous category that may
reflect survey wording, semantic mismatch, or genuinely mixed occupant
responses.

Formally, the Z class is assigned before the usual suffix rule:

.. math::

   DC3 = Z \quad \mathrm{if}\quad TP=\mathrm{no\_change}\ \mathrm{and}\ TA=0

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

DC3 Algorithm
-------------

The complete deterministic procedure implemented in :func:`dc3.classify_dc3`
is:

.. code-block:: text

   Input: thermal_sensation, thermal_preference, thermal_acceptability

   1. Normalise thermal_sensation to TS in {-3, -2, -1, 0, 1, 2, 3}.
   2. Normalise thermal_preference to TP in {cooler, no_change, warmer}.
   3. Normalise thermal_acceptability to TA in {0, 1}.
   4. Compute observed comfort:
          OC = 1 if TP == no_change and TA == 1 else 0
   5. If TP == no_change and TA == 0:
          DC3 label = Z
          DC3 code = 22
      Else:
          base letter = L(TS)
          suffix = S(TP)
          DC3 label = base letter + suffix
          DC3 code = 3 * (TS + 3) + preference_group(TP)

where:

.. math::

   preference\_group(TP) =
   \begin{cases}
   1, & TP=\mathrm{cooler} \\
   2, & TP=\mathrm{no\_change} \\
   3, & TP=\mathrm{warmer}
   \end{cases}

Since :math:`TS + 3` maps thermal sensation from :math:`[-3,3]` to the
zero-based index :math:`[0,6]`, the non-Z classes are encoded from
``1`` to ``21``. The Z class is assigned ``22`` and kept outside the regular
seven-by-three DC3 state space.

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
