Package Documentation
=====================

The app runs on top of the installed ``dc3-model`` package. Use the package
documentation when you need:

- Python method calls,
- deterministic DC3 classification rules,
- generated API reference pages,
- ASHRAE DB II loader functions,
- figure export functions,
- package release and PyPI publishing notes.

During local development, the package documentation is served separately at:

.. code-block:: text

   http://localhost:8511

Build the package documentation from the project root:

.. code-block:: bash

   python -m sphinx -b html docs docs/_build/html
