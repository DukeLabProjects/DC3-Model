Changelog
=========

0.1.2
-----

Documentation and API usability release.

- Expanded API reference docstrings with runnable single-record and small
  dataframe examples.
- Expanded the examples chapter into a copy-paste cookbook for core
  classification, dataframe processing, ASHRAE DB II loading, geography,
  observed comfort, Z-class matching, live snapshots, and plotting.
- Added regression tests for representative documentation examples.
- Retained normalised thermal sensation labels on Z-class processed rows so
  Z-class matching tables remain easier to interpret.

0.1.0
-----

Initial development version.

- Deterministic OC and DC3 classification following Duke et al. (2026).
- DC3 label/code encoding and decoding.
- Dataframe processing with column mapping and validation metadata.
- Visual analytics for DC3, OC, environmental variables, and Z-class records.
- Streamlit app moved to the independent sibling ``DC3-App`` project for
  separate hosting, releases, and documentation.
- Package Sphinx documentation uses the PyData Sphinx Theme.
