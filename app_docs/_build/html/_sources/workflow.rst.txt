Analysis Workflow
=================

The app workflow is designed for exploratory analysis first and operational
deployment later.

1. Start from the default packaged ASHRAE DB II data, or choose uploaded
   CSV/XLSX or synthetic demo data.
2. Review the raw-data summary and preview records.
3. Map the required DC3 columns: thermal sensation, thermal preference, and
   thermal acceptability.
4. Map environmental, geographic, and optional metadata columns only when they
   are useful for analysis.
5. Validate the mapped records and inspect invalid-row feedback.
6. Process the data through the deterministic DC3 engine.
7. Add, remove, and adjust filters, then click ``Apply filters``.
8. Review the dashboard tabs: overview, comfort/OC, environment, comparisons,
   maps, Z-class, codebook, live operation, and export.
9. Download filtered records, summary tables, ZIP packages, or figures.

Filtered Dataset Rule
---------------------

All analysis tabs use the last applied filtered dataset. When a country, city,
season, building type, cooling strategy, DC3 class, OC status, Z-class status,
or numeric range is selected, downstream tables and figures reflect those
records after ``Apply filters`` is clicked.

This rule is important because the app is meant to support research and future
control workflows where selected cohorts must be traceable.
