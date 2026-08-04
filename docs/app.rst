Companion App
=============

The Streamlit companion app now lives in a separate project, ``DC3-App``. This
package repository, ``DC3-Project``, contains the reusable ``dc3model_v1`` Python
library: classification rules, validation contracts, dataset loaders,
geography helpers, live snapshot utilities, and package API documentation.

The app repository depends on the installed ``dc3model_v1`` package for
classification, observed-comfort computation, Z-class matching, ASHRAE DB II
loading, and figure export. It does not maintain a separate DC3 rule
implementation.

Local App Development
---------------------

When both repositories are checked out side by side, install the package first
and then install the app:

.. code-block:: bash

   cd ../DC3-App
   python -m pip install -e ../DC3-Project[viz,live]
   python -m pip install -e .[dev]
   dc3-model-app

Or use the app module launcher:

.. code-block:: bash

   python -m dc3_model_app.launcher --server.port 8506

Upload Handling
---------------

The app starts with the packaged ASHRAE DB II dataset. The upload control is
shown only after selecting ``Upload file``. CSV, XLSX, and XLS files are
supported through the ``app`` extra. Multiple uploaded files are staged for
convenience, but the app analyses one selected file at a time rather than
automatically merging arbitrary schemas. The active file is tagged with a
``dc3_source_file`` column for traceability. Missing optional columns are
retained as missing values; missing required mappings or required DC3 values
are reported through validation and invalid-row metadata.

Filtering Performance
---------------------

The companion app uses a session-local in-memory filter index for the active
processed dataset. Filter controls are applied explicitly, and only the
selected dashboard view is rendered after application. This avoids repeatedly
scanning the full dataframe and rebuilding every visualisation during filter
setup.

Build App Documentation
-----------------------

Build the separate app manual from the ``DC3-App`` root:

.. code-block:: bash

   python -m sphinx -b html docs docs/_build/html

During local development, the Streamlit app opens the app manual from:

.. code-block:: text

   http://localhost:8512

The package documentation remains available separately at:

.. code-block:: text

   http://localhost:8511
