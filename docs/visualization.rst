Analytics And Visualisation
===========================

The visualisation helpers summarise the DC3 labels, OC states, and Z-class
flags derived from the Duke et al. (2026) classification framework.

DC3 Model separates visualisation into two layers:

``analytics helpers``
   Functions that return plain pandas dataframes or dictionaries. These work
   with the core package dependencies.

``plot helpers``
   Optional functions that produce Plotly figures. These require the ``viz``
   extra.

Class Distribution
------------------

Use :func:`dc3.dc3_distribution` after processing a dataframe.

.. code-block:: python

   from dc3 import dc3_distribution

   distribution = dc3_distribution(processed)

The result contains:

``dc3_label``
   DC3 class label.

``count``
   Number of records in that class.

``percentage``
   Percentage of all rows represented by that class.

By default, the output includes zero-count rows for all canonical DC3 classes.
This keeps dashboards stable when filters change.

Class Order And Colours
-----------------------

Use :func:`dc3.dc3_class_order` and :func:`dc3.dc3_color_map` when building
figures outside the app.

.. code-block:: python

   from dc3 import dc3_class_order, dc3_color_map

   order = dc3_class_order()
   colours = dc3_color_map()

The canonical visual order follows the Duke et al. (2026) DC3 paper:
``A-``, ``A``, ``A+`` through ``G-``, ``G``, ``G+``, with ``Z`` kept at the
far right. The ``Z`` class is intentionally separated because it is a special
matching category rather than a normal point in the 7-by-3 DC3 state space.
The colour map follows the thermal interpretation of the classes: colder
classes on the left are blue, neutral classes around the middle are green, and
hotter classes on the right move toward red. ``Z`` is shown in neutral gray.

DC3 Matrix
----------

Use :func:`dc3.dc3_matrix` to create the 7-by-3 model space.

.. code-block:: python

   from dc3 import dc3_matrix

   matrix = dc3_matrix(processed)

Rows are thermal sensation labels ``A`` through ``G``. Columns are:

``cooler``
   Preference for cooler conditions.

``no_change``
   Comfortable no-change states.

``warmer``
   Preference for warmer conditions.

The ``Z`` class is excluded from this matrix because it is a flag category,
not a normal position in the 7-by-3 DC3 space.

Environmental Summary
---------------------

Use :func:`dc3.environmental_summary` to summarise numeric columns by DC3
class.

.. code-block:: python

   from dc3 import environmental_summary

   summary = environmental_summary(
       processed,
       ["Air temperature", "Relative humidity", "Air velocity"],
   )

The function coerces non-numeric values to missing values and returns count,
mean, median, minimum, maximum, 25th percentile, and 75th percentile.

In the app, environmental variables can be displayed as box plots or full
violin density plots. The x-axis uses the Duke et al. (2026) DC3 order and
supports colouring by either DC3 class or internally computed observed
comfort. Observed comfort is displayed as ``Comfortable``,
``Uncomfortable``, and ``Unknown`` instead of raw boolean values.

Z-Class Review
--------------

Use :func:`dc3.z_class_summary` and :func:`dc3.z_class_records` to inspect
ambiguous or inconsistent responses.

.. code-block:: python

   from dc3 import z_class_summary, z_class_records

   info = z_class_summary(processed)
   z_rows = z_class_records(processed)

Observed Comfort
----------------

Use :func:`dc3.observed_comfort_distribution` to summarise the internally
computed OC states.

.. code-block:: python

   from dc3 import observed_comfort_distribution

   oc = observed_comfort_distribution(processed)

The app visualises this output as comfortable, uncomfortable, and unknown
records.

Z-Class Matching Table
----------------------

Use :func:`dc3.z_class_match_table` to see which internally normalised records
matched the Z-class rule.

.. code-block:: python

   from dc3 import z_class_match_table

   matches = z_class_match_table(processed)

By default, this groups Z-class records by thermal sensation, preference, and
acceptability. This is useful when reviewing whether Z-class responses are
survey wording effects, ambiguous responses, or data-quality issues.

Optional Plotly Charts
----------------------

Install visualisation dependencies:

.. code-block:: bash

   python -m pip install -e .[viz]

Then create figures:

.. code-block:: python

   from dc3.viz import plot_dc3_distribution, plot_dc3_matrix

   fig1 = plot_dc3_distribution(distribution)
   fig2 = plot_dc3_matrix(matrix)

Static Plot Export
------------------

Use :func:`dc3.export_figure` to export Plotly figures as ``png``, ``svg``, or
``pdf`` bytes.

.. code-block:: python

   from dc3 import export_figure

   png_bytes = export_figure(fig1, format="png", width=1800, height=1200, scale=2)

Static export uses Plotly's Kaleido backend. The app exposes standard, high,
and publication quality presets.
