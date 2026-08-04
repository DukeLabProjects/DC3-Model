Publishing To PyPI
==================

PyPI is the Python Package Index. After publishing, users will be able to
install the package with:

.. code-block:: bash

   python -m pip install dc3-model

The import name remains:

.. code-block:: python

   import dc3

Package Name
------------

The current distribution name is ``dc3-model``. Final ownership is only
secured after the first successful upload to PyPI.

Pre-Release Checklist
---------------------

Before publishing:

1. Confirm package metadata in ``pyproject.toml``.
2. Add a real ``LICENSE`` file.
3. Update ``README.md`` and include the Duke et al. (2026) citation.
4. Update ``docs/changelog.rst``.
5. Update the version in ``pyproject.toml`` and ``src/dc3/__init__.py``.
6. Run tests.
7. Build docs.
8. Build distribution files.
9. Upload to TestPyPI first.
10. Install from TestPyPI in a clean environment.
11. Publish to PyPI.

Build Locally
-------------

Install publishing tools:

.. code-block:: bash

   python -m pip install -e .[publish]

Clean previous builds:

.. code-block:: bash

   python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in ['build', 'dist']]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').glob('*.egg-info')]"

Build source and wheel distributions:

.. code-block:: bash

   python -m build

Check the package metadata:

.. code-block:: bash

   python -m twine check dist/*

Upload To TestPyPI
------------------

Create an account at https://test.pypi.org/ and create an API token.

Upload:

.. code-block:: bash

   python -m twine upload --repository testpypi dist/*

Test the install:

.. code-block:: bash

   python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ dc3-model

Upload To PyPI
--------------

Create an account at https://pypi.org/ and create an API token.

Upload:

.. code-block:: bash

   python -m twine upload dist/*

Install from PyPI:

.. code-block:: bash

   python -m pip install dc3-model

Install the independent app after publishing it separately:

.. code-block:: bash

   python -m pip install dc3-model-app
   dc3-model-app

If the console script is not on ``PATH``:

.. code-block:: bash

   python -m dc3_model_app.launcher

GitHub Trusted Publishing
-------------------------

For the long-term project, prefer PyPI Trusted Publishing instead of storing
long-lived API tokens in GitHub secrets. The workflow is:

1. Push the project to GitHub.
2. Create a GitHub Actions workflow for release publishing.
3. Register that workflow as a trusted publisher in PyPI.
4. Publish from GitHub Actions when a release is created.

This lets PyPI verify that the package came from the configured repository and
workflow.

Versioning
----------

Use semantic versioning once external users depend on the package:

``0.x``
   Early development. APIs may still change.

``1.0``
   Stable public API for deterministic DC3 classification and batch
   processing.

Patch releases
   Bug fixes and documentation corrections.

Minor releases
   New visualisations, app features, ML utilities, or live-source connectors.

Major releases
   Breaking API changes.
