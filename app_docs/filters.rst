Dynamic Filters
===============

The filter system is dynamic. It inspects the mapped dataset and suggests a
small default set, then lets the user add or remove filters.

Default Filters
---------------

Common default filters include:

- country,
- city,
- season,
- building type,
- building cooling strategy,
- DC3 class,
- observed comfort,
- Z-class status.

The user can remove any default filter. This is useful when a default field is
too sparse or when the research question needs a different grouping.

Apply Filters
-------------

Filter controls are grouped inside an apply form. Changing checkboxes,
adding/removing active filters, or moving numeric sliders does not update the
dashboard immediately. The app updates filtered tables, charts, maps, and
exports only after the user clicks an explicit filter action such as
``Apply filters``, ``Select all``, or ``Unselect all``. This keeps exploratory
filter adjustment from repeatedly recomputing the visual dashboard.

The ``Reset filters`` button clears filter widget state and returns the
dashboard to the default filter configuration.

Session Filter Index
--------------------

For each processed dataset, the app builds a lightweight in-memory filter
index for the current user session. Categorical filters use precomputed value
arrays, numeric filters use precomputed numeric arrays, and active filters are
combined with a boolean row mask. The dataframe is sliced once after the mask
is resolved.

This behaves like a small session-local database index without adding an
external database dependency or sharing user data across sessions.

Qualitative Filters
-------------------

Text and categorical fields use searchable checkbox dropdowns with:

- select all,
- unselect all,
- individual include/exclude controls.

Individual checkbox edits are staged until ``Apply filters`` is clicked.

Country And City Filters
------------------------

Country and city filters are hierarchical. When both filters are active, the
country filter is applied first and the city checklist is rebuilt from the
remaining records. This means selecting India, for example, shows only the
cities present in the filtered Indian records rather than every city in the
full dataset.

Numeric Filters
---------------

Numeric fields use range sliders. When the slider remains at the full detected
range, missing values are preserved so sparse optional columns do not
accidentally remove records. When a range is narrowed, the app can optionally
keep or remove missing values.

Filtered Outputs
----------------

All charts, maps, tables, and downloads use the filtered dataset shown in the
dashboard. Table CSV downloads export only the visible table data.
