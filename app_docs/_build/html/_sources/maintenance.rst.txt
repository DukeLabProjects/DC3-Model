Documentation Maintenance
=========================

The app documentation is separate from the package documentation because the
two projects have different audiences.

Package Documentation
---------------------

The package documentation explains importable Python functions, API contracts,
data loaders, validation rules, and generated docstrings. It supports a paper
or technical report focused on the reusable ``dc3-model`` package.

App Documentation
-----------------

This documentation explains the Streamlit interface, analysis workflow,
interactive filters, visual dashboards, state handling, live operation, map
views, and export behaviour. It supports a separate paper or report focused on
the user-facing DC3 Model App.

Update Rule
-----------

Whenever a major app feature changes, update this manual in the same pull
request or development change. Major app changes include:

- new tabs or dashboard sections,
- changed source loading behaviour,
- changed mapping or validation behaviour,
- new filters,
- new plots or map outputs,
- changed export formats,
- state handling changes,
- live-operation workflow changes.

Local Build
-----------

.. code-block:: bash

   python -m sphinx -b html app_docs app_docs/_build/html
