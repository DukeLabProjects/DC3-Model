Quickstart
==========

These examples use the deterministic DC3 rules described by Duke et al.
(2026).

Single Record Classification
----------------------------

Use :func:`dc3.classify_dc3` when you already have the three subjective
inputs required by the deterministic DC3 model.

.. code-block:: python

   from dc3 import classify_dc3, encode_dc3, decode_dc3

   label = classify_dc3(
       thermal_sensation=0,
       thermal_preference="no_change",
       thermal_acceptability=1,
   )

   code = encode_dc3(label)
   decoded = decode_dc3(code)

   print(label)       # D
   print(code)        # 11
   print(decoded)

Batch Processing
----------------

Use :func:`dc3.process_dataframe` when users upload a table with their own
column names.

.. code-block:: python

   import pandas as pd
   from dc3 import process_dataframe

   df = pd.DataFrame(
       {
           "TS": [0, "slightly warm"],
           "Pref": ["no change", "prefer cooler"],
           "Accept": ["acceptable", 1],
       }
   )

   processed = process_dataframe(
       df,
       columns={
           "thermal_sensation": "TS",
           "thermal_preference": "Pref",
           "thermal_acceptability": "Accept",
       },
   )

   print(processed[["dc3_label", "dc3_code", "dc3_valid"]])

Invalid Rows
------------

Invalid rows are retained by default. Each invalid row receives:

``dc3_valid = False``
   The row could not be classified.

``dc3_error``
   Human-readable reason for the failure.

Set ``keep_invalid=False`` to drop invalid rows from the returned dataframe.
