"""
relocate.py
Location effects, the honest way.

Your natal planets never move. What moves when you travel is the house
framework and the angles. This module recasts your birth chart for a new
place (relocation astrology, also called astrocartography) and reports which
planets land on the angles there, since those are the themes a place amplifies
for you. It also reads the live local sky: which planets are rising or
culminating over you right now.
"""

import astro

PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter",
           "Saturn", "Uranus", "Neptune", "Pluto"]

ANGLE_MEANING = {
    "Ascendant": "your body, your presence, how you show up here",
    "Midheaven": "your career, reputation, and public role here",
    "Descendant": "your relationships and partnerships here",
    "IC": "your home, roots, and inner life here",
}

PLANET_AT_ANGLE = {
    "Sun": "vitality, visibility, and leadership come forward",
    "Moon": "feelings, home longing, and the public run close to the surface",
    "Mercury": "the mind speeds up: talk, business, learning, restlessness",
    "Venus": "love, beauty, money, and ease are amplified",
    "Mars": "energy and drive spike, along with friction and competition",
    "Jupiter": "growth, luck, opportunity, and optimism expand",
    "Saturn": "work, discipline, and weight increase, a place that matures you",
    "Uranus": "change, freedom, and the unexpected get switched on",
    "Neptune": "dreams, inspiration, and also fog and escapism rise",
    "Pluto": "intensity, power, and deep transformation are stirred",
}


def separation(a, b):
    d = abs(a - b) % 360
    return 360 - d if d > 180 else d


def _angles(asc, mc):
    return {
        "Ascendant": asc,
        "Midheaven": mc,
        "Descendant": (asc + 180) % 360,
        "IC": (mc + 180) % 360,
    }


def relocated_chart(natal, lat, lon, orb=6.0):
    """Recast the birth moment at a new place. Planets keep their longitudes,
    the houses and angles are rebuilt for the new location."""
    jd = natal["jd"]  # the birth instant
    cusps, asc, mc = astro.tropical_houses(jd, lat, lon)
    angles = _angles(asc, mc)

    angular = []
    for p in PLANETS:
        plon = natal["tropical"][p]["lon"]
        for aname, alon in angles.items():
            d = separation(plon, alon)
            if d <= orb:
                angular.append({
                    "planet": p, "angle": aname, "orb": round(d, 2),
                    "text": (f"{p} on your {aname}: "
                             f"{PLANET_AT_ANGLE[p]}, touching "
                             f"{ANGLE_MEANING[aname]}."),
                })
    angular.sort(key=lambda x: x["orb"])

    moves = []
    for p in PLANETS:
        natal_house = astro.house_of(natal["tropical"][p]["lon"],
                                     natal["cusps"])
        reloc_house = astro.house_of(natal["tropical"][p]["lon"], cusps)
        if natal_house != reloc_house:
            moves.append({"planet": p, "from": natal_house, "to": reloc_house})

    return {
        "asc_sign": astro.SIGNS[int(asc // 30)],
        "mc_sign": astro.SIGNS[int(mc // 30)],
        "asc": asc, "mc": mc,
        "angular": angular,
        "house_moves": moves,
    }


def local_sky(lat, lon, when_utc, orb=6.0):
    """The live sky over a location: which transiting planets sit near the
    local angles right now."""
    jd = astro.julday(when_utc)
    cusps, asc, mc = astro.tropical_houses(jd, lat, lon)
    trans = astro.positions(jd, sidereal=False)
    angles = _angles(asc, mc)

    near = []
    for p in PLANETS:
        for aname, alon in angles.items():
            d = separation(trans[p]["lon"], alon)
            if d <= orb:
                verb = {"Ascendant": "rising", "Midheaven": "culminating",
                        "Descendant": "setting",
                        "IC": "at the low point"}[aname]
                near.append({
                    "planet": p, "angle": aname, "orb": round(d, 2),
                    "text": (f"{p} is {verb} over you now: "
                             f"{PLANET_AT_ANGLE[p]}."),
                })
    near.sort(key=lambda x: x["orb"])
    return {"asc_sign": astro.SIGNS[int(asc // 30)],
            "mc_sign": astro.SIGNS[int(mc // 30)], "near": near}
