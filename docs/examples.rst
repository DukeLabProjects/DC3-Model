Examples
========

Process A CSV
-------------

.. code-block:: python

   import pandas as pd
   from dc3 import process_dataframe, summarise_dc3

   df = pd.read_csv("comfort_data.csv")

   processed = process_dataframe(
       df,
       columns={
           "thermal_sensation": "Thermal sensation",
           "thermal_preference": "Thermal preference",
           "thermal_acceptability": "Thermal acceptability",
       },
   )

   summary = summarise_dc3(processed)

   processed.to_csv("comfort_data_dc3.csv", index=False)
   summary.to_csv("comfort_data_dc3_summary.csv", index=False)

Use Demo Data
-------------

.. code-block:: python

   from dc3.datasets import load_demo_data
   from dc3 import process_dataframe

   df = load_demo_data()
   processed = process_dataframe(
       df,
       columns={
           "thermal_sensation": "Thermal sensation",
           "thermal_preference": "Thermal preference",
           "thermal_acceptability": "Thermal acceptability",
       },
   )

   print(processed)

