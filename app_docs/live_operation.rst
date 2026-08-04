Live Operation
==============

Live operation uses snapshot polling. This gives a practical path from
research datasets to operational occupant-feedback pipelines.

Snapshot Cycle
--------------

On each refresh, the app:

1. reads the latest snapshot,
2. applies the existing column mapping,
3. processes the snapshot through the installed ``dc3-model`` package,
4. updates DC3 class, observed comfort, and Z-class summaries.

Supported Sources
-----------------

``Demo stream``
   Reveals the currently loaded dataset in batches. Use this for demonstration
   and UI testing.

``CSV/XLSX file path``
   Polls a local file that can be updated by another process.

``SQL database``
   Uses a SQLAlchemy connection URL and polling query. This is the preferred
   production pattern for future integration with kiosks, survey tools, BMS
   gateways, or IoT services.

HVAC Control Pathway
--------------------

The live summaries can later feed an HVAC-energy optimisation layer by
providing current comfort ratio, dominant directional preference, Z-class
rate, and local environmental context.
