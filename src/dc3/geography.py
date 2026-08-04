"""Offline geographic helpers for DC3 app maps.

The helpers intentionally use a small curated lookup instead of paid map
tiles, API keys, or online geocoding. Coordinates are approximate city-centre
points suitable for aggregate visual comparison, not building-level location
analysis.
"""

from __future__ import annotations

import math
import re
import unicodedata
from typing import Mapping

import pandas as pd

COUNTRY_ISO3 = {
    "Australia": "AUS",
    "Belgium": "BEL",
    "Brazil": "BRA",
    "Canada": "CAN",
    "China": "CHN",
    "Denmark": "DNK",
    "France": "FRA",
    "Germany": "DEU",
    "Greece": "GRC",
    "India": "IND",
    "Indonesia": "IDN",
    "Iran": "IRN",
    "Italy": "ITA",
    "Japan": "JPN",
    "Malaysia": "MYS",
    "Mexico": "MEX",
    "Nigeria": "NGA",
    "Pakistan": "PAK",
    "Philippines": "PHL",
    "Portugal": "PRT",
    "Singapore": "SGP",
    "Slovakia": "SVK",
    "South Korea": "KOR",
    "Sweden": "SWE",
    "Thailand": "THA",
    "Tunisia": "TUN",
    "UK": "GBR",
    "United Kingdom": "GBR",
    "USA": "USA",
    "United States": "USA",
    "United States of America": "USA",
}

ASHRAE_CITY_COORDINATES = {
    ("Australia", "Brisbane"): (-27.4698, 153.0251),
    ("Australia", "Darwin"): (-12.4634, 130.8456),
    ("Australia", "Goulburn"): (-34.7516, 149.7209),
    ("Australia", "Kalgoorlie"): (-30.7490, 121.4660),
    ("Australia", "Melbourne"): (-37.8136, 144.9631),
    ("Australia", "Sydney"): (-33.8688, 151.2093),
    ("Australia", "Townsville"): (-19.2590, 146.8169),
    ("Australia", "Wollongong"): (-34.4278, 150.8931),
    ("Belgium", "Liege"): (50.6326, 5.5797),
    ("Brazil", "Brasilia"): (-15.7939, -47.8828),
    ("Brazil", "Bras�_lia"): (-15.7939, -47.8828),
    ("Brazil", "Florianopolis"): (-27.5949, -48.5482),
    ("Brazil", "Maceio"): (-9.6498, -35.7089),
    ("Brazil", "Recife"): (-8.0476, -34.8770),
    ("Canada", "Montreal"): (45.5017, -73.5673),
    ("Canada", "Ottawa"): (45.4215, -75.6972),
    ("China", "Beijing"): (39.9042, 116.4074),
    ("China", "Changsha"): (28.2282, 112.9388),
    ("China", "Chaozhou"): (23.6567, 116.6220),
    ("China", "Guangzhou"): (23.1291, 113.2644),
    ("China", "Harbin"): (45.8038, 126.5350),
    ("China", "Nanyang"): (32.9908, 112.5283),
    ("China", "Shanghai"): (31.2304, 121.4737),
    ("China", "Yueyang"): (29.3571, 113.1287),
    ("Denmark", "Elsinore"): (56.0361, 12.6136),
    ("France", "Lyon"): (45.7640, 4.8357),
    ("Germany", "Karlsruhe"): (49.0069, 8.4037),
    ("Germany", "Stuttgart"): (48.7758, 9.1829),
    ("Greece", "Athens"): (37.9838, 23.7275),
    ("India", "Ahmedabad"): (23.0225, 72.5714),
    ("India", "Bangalore"): (12.9716, 77.5946),
    ("India", "Chennai"): (13.0827, 80.2707),
    ("India", "Delhi"): (28.6139, 77.2090),
    ("India", "Hyderabad"): (17.3850, 78.4867),
    ("India", "Imphal"): (24.8170, 93.9368),
    ("India", "Jaipur"): (26.9124, 75.7873),
    ("India", "Shilong"): (25.5788, 91.8933),
    ("India", "Shillong"): (25.5788, 91.8933),
    ("India", "Shimla"): (31.1048, 77.1734),
    ("India", "Tezpur"): (26.6528, 92.7926),
    ("Indonesia", "Jakarta"): (-6.2088, 106.8456),
    ("Iran", "Bandar Abbas"): (27.1832, 56.2666),
    ("Iran", "Ilam"): (33.6374, 46.4227),
    ("Italy", "Imola"): (44.3599, 11.7124),
    ("Italy", "Lodi"): (45.3097, 9.5037),
    ("Italy", "Varese"): (45.8206, 8.8251),
    ("Japan", "Tokyo"): (35.6762, 139.6503),
    ("Japan", "Tsukuba"): (36.0835, 140.0764),
    ("Malaysia", "Bedong"): (5.7274, 100.5082),
    ("Malaysia", "Beverly Hills"): (5.9220, 116.1010),
    ("Malaysia", "Kinarut"): (5.8231, 115.9980),
    ("Malaysia", "Kota Kinabalu"): (5.9804, 116.0735),
    ("Malaysia", "Kuala Lumpur"): (3.1390, 101.6869),
    ("Malaysia", "Kuching"): (1.5533, 110.3592),
    ("Malaysia", "Putra Jaya"): (2.9264, 101.6964),
    ("Malaysia", "Putrajaya"): (2.9264, 101.6964),
    ("Mexico", "Colima"): (19.2452, -103.7241),
    ("Mexico", "Culiacan"): (24.8091, -107.3940),
    ("Mexico", "Hermosillo"): (29.0729, -110.9559),
    ("Mexico", "Mexicali"): (32.6245, -115.4523),
    ("Mexico", "Merida"): (20.9674, -89.5926),
    ("Mexico", "M̩rida"): (20.9674, -89.5926),
    ("Nigeria", "Bauchi"): (10.3158, 9.8442),
    ("Pakistan", "Karachi"): (24.8607, 67.0011),
    ("Pakistan", "Multan"): (30.1575, 71.5249),
    ("Pakistan", "Peshawar"): (34.0151, 71.5249),
    ("Pakistan", "Quetta"): (30.1798, 66.9750),
    ("Pakistan", "Saidu Sharif"): (34.7463, 72.3578),
    ("Philippines", "Makati"): (14.5547, 121.0244),
    ("Portugal", "Lisbon"): (38.7223, -9.1393),
    ("Portugal", "Porto"): (41.1579, -8.6291),
    ("Singapore", "Singapore"): (1.3521, 103.8198),
    ("Slovakia", "Bratislava"): (48.1486, 17.1077),
    ("South Korea", "Seoul"): (37.5665, 126.9780),
    ("Sweden", "Gothenburg"): (57.7089, 11.9746),
    ("Sweden", "Halmstad"): (56.6745, 12.8578),
    ("Sweden", "Malmo"): (55.6050, 13.0038),
    ("Thailand", "Bangkok"): (13.7563, 100.5018),
    ("Tunisia", "El Kef"): (36.1675, 8.7049),
    ("Tunisia", "Gabes"): (33.8815, 10.0982),
    ("Tunisia", "Gafsa"): (34.4250, 8.7842),
    ("Tunisia", "Sfax"): (34.7406, 10.7603),
    ("Tunisia", "Tunis"): (36.8065, 10.1815),
    ("UK", "Cardiff"): (51.4816, -3.1791),
    ("UK", "Chester"): (53.1934, -2.8931),
    ("UK", "Hampshire"): (51.0577, -1.3081),
    ("UK", "Liverpool"): (53.4084, -2.9916),
    ("UK", "London"): (51.5072, -0.1276),
    ("UK", "Midland"): (52.4862, -1.8904),
    ("UK", "Oxford"): (51.7520, -1.2577),
    ("UK", "St Helens"): (53.4539, -2.7369),
    ("USA", "Alameda"): (37.7652, -122.2416),
    ("USA", "Auburn"): (32.6099, -85.4808),
    ("USA", "Berkeley"): (37.8715, -122.2730),
    ("USA", "Grand Rapids"): (42.9634, -85.6681),
    ("USA", "Honolulu"): (21.3099, -157.8581),
    ("USA", "Palo Alto"): (37.4419, -122.1430),
    ("USA", "Philadelphia"): (39.9526, -75.1652),
    ("USA", "San Francisco"): (37.7749, -122.4194),
    ("USA", "San Ramon"): (37.7799, -121.9780),
    ("USA", "Texas"): (31.9686, -99.9018),
    ("USA", "Walnut Creek"): (37.9101, -122.0652),
}


def country_to_iso3(country: object) -> str | None:
    """Return an ISO-3 country code for a known country label.

    Parameters
    ----------
    country:
        Country name or common country alias, for example ``"India"``,
        ``"USA"``, or ``"United Kingdom"``.

    Returns
    -------
    str or None
        ISO-3 code when the country is known; otherwise ``None``.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       from dc3 import country_to_iso3

       print(country_to_iso3("India"))
       print(country_to_iso3("United Kingdom"))
       print(country_to_iso3("Unknownland"))

    Expected output:

    .. code-block:: text

       IND
       GBR
       None
    """

    key = _normalise_key(country)
    for name, code in COUNTRY_ISO3.items():
        if _normalise_key(name) == key:
            return code
    return None


def city_coordinates(country: object | None, city: object) -> tuple[float, float] | None:
    """Return approximate coordinates for a known country-city pair.

    Parameters
    ----------
    country:
        Country name. Use ``None`` to search by city only.
    city:
        City name.

    Returns
    -------
    tuple[float, float] or None
        Approximate ``(latitude, longitude)`` pair for known cities.

    .. note::

       Coordinates are city-centre approximations for aggregate maps. They are
       not intended for building-level geocoding.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       from dc3 import city_coordinates

       lat, lon = city_coordinates("India", "Delhi")
       print(round(lat, 3))
       print(round(lon, 3))

    Expected output:

    .. code-block:: text

       28.614
       77.209
    """

    city_key = _normalise_key(city)
    country_key = _normalise_key(country)
    if not city_key:
        return None
    for (known_country, known_city), coordinates in ASHRAE_CITY_COORDINATES.items():
        if _normalise_key(known_city) != city_key:
            continue
        if not country_key or _normalise_key(known_country) == country_key:
            return coordinates
    return None


def enrich_geography(
    df: pd.DataFrame,
    columns: Mapping[str, str],
    *,
    country_code_column: str = "dc3_country_code",
    latitude_column: str = "dc3_latitude",
    longitude_column: str = "dc3_longitude",
) -> tuple[pd.DataFrame, dict[str, str]]:
    """Add offline ISO-3 and coordinate columns when country/city data is known.

    Existing user-mapped country code, latitude, or longitude columns are left
    untouched. Derived columns are added only when enough known geography is
    available.

    Parameters
    ----------
    df:
        Source dataframe.
    columns:
        Existing canonical field mapping. Include ``country`` and optionally
        ``city`` for enrichment.
    country_code_column:
        Default is ``"dc3_country_code"``. Name for derived ISO-3 values.
    latitude_column:
        Default is ``"dc3_latitude"``. Name for derived latitude values.
    longitude_column:
        Default is ``"dc3_longitude"``. Name for derived longitude values.

    Returns
    -------
    tuple[pandas.DataFrame, dict[str, str]]
        Enriched dataframe and updated canonical mapping.

    Examples
    --------
    .. code-block:: python

       # python -m pip install dc3model_v1
       import pandas as pd
       from dc3 import enrich_geography

       df = pd.DataFrame(
           {
               "Country": ["India", "USA"],
               "City": ["Delhi", "San Francisco"],
           }
       )
       enriched, mapping = enrich_geography(
           df,
           columns={"country": "Country", "city": "City"},
       )

       print(mapping["country_code"])
       print(round(enriched.loc[0, "dc3_latitude"], 3))
       print(enriched.loc[1, "dc3_country_code"])

    Expected output:

    .. code-block:: text

       dc3_country_code
       28.614
       USA
    """

    enriched = df.copy()
    mapping = dict(columns)
    country_column = mapping.get("country")
    city_column = mapping.get("city")

    if "country_code" not in mapping and country_column in enriched.columns:
        iso_values = enriched[country_column].map(country_to_iso3)
        if iso_values.notna().any():
            enriched[country_code_column] = iso_values
            mapping["country_code"] = country_code_column

    if (
        "latitude" not in mapping
        and "longitude" not in mapping
        and city_column in enriched.columns
    ):
        countries = enriched[country_column] if country_column in enriched.columns else pd.Series([None] * len(enriched), index=enriched.index)
        coordinates = [
            city_coordinates(country, city)
            for country, city in zip(countries, enriched[city_column], strict=False)
        ]
        latitudes = [coordinate[0] if coordinate else math.nan for coordinate in coordinates]
        longitudes = [coordinate[1] if coordinate else math.nan for coordinate in coordinates]
        if any(not math.isnan(value) for value in latitudes):
            enriched[latitude_column] = latitudes
            enriched[longitude_column] = longitudes
            mapping["latitude"] = latitude_column
            mapping["longitude"] = longitude_column

    return enriched, mapping


def _normalise_key(value: object) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    text = str(value).strip().replace("�", "")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(character for character in text if not unicodedata.combining(character))
    return re.sub(r"[^a-z0-9]+", "", text.lower())
