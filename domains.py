"""
domains.py
Life-area guidance layer for the dual-chart forecaster.

This is electional astrology: is a given day favorable for a given activity.
It blends personalized Vedic timing (Tarabala and Chandra Bala, both counted
from your birth chart), the muhurta layer (does the day's nakshatra suit this
kind of activity), and Western significator transits (are this domain's
planets being helped or stressed today).

Every factor is returned as a readable line so the verdict can be checked.
Nothing here is a prediction, and nothing here is medical or financial advice.
"""

import astro

# ---------------------------------------------------------------------------
# Personalized Vedic timing
# ---------------------------------------------------------------------------

TARA = ["Janma", "Sampat", "Vipat", "Kshema", "Pratyari",
        "Sadhaka", "Vadha", "Mitra", "Ati Mitra"]

# Score and plain meaning for each of the nine taras.
TARA_INFO = {
    "Janma":    (0,  "your own nakshatra, a mixed and self-referential day"),
    "Sampat":   (2,  "wealth and ease, one of the best days"),
    "Vipat":    (-2, "friction and risk, hold off on new starts"),
    "Kshema":   (2,  "well-being and safety, favorable"),
    "Pratyari": (-1, "obstacles, expect resistance"),
    "Sadhaka":  (2,  "accomplishment, good for effort that must land"),
    "Vadha":    (-2, "the hardest day, avoid important beginnings"),
    "Mitra":    (1,  "friendly and smooth"),
    "Ati Mitra": (2, "very friendly, strongly supportive"),
}


def tarabala(natal_nak_index, day_nak_index):
    """Count the day's Moon nakshatra from your birth nakshatra."""
    n = (day_nak_index - natal_nak_index) % 27
    name = TARA[n % 9]
    score, meaning = TARA_INFO[name]
    return {"name": name, "score": score, "meaning": meaning}


# Moon-sign position from your natal Moon, the Chandra Bala scheme.
CHANDRA_GOOD = {1, 3, 6, 7, 10, 11}
CHANDRA_MIXED = {2, 5, 9}
CHANDRA_HARD = {4, 8, 12}


def chandra_bala(natal_moon_sign_index, day_moon_sign_index):
    pos = (day_moon_sign_index - natal_moon_sign_index) % 12 + 1
    if pos in CHANDRA_GOOD:
        return {"position": pos, "score": 1,
                "meaning": f"day Moon is {pos} signs from your natal Moon, "
                           "a supportive position"}
    if pos in CHANDRA_MIXED:
        return {"position": pos, "score": 0,
                "meaning": f"day Moon is {pos} signs from your natal Moon, "
                           "a mixed position"}
    return {"position": pos, "score": -1,
            "meaning": f"day Moon is {pos} signs from your natal Moon, "
                       "a draining position"}


# ---------------------------------------------------------------------------
# Muhurta layer: nakshatra activity nature
# ---------------------------------------------------------------------------
# Classic groupings. Each nakshatra suits certain kinds of action.

ACTIVITY_OF_NAK = [
    "Kshipra", "Ugra", "Mishra", "Dhruva", "Mridu", "Tikshna", "Chara",
    "Kshipra", "Tikshna", "Ugra", "Ugra", "Dhruva", "Kshipra", "Mridu",
    "Chara", "Mishra", "Mridu", "Tikshna", "Tikshna", "Ugra", "Dhruva",
    "Chara", "Chara", "Chara", "Ugra", "Dhruva", "Mridu",
]

ACTIVITY_MEANING = {
    "Dhruva": "fixed, good for lasting things (property, commitments, roots)",
    "Chara": "movable, good for travel, vehicles, change",
    "Kshipra": "swift, good for trade, learning, quick tasks, medicine",
    "Mridu": "soft, good for love, art, friendship, gentle healing",
    "Tikshna": "sharp, good for discipline and surgery, harsh for soft aims",
    "Ugra": "fierce, good for bold or forceful acts, harsh for soft aims",
    "Mishra": "mixed, ordinary tasks",
}

VARA_RULER = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
# index matches Python weekday(): Monday=0 ... Sunday=6


# ---------------------------------------------------------------------------
# Domain definitions
# ---------------------------------------------------------------------------

DOMAINS = {
    "Finances and wealth": {
        "houses": [2, 11, 8],
        "significators": ["Jupiter", "Venus", "Mercury"],
        "good_activity": ["Kshipra", "Dhruva", "Chara"],
        "avoid_activity": ["Tikshna", "Ugra"],
        "vara_boost": ["Mercury", "Jupiter"],
        "mercury_rx_sensitive": False,
        "note": "Reflective timing only, not financial advice. "
                "Run your own numbers and talk to a professional.",
    },
    "Deals and contracts": {
        "houses": [3, 7, 2],
        "significators": ["Mercury", "Jupiter"],
        "good_activity": ["Kshipra", "Chara", "Dhruva"],
        "avoid_activity": ["Tikshna", "Ugra"],
        "vara_boost": ["Mercury"],
        "mercury_rx_sensitive": True,
        "note": "A timing lens, not a verdict on the deal. "
                "Read the contract and get advice before you sign.",
    },
    "Love and relationships": {
        "houses": [5, 7, 11],
        "significators": ["Venus", "Moon", "Mars"],
        "good_activity": ["Mridu", "Dhruva"],
        "avoid_activity": ["Tikshna", "Ugra"],
        "vara_boost": ["Venus", "Moon"],
        "mercury_rx_sensitive": False,
        "note": "A mirror for the heart, not a rule for it.",
    },
    "Health and vitality": {
        "houses": [1, 6, 8],
        "significators": ["Sun", "Moon", "Mars"],
        "good_activity": ["Kshipra", "Mridu"],
        "avoid_activity": ["Ugra"],
        "vara_boost": ["Sun"],
        "mercury_rx_sensitive": False,
        "note": "Reflective timing only, not medical advice. "
                "For real symptoms or decisions, see a clinician.",
    },
    "Family and home": {
        "houses": [4, 3, 9],
        "significators": ["Moon", "Jupiter", "Sun"],
        "good_activity": ["Dhruva", "Mridu"],
        "avoid_activity": ["Tikshna", "Ugra"],
        "vara_boost": ["Moon", "Jupiter"],
        "mercury_rx_sensitive": False,
        "note": "A timing lens for home and kin.",
    },
    "Career and public life": {
        "houses": [10, 6, 2],
        "significators": ["Sun", "Saturn", "Mars", "Mercury"],
        "good_activity": ["Dhruva", "Kshipra"],
        "avoid_activity": ["Tikshna"],
        "vara_boost": ["Sun", "Saturn"],
        "mercury_rx_sensitive": False,
        "note": "A timing lens for work and reputation.",
    },
    "Travel and moving": {
        "houses": [3, 9, 12],
        "significators": ["Mercury", "Moon"],
        "good_activity": ["Chara"],
        "avoid_activity": ["Dhruva"],
        "vara_boost": ["Mercury", "Moon"],
        "mercury_rx_sensitive": False,
        "note": "A timing lens for journeys and relocation.",
    },
}


# ---------------------------------------------------------------------------
# Significator transits (Western layer)
# ---------------------------------------------------------------------------

BENEFICS = ["Jupiter", "Venus"]
MALEFICS = ["Saturn", "Mars"]
SOFT = ["trine", "sextile", "conjunction"]
HARD = ["square", "opposition"]


def significator_transits(natal, transit_trop, sig_planets, orb=5.0):
    """Benefic help and malefic stress on this domain's natal planets."""
    positives, negatives = [], []
    for b in BENEFICS:
        for s in sig_planets:
            hit = astro.aspect(transit_trop[b]["lon"],
                               natal["tropical"][s]["lon"], orb)
            if hit and hit["aspect"] in SOFT:
                positives.append(
                    f"transiting {b} {hit['aspect']} your natal {s} "
                    f"(orb {hit['orb']})")
    for m in MALEFICS:
        for s in sig_planets:
            hit = astro.aspect(transit_trop[m]["lon"],
                               natal["tropical"][s]["lon"], orb)
            if hit and hit["aspect"] in HARD:
                negatives.append(
                    f"transiting {m} {hit['aspect']} your natal {s} "
                    f"(orb {hit['orb']})")
    return positives, negatives


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def verdict_from_score(score):
    if score >= 4:
        return "Strongly favorable"
    if score >= 2:
        return "Favorable"
    if score >= -1:
        return "Mixed, proceed with care"
    if score >= -3:
        return "Better to wait"
    return "Wait for a clearer day"


def read_domain(domain_name, natal, transit_trop, jd, weekday_index, cusps):
    """Full guidance read for one domain on one day."""
    d = DOMAINS[domain_name]

    # Personalized Vedic timing.
    sid = astro.positions(jd, sidereal=True)
    day_moon_lon = sid["Moon"]["lon"]
    day_nak = astro.nakshatra(day_moon_lon)
    day_moon_sign = int(day_moon_lon // 30)

    natal_nak_idx = natal["moon_nakshatra"]["index"]
    natal_moon_sign = int(natal["sidereal"]["Moon"]["lon"] // 30)

    tara = tarabala(natal_nak_idx, day_nak["index"])
    cbala = chandra_bala(natal_moon_sign, day_moon_sign)

    activity = ACTIVITY_OF_NAK[day_nak["index"]]
    vara_ruler = VARA_RULER[weekday_index]

    # Western significator transits.
    positives, negatives = significator_transits(
        natal, transit_trop, d["significators"])

    # Transiting Moon spotlight on a domain house.
    moon_house = astro.house_of(transit_trop["Moon"]["lon"], cusps)
    moon_spotlight = moon_house in d["houses"]

    # Mercury retrograde caution where it matters.
    merc_rx = transit_trop["Mercury"]["retro"]

    # Assemble score and reasons.
    score = 0
    reasons = []

    score += tara["score"]
    reasons.append(f"Tarabala: {tara['name']}, {tara['meaning']} "
                   f"({tara['score']:+d})")

    score += cbala["score"]
    reasons.append(f"Chandra Bala: {cbala['meaning']} ({cbala['score']:+d})")

    if activity in d["good_activity"]:
        score += 2
        reasons.append(f"Nakshatra nature: {activity}, "
                       f"{ACTIVITY_MEANING[activity]} (+2)")
    elif activity in d["avoid_activity"]:
        score -= 2
        reasons.append(f"Nakshatra nature: {activity}, "
                       f"{ACTIVITY_MEANING[activity]} (-2)")
    else:
        reasons.append(f"Nakshatra nature: {activity}, "
                       f"{ACTIVITY_MEANING[activity]} (neutral)")

    if vara_ruler in d["vara_boost"]:
        score += 1
        reasons.append(f"Weekday ruler {vara_ruler} supports this area (+1)")

    for p in positives:
        score += 1
        reasons.append(f"Support: {p} (+1)")
    for n in negatives:
        score -= 1
        reasons.append(f"Stress: {n} (-1)")

    if moon_spotlight:
        score += 1
        reasons.append(f"Timing: transiting Moon is in your house {moon_house}, "
                       "spotlighting this area (+1)")

    if d["mercury_rx_sensitive"] and merc_rx:
        score -= 2
        reasons.append("Caution: Mercury is retrograde, weak for signing "
                       "and finalizing (-2)")

    return {
        "domain": domain_name,
        "score": score,
        "verdict": verdict_from_score(score),
        "reasons": reasons,
        "note": d["note"],
        "day_nakshatra": day_nak["name"],
        "activity": activity,
    }


def scan_all(natal, transit_trop, jd, weekday_index, cusps):
    """One-line verdict for every domain, for a daily overview."""
    out = []
    for name in DOMAINS:
        r = read_domain(name, natal, transit_trop, jd, weekday_index, cusps)
        out.append({"domain": name, "verdict": r["verdict"],
                    "score": r["score"]})
    out.sort(key=lambda x: x["score"], reverse=True)
    return out
