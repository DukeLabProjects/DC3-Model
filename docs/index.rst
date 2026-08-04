DC3 Model
=========

DC3 Model is a scientific Python package for the D-centred thermal comfort
classification model. It converts occupant feedback into interpretable DC3
states, numeric codes, observed comfort labels, and reusable analytics that
can support occupant-centred HVAC control. The implementation follows the DC3
framework introduced by Duke et al. (2026).

.. toctree::
   :maxdepth: 2
   :caption: Getting Started
   :hidden:

   quickstart
   installation

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   :hidden:

   model
   data_mapping
   datasets
   visualization
   examples
   app

.. toctree::
   :maxdepth: 2
   :caption: Reference
   :hidden:

   api
   references
   changelog
   release
   publishing

.. grid:: 1 1 2 3
   :gutter: 3
   :class-container: sd-text-center

   .. grid-item-card:: Deterministic DC3 Engine
      :link: model
      :link-type: doc

      Rule-based OC/DC3 classification, label encoding, decoding, and a
      complete codebook for labels ``A-`` through ``G+`` plus ``Z``.

   .. grid-item-card:: Data Processing
      :link: data_mapping
      :link-type: doc

      Robust column mapping, value normalisation, invalid-row reporting, and
      batch processing for real survey or building datasets.

   .. grid-item-card:: Visual Analytics
      :link: visualization
      :link-type: doc

      DC3 distributions, OC charts, Z-class matching summaries, environmental
      plots, and static figure export.

   .. grid-item-card:: Companion App
      :link: app
      :link-type: doc

      The Streamlit companion app now lives in the separate ``DC3-App`` project
      and depends on this package.

   .. grid-item-card:: Live Operation
      :link: app
      :link-type: doc

      Snapshot polling from demo streams, files, or SQL databases for future
      integration with HVAC optimisation workflows.

   .. grid-item-card:: API Reference
      :link: api
      :link-type: doc

      Generated API documentation from the package docstrings.

Key Features
------------

- DC3 labels and numeric code equivalence through :func:`dc3.dc3_codebook`.
- Observed Comfort classification from thermal preference and acceptability.
- Z-class preservation and matching analysis for ambiguous responses.
- Optional metadata filters for country, city, season, building type, and
  building cooling strategy, plus ASHRAE DB II climate and demographic fields.
- Packaged ASHRAE DB II loader, country/city comparison workflows, and ZIP
  subset export with attribution.
- Static plot export as PNG, SVG, or PDF.
- Separate PyData Sphinx documentation builds for the package and app, with
  generated API pages for the package.

Quick Start
-----------

.. code-block:: python

   from dc3 import classify_dc3, encode_dc3, decode_dc3

   label = classify_dc3(
       thermal_sensation=0,
       thermal_preference="no_change",
       thermal_acceptability=1,
   )

   print(label)             # D
   print(encode_dc3(label)) # 11
   print(decode_dc3(11))

Install For Development
-----------------------

.. code-block:: bash

   python -m pip install -e .[test,docs]
   python -m pytest
   python -m sphinx -b html docs docs/_build/html

Install all optional components:

.. code-block:: bash

   python -m pip install -e .[viz,live,ml,docs,test]

Reference Paper
---------------

DC3 Model implements the model described by :doc:`Duke et al. (2026) <references>`:

O.P. Duke, A. Kowli, and J. Zhou, "Development of a D-centred thermal comfort
classification model based on the ASHRAE global thermal comfort database II:
an Indian case study", *Building and Environment*, 293, 114324, 2026.
