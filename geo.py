"""
geo.py
Turn a typed city name into coordinates and a timezone.

Uses geonamescache, a bundled world-cities database, so there is no API key
and no network call. Matching is accent-insensitive and also checks each
city's alternate names, then ranks by population so the best-known match
comes first.
"""

import unicodedata

import geonamescache

_gc = geonamescache.GeonamesCache()
_cities = None
_countries = None


def _load():
    global _cities, _countries
    if _cities is None:
        _cities = list(_gc.get_cities().values())
        _countries = _gc.get_countries()


def _strip(text):
    """Lowercase and drop accents so Merida matches Merida."""
    n = unicodedata.normalize("NFKD", text)
    return "".join(c for c in n if not unicodedata.combining(c)).lower().strip()


def _country_name(code):
    c = _countries.get(code)
    return c["name"] if c else code


def _pop(c):
    try:
        return int(c.get("population") or 0)
    except (TypeError, ValueError):
        return 0


def search_cities(query, limit=8):
    """Return up to `limit` matching cities, best match first."""
    _load()
    q = _strip(query)
    if not q:
        return []

    exact, starts, contains = [], [], []
    for c in _cities:
        name = _strip(c["name"])
        alts = [_strip(a) for a in c.get("alternatenames", [])]
        if name == q or q in alts:
            exact.append(c)
        elif name.startswith(q):
            starts.append(c)
        elif q in name:
            contains.append(c)

    for group in (exact, starts, contains):
        group.sort(key=_pop, reverse=True)

    ranked = (exact + starts + contains)[:limit]
    out = []
    for c in ranked:
        lat = float(c["latitude"])
        lon = float(c["longitude"])
        country = _country_name(c["countrycode"])
        out.append({
            "name": c["name"],
            "country": country,
            "lat": lat,
            "lon": lon,
            "tz": c.get("timezone") or "UTC",
            "population": _pop(c),
            "label": f"{c['name']}, {country}  ({lat:.1f}, {lon:.1f})",
        })
    return out
