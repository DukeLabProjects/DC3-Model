Maps
====

The maps tab supports geographic comparison without paid services.

Free Map Approach
-----------------

The app uses Plotly geo rendering. It does not require:

- paid map tiles,
- a map subscription,
- API keys,
- automatic online geocoding.

This keeps the app usable for research environments where internet access,
budget, or data governance constraints matter.

Country Maps
------------

Country maps work with a mapped country name or ISO-3 country code. Available
metrics include:

- row count,
- comfortable percentage,
- uncomfortable percentage,
- Z-class percentage,
- mean values for mapped numeric variables.

Map View Selector
-----------------

The maps tab includes a view selector:

``Country and city``
   Shows the country overview, then the city comparison section.

``Country overview``
   Shows only the country-level choropleth and country summary table.

``City comparison``
   Shows only the city-level map, city ranking plot, and city summary table.

City Maps
---------

City maps use latitude and longitude, but users do not need to provide those
columns for the packaged ASHRAE DB II locations. When country and city are
mapped, the app first tries an internal offline lookup of known ASHRAE
country-city pairs and common city labels. The derived coordinates are
approximate city-centre points for aggregate comparison.

Manual latitude and longitude mapping is available only as an advanced
override for uploaded datasets that already contain coordinate columns. The
app does not send city names to an external geocoding service.

The city comparison map automatically fits to the currently visible city
points. If a user filters to one country, the map zooms to the selected
country's cities. A matching city ranking chart is shown below the map so the
same metric can be compared without relying only on spatial position.

In city-comparison mode, selected country polygons are filled transparently
using the country average for the selected metric. City markers are drawn above
that country layer. The map label control can show hover-only labels, city
names, country names, or both; city labels are limited intelligently when many
points are visible to reduce clutter. The Plotly toolbar camera exports the
current zoomed view, including visible labels and the legend.

Filtered Maps
-------------

Maps use the same filtered dataset as the rest of the app. For example, if a
user selects India and a subset of seasons, the country/city map summaries are
computed from those selected records only.
