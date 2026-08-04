Versioning And Releases
=======================

DC3 Model is configured so documentation can later support versioned
publishing on GitHub and Read the Docs. Versioned releases should preserve
clear traceability to the primary Duke et al. (2026) model reference.

Recommended Version Flow
------------------------

1. Update the package version in ``pyproject.toml`` and ``src/dc3/__init__.py``.
2. Update ``docs/conf.py`` release metadata if needed.
3. Add release notes to ``docs/changelog.rst``.
4. Run tests and build documentation locally.
5. Tag the release in Git.
6. Publish package and documentation through CI.

Version Switcher
----------------

The PyData Sphinx Theme version switcher is prepared in ``docs/conf.py`` but
disabled until a hosted JSON file is available. When the project is on GitHub
or Read the Docs, set:

.. code-block:: bash

   DC3_DOCS_VERSION_JSON=https://example.com/path/to/versions.json

The JSON file should describe the available documentation versions. The active
version is selected from ``READTHEDOCS_VERSION`` when available, otherwise the
package release value is used.

Edit On GitHub
--------------

The PyData "Edit this page" button can be enabled once the repository exists:

.. code-block:: bash

   DC3_GITHUB_USER=your-org-or-user
   DC3_GITHUB_REPO=DC3-Model
   DC3_GITHUB_VERSION=main
