Visualisations
==============

The app visualisations are intended for scientific review and publication
preparation.

Active View Rendering
---------------------

Only the selected dashboard view is rendered after filters are applied. This
keeps expensive maps, violin plots, Z-class charts, and export previews from
being recomputed when the user is working in another view.

DC3 Class Views
---------------

DC3 class plots follow the class ordering used in Duke et al. (2026), with the
ambiguous ``Z`` class placed at the far right. The default class colour scheme
moves from cold-side blue, through neutral green, to hot-side red.

Observed Comfort Views
----------------------

Observed comfort is computed internally from thermal preference and
acceptability. The app labels the two main states as:

- comfortable,
- uncomfortable.

Unknown values are retained when inputs are missing or invalid.

Environmental Views
-------------------

Mapped environmental variables can be plotted by DC3 class or observed
comfort. The app supports:

- box plots,
- violin plots,
- grouped summaries,
- comparisons by country, city, season, building type, cooling strategy, and
  other mapped dimensions.

Colour Palettes
---------------

Users can choose from preset palettes or build a custom palette by selecting
the desired number of colours. The selected palette is applied to the
available chart types where appropriate.

Z-Class Matching
----------------

The Z-class tab shows ambiguous records and groups matching patterns so the
researcher can inspect where a respondent's inputs do not resolve cleanly into
a standard DC3 class.
