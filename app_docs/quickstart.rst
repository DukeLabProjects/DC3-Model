Quickstart
==========

Install App Dependencies
------------------------

From the project root, install the package with the app and visualisation
extras:

.. code-block:: bash

   python -m pip install -e .[app,viz,live]

Launch The App
--------------

Use the installed console command:

.. code-block:: bash

   dc3-model-app

If the Windows Scripts directory is not on ``PATH``, use the module launcher:

.. code-block:: bash

   python -m dc3.app.launcher --server.port 8506

Open the browser URL shown by Streamlit, normally:

.. code-block:: text

   http://localhost:8506

Open The App Documentation
--------------------------

The app sidebar places documentation links at the bottom of the control panel.
The app manual link uses the ``DC3_APP_DOCS_URL`` environment variable. During
local development the default URL is:

.. code-block:: text

   http://localhost:8512

Build and serve this manual locally:

.. code-block:: bash

   python -m sphinx -b html app_docs app_docs/_build/html
   python -m http.server 8512 --bind localhost --directory app_docs/_build/html

Sidebar Image
-------------

The sidebar uses a locally packaged DC3 concept diagram showing thermal
sensation, thermal acceptability, and thermal preference feeding DC3 codes. On
hover, the diagram darkens and explains that DC3 maps occupant feedback for
real-time comfort control and energy optimisation.
