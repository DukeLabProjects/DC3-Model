Installation
============

Python Version
--------------

DC3 Model supports Python 3.10 and newer.

Editable Development Install
----------------------------

From the project root:

.. code-block:: bash

   python -m pip install -e .[test,docs]

Verify the installation:

.. code-block:: bash

   python -m pytest
   python -m sphinx -b html docs docs/_build/html

Optional Extras
---------------

The package keeps the deterministic DC3 engine lightweight. Install optional
extras when you need visualisation, live database, or ML functionality.

.. list-table::
   :header-rows: 1

   * - Extra
     - Purpose
     - Install command
   * - ``viz``
     - Plotly/Matplotlib visualisations and static image export
     - ``python -m pip install -e .[viz]``
   * - ``live``
     - SQLAlchemy database snapshot polling
     - ``python -m pip install -e .[live]``
   * - ``ml``
     - Scikit-learn Random Forest utilities
     - ``python -m pip install -e .[ml]``
   * - ``docs``
     - Sphinx documentation with PyData theme
     - ``python -m pip install -e .[docs]``

Run The App
-----------

The Streamlit app is maintained in the sibling ``DC3-App`` project. For local
development with both repositories checked out side by side:

.. code-block:: bash

   cd ../DC3-App
   python -m pip install -e ../DC3-Project[viz,live]
   python -m pip install -e .[dev]
   dc3-model-app

On Windows, if the Python Scripts directory is not on ``PATH``, use the app
module launcher from the ``DC3-App`` environment:

.. code-block:: bash

   python -m dc3_model_app.launcher

You can pass Streamlit options through the launcher:

.. code-block:: bash

   dc3-model-app --server.port 8506 --server.headless true

Equivalent module form:

.. code-block:: bash

   python -m dc3_model_app.launcher --server.port 8506 --server.headless true

Upgrade The App
---------------

The app imports the installed ``dc3model_v1`` package. When a new package version
is released, upgrade the package in the app environment and relaunch the app:

.. code-block:: bash

   python -m pip install --upgrade dc3model_v1
   dc3-model-app

Build Documentation
-------------------

.. code-block:: bash

   python -m sphinx -b html docs docs/_build/html

Build the separate app manual from the ``DC3-App`` repository:

.. code-block:: bash

   python -m sphinx -b html docs docs/_build/html
