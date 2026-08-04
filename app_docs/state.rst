Saved State
===========

The app includes source-change awareness so users can preserve analysis
settings before moving between datasets.

What Is Saved
-------------

Saved state stores lightweight user-interface choices, including:

- selected source,
- column mappings,
- active filters,
- palette settings,
- selected plot controls.

The app does not store full uploaded datasets in saved state files.

Where State Is Stored
---------------------

State files are stored on the user's local device under:

.. code-block:: text

   ~/.dc3_model/states

Source Switching
----------------

When the user switches from one source to another, the app asks whether to
save or discard the current analysis state. If the state is discarded, the
new source opens with its default controls. If a matching saved state exists
when a source is selected again, the sidebar offers restore and delete
controls.
