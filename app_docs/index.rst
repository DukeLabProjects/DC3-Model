DC3 Model App
=============

DC3 Model App is the user-facing Streamlit application for exploring the
D-centred thermal comfort classification workflow. It helps users import
occupant-feedback datasets, map local column names to DC3 fields, filter
records, compare countries or cities, inspect observed comfort, review Z-class
matches, and export publication-ready figures and tables.

The app calls the installed ``dc3-model`` package for classification and
analytics. It is therefore documented separately from the package API: the
package documentation explains reusable Python methods, while this app manual
explains interactive operation, data preparation, dashboards, state handling,
and export workflows.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started
   :hidden:

   quickstart
   workflow

.. toctree::
   :maxdepth: 2
   :caption: Data Setup
   :hidden:

   data_sources
   mapping
   filters
   state

.. toctree::
   :maxdepth: 2
   :caption: Analysis Views
   :hidden:

   visualisations
   maps
   live_operation
   exports

.. toctree::
   :maxdepth: 2
   :caption: Reference
   :hidden:

   maintenance
   package_docs

.. grid:: 1 1 2 3
   :gutter: 3
   :class-container: sd-text-center

   .. grid-item-card:: Import And Map
      :link: mapping
      :link-type: doc

      Use packaged ASHRAE DB II data or upload CSV/XLSX data, then map only
      the required DC3 fields and any optional fields needed for analysis.

   .. grid-item-card:: Filtered Analysis
      :link: filters
      :link-type: doc

      Add or remove qualitative checkbox filters and numeric range sliders.
      Charts, tables, maps, and downloads use the filtered dataset.

   .. grid-item-card:: Visual Dashboards
      :link: visualisations
      :link-type: doc

      Inspect DC3 classes, OC comfort status, environmental box or violin
      plots, country/city summaries, Z-class matching, and codebook tables.

   .. grid-item-card:: Free Maps
      :link: maps
      :link-type: doc

      Compare countries and cities using Plotly geo views that require no paid
      map tiles, subscriptions, API keys, or automatic online geocoding.

   .. grid-item-card:: Live Operation
      :link: live_operation
      :link-type: doc

      Use demo, file, or SQL snapshots as a practical path toward real-time
      occupant feedback and HVAC-energy optimisation workflows.

   .. grid-item-card:: Publication Export
      :link: exports
      :link-type: doc

      Download filtered tables as CSV, ASHRAE subsets as ZIP packages, and
      figures as PNG, SVG, or PDF with print-oriented sizing controls.

Reference Paper
---------------

The app uses the DC3 model implemented in the package from Duke et al. (2026):

O.P. Duke, A. Kowli, and J. Zhou, "Development of a D-centred thermal comfort
classification model based on the ASHRAE global thermal comfort database II:
an Indian case study", *Building and Environment*, 293, 114324, 2026.
