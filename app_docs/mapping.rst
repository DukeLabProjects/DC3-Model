Column Mapping
==============

Mapping tells the app which user columns correspond to fields understood by
the DC3 package.

Required DC3 Fields
-------------------

The following fields are required for DC3 classification:

``thermal_sensation``
   The occupant thermal sensation vote.

``thermal_preference``
   The occupant preference direction, such as cooler, no change, or warmer.

``thermal_acceptability``
   The occupant acceptability response.

Environmental Fields
--------------------

Environmental fields are optional but strongly recommended for scientific
visualisation and comparison:

- air temperature,
- relative humidity,
- air speed,
- globe temperature,
- mean radiant temperature,
- operative temperature,
- outdoor temperature.

Geographic Fields
-----------------

Country and city mappings enable comparison charts and maps. When possible,
the app derives ISO-3 country codes and approximate city-centre coordinates
internally from known ASHRAE DB II locations and common city labels.

ISO-3 country code, latitude, and longitude remain available as advanced
manual mappings for uploaded datasets that already contain those fields. The
app does not send locations to an external geocoding service.

Additional System Fields
------------------------

The app keeps a broader set of known fields internally, including ASHRAE DB II
metadata. These fields are not all shown as mandatory controls. A user can map
additional fields when needed, and mapped fields become available to the
filter system.
