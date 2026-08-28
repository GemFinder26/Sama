"""
reading.py
Turns the computed birth chart into a readable "who you are" narrative.

The interpretation is composed from building blocks (planet role, sign flavor,
house arena) so every placement is covered without pretending each line is a
bespoke revelation. The numbers come from astro.py. This file only phrases them.
"""

import astro

SIGN_FLAVOR = {
    "Aries": "bold, direct, quick to start",
    "Taurus": "steady, sensual, patient",
    "Gemini": "curious, verbal, mentally quick",
    "Cancer": "caring, protective, tidal in mood",
    "Leo": "warm, expressive, proud",
    "Virgo": "precise, useful, discerning",
    "Libra": "relational, fair-minded, drawn to beauty",
    "Scorpio": "deep, intense, private",
    "Sagittarius": "expansive, truth-seeking, restless",
    "Capricorn": "disciplined, ambitious, built for the long game",
    "Aquarius": "original, independent, future-facing",
    "Pisces": "dreamy, permeable, compassionate",
}

ELEMENT = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
}

MODALITY = {
    "Aries": "Cardinal", "Cancer": "Cardinal", "Libra": "Cardinal",
    "Capricorn": "Cardinal", "Taurus": "Fixed", "Leo": "Fixed",
    "Scorpio": "Fixed", "Aquarius": "Fixed", "Gemini": "Mutable",
    "Virgo": "Mutable", "Sagittarius": "Mutable", "Pisces": "Mutable",
}

PLANET_ROLE = {
    "Sun": "your core identity and vitality",
    "Moon": "your emotional needs and instinct",
    "Mercury": "your mind and how you communicate",
    "Venus": "how you love and what you value",
    "Mars": "your drive and how you assert yourself",
    "Jupiter": "how you grow and what you believe",
    "Saturn": "your discipline and where you meet limits",
    "Uranus": "your individuality and urge to break form",
    "Neptune": "your imagination and spiritual pull",
    "Pluto": "your relationship to power and transformation",
}

HOUSE_ARENA = {
    1: "yourself, your body, your presence",
    2: "money, values, and self-worth",
    3: "communication, learning, and your daily surroundings",
    4: "home, roots, and family",
    5: "creativity, romance, and play",
    6: "work, health, and daily routine",
    7: "partnership and one-to-one relationships",
    8: "depth, intimacy, and shared resources",
    9: "meaning, travel, and the big picture",
    10: "career, reputation, and public life",
    11: "community, networks, and the future",
    12: "solitude, rest, and the unseen",
}

ELEMENT_MEANING = {
    "Fire": "You lead with warmth, action, and instinct. You need movement "
            "and a cause to burn toward.",
    "Earth": "You lead with the practical and the tangible. You trust what "
             "you can build, hold, and rely on.",
    "Air": "You lead with the mind. You need ideas, conversation, and room "
           "to think out loud.",
    "Water": "You lead with feeling. You read the emotional current in a "
             "room before anyone says a word.",
}

MODALITY_MEANING = {
    "Cardinal": "You start things. You are most alive at the beginning of "
                "a push.",
    "Fixed": "You sustain things. Your gift is depth and staying power.",
    "Mutable": "You adapt things. You move and bend as conditions change.",
}

ASPECT_TONE = {
    "conjunction": "fused and intensified",
    "sextile": "working together with ease",
    "square": "in productive tension",
    "trine": "flowing together smoothly",
    "opposition": "pulling against each other, seeking balance",
}

NAKSHATRA_KEY = {
    "Ashwini": "swift healing and fresh starts",
    "Bharani": "intensity, endurance, and creative force",
    "Krittika": "a sharp, purifying edge that cuts through",
    "Rohini": "magnetism, beauty, and the power to grow things",
    "Mrigashira": "gentle, curious seeking",
    "Ardra": "storm and breakthrough, renewal after upheaval",
    "Punarvasu": "return, renewal, and safe harbor",
    "Pushya": "nourishment and care, one of the most auspicious",
    "Ashlesha": "penetrating, hypnotic depth",
    "Magha": "ancestry, authority, and the seat of power",
    "Purva Phalguni": "pleasure, romance, rest, and creativity",
    "Uttara Phalguni": "reliable friendship and generous service",
    "Hasta": "skilled hands, craft, and cleverness",
    "Chitra": "brilliance, design, and striking beauty",
    "Swati": "independence and self-made movement",
    "Vishakha": "focused, goal-driven ambition",
    "Anuradha": "devotion and discipline in relationship",
    "Jyeshtha": "seniority, protection, and hard-won power",
    "Mula": "getting to the root, tearing down to truth",
    "Purva Ashadha": "conviction and early, unstoppable victory",
    "Uttara Ashadha": "lasting victory won with integrity",
    "Shravana": "listening, learning, and connection",
    "Dhanishta": "rhythm, wealth, and music",
    "Shatabhisha": "healing, mystery, and the hidden",
    "Purva Bhadrapada": "spiritual fire and intensity",
    "Uttara Bhadrapada": "calm, deep, wise waters",
    "Revati": "completion, safe passage, and care for the whole",
}


def headline(natal):
    sun = natal["tropical"]["Sun"]["sign"]
    moon = natal["tropical"]["Moon"]["sign"]
    asc_sign = astro.SIGNS[int(natal["asc_tropical"] // 30)]
    return {
        "sun": sun, "moon": moon, "rising": asc_sign,
        "line": (f"{sun} Sun, {moon} Moon, {asc_sign} rising. "
                 f"You meet the world as someone {SIGN_FLAVOR[asc_sign]}, "
                 f"you are at core {SIGN_FLAVOR[sun]}, and underneath you "
                 f"need what is {SIGN_FLAVOR[moon]}."),
    }


def element_modality(natal):
    personal = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    el, mo = {}, {}
    for p in personal:
        s = natal["tropical"][p]["sign"]
        el[ELEMENT[s]] = el.get(ELEMENT[s], 0) + 1
        mo[MODALITY[s]] = mo.get(MODALITY[s], 0) + 1
    dom_el = max(el, key=el.get)
    dom_mo = max(mo, key=mo.get)
    return {
        "elements": el, "modalities": mo,
        "dominant_element": dom_el, "dominant_modality": dom_mo,
        "text": f"{ELEMENT_MEANING[dom_el]} {MODALITY_MEANING[dom_mo]}",
    }


def placements(natal):
    lines = []
    order = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter",
             "Saturn", "Uranus", "Neptune", "Pluto"]
    for p in order:
        pos = natal["tropical"][p]
        house = astro.house_of(pos["lon"], natal["cusps"])
        retro = " (retrograde, turned inward)" if pos["retro"] else ""
        lines.append(
            f"{p} in {pos['sign']}, house {house}{retro}: "
            f"{PLANET_ROLE[p]} shows up as {SIGN_FLAVOR[pos['sign']]}, "
            f"and plays out in {HOUSE_ARENA[house]}."
        )
    return lines


def top_aspects(natal, orb=5.0, limit=5):
    bodies = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter",
              "Saturn", "Uranus", "Neptune", "Pluto"]
    out = []
    for i, a in enumerate(bodies):
        for b in bodies[i + 1:]:
            hit = astro.aspect(natal["tropical"][a]["lon"],
                               natal["tropical"][b]["lon"], orb)
            if hit:
                out.append({
                    "a": a, "b": b, "aspect": hit["aspect"], "orb": hit["orb"],
                    "text": (f"{a} and {b} are {ASPECT_TONE[hit['aspect']]} "
                             f"({hit['aspect']}, orb {hit['orb']} deg): "
                             f"{PLANET_ROLE[a]} meets {PLANET_ROLE[b]}."),
                })
    out.sort(key=lambda x: x["orb"])
    return out[:limit]


def vedic_summary(natal):
    asc = natal["asc_sidereal_sign"]
    nak = natal["moon_nakshatra"]
    key = NAKSHATRA_KEY.get(nak["name"], "")
    return {
        "ascendant": asc,
        "nakshatra": nak["name"],
        "nakshatra_lord": nak["lord"],
        "text": (f"In the Vedic (sidereal) system your rising sign is {asc}, "
                 f"and your Moon sits in {nak['name']} nakshatra, ruled by "
                 f"{nak['lord']}. That lunar mansion carries {key}. In Vedic "
                 f"practice your Moon nakshatra sets your whole life-timeline "
                 f"clock, the Vimshottari Dasha."),
    }


def full_reading(natal):
    return {
        "headline": headline(natal),
        "balance": element_modality(natal),
        "placements": placements(natal),
        "aspects": top_aspects(natal),
        "vedic": vedic_summary(natal),
    }
