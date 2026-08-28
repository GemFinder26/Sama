"""
astro.py
Core calculation engine for the dual-chart forecaster.

Two systems from one ephemeris (Swiss Ephemeris via pyswisseph):
  Western: tropical zodiac, Placidus houses, transit-to-natal aspects.
  Vedic:   sidereal zodiac (Lahiri), nakshatras, whole-sign houses,
           Panchanga (daily lunar almanac), Vimshottari Dasha.

Everything here is pure computation. No interpretation lives in this file,
so the numbers can always be checked against any other ephemeris.
"""

import datetime as dt
from datetime import timedelta
from zoneinfo import ZoneInfo

import swisseph as swe

# Moshier model means no external data files are needed on Replit.
CALC_FLAG = swe.FLG_MOSEPH | swe.FLG_SPEED

# Lahiri is the standard ayanamsa for Vedic work.
swe.set_sid_mode(swe.SIDM_LAHIRI)

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
    "Rahu": swe.MEAN_NODE,  # north lunar node
}

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
    "Revati",
]

# Vimshottari mahadasha lords, in cyclic order, with their year lengths.
DASHA_SEQUENCE = [
    ("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10), ("Mars", 7),
    ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17),
]
DASHA_YEARS = dict(DASHA_SEQUENCE)
DASHA_NAMES = [d[0] for d in DASHA_SEQUENCE]

# Which mahadasha lord a nakshatra starts. 27 nakshatras, 9 lords, so the
# 9-lord pattern repeats three times.
NAK_LORDS = (["Ketu", "Venus", "Sun", "Moon", "Mars",
              "Rahu", "Jupiter", "Saturn", "Mercury"]) * 3

ASPECTS = {0: "conjunction", 60: "sextile", 90: "square",
           120: "trine", 180: "opposition"}

TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Purnima/Amavasya",
]

YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
    "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana", "Parigha",
    "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra",
    "Vaidhriti",
]

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"]


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------

def to_utc(local_dt, tz_name):
    """Turn a naive local datetime plus a timezone name into aware UTC."""
    aware = local_dt.replace(tzinfo=ZoneInfo(tz_name))
    return aware.astimezone(ZoneInfo("UTC"))


def julday(utc_dt):
    """Julian day (UT) from an aware UTC datetime."""
    hour = utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour)


# ---------------------------------------------------------------------------
# Positions
# ---------------------------------------------------------------------------

def _lon(jd, body, sidereal=False):
    flag = CALC_FLAG | (swe.FLG_SIDEREAL if sidereal else 0)
    xx, _ = swe.calc_ut(jd, body, flag)
    return xx[0] % 360, xx[3]  # longitude, longitude speed (deg/day)


def positions(jd, sidereal=False):
    """All tracked bodies. Rahu is the mean north node, Ketu is opposite."""
    out = {}
    for name, body in PLANETS.items():
        lon, speed = _lon(jd, body, sidereal)
        out[name] = {"lon": lon, "speed": speed,
                     "retro": speed < 0, "sign": SIGNS[int(lon // 30)],
                     "deg_in_sign": lon % 30}
    rahu = out["Rahu"]["lon"]
    ketu = (rahu + 180) % 360
    out["Ketu"] = {"lon": ketu, "speed": out["Rahu"]["speed"],
                   "retro": True, "sign": SIGNS[int(ketu // 30)],
                   "deg_in_sign": ketu % 30}
    return out


def tropical_houses(jd, lat, lon):
    """Placidus cusps plus ascendant and midheaven (tropical)."""
    cusps, ascmc = swe.houses(jd, lat, lon, b"P")
    if len(cusps) == 13:      # some wrapper versions pad index 0
        cusps = cusps[1:]
    return list(cusps), ascmc[0], ascmc[1]  # 12 cusps, Asc, MC


def house_of(lon, cusps):
    """Which of the 12 Placidus houses a longitude falls in."""
    for i in range(12):
        a = cusps[i]
        b = cusps[(i + 1) % 12]
        if a < b:
            if a <= lon < b:
                return i + 1
        else:  # this house wraps past 360
            if lon >= a or lon < b:
                return i + 1
    return 1


def sidereal_ascendant(jd, lat, lon):
    """Sidereal ascendant longitude, for whole-sign Vedic houses."""
    _, trop_asc, _ = tropical_houses(jd, lat, lon)
    ayan = swe.get_ayanamsa_ut(jd)
    return (trop_asc - ayan) % 360


# ---------------------------------------------------------------------------
# Nakshatra and Panchanga
# ---------------------------------------------------------------------------

NAK_SEG = 360 / 27  # 13 deg 20 min


def nakshatra(sidereal_lon):
    idx = int(sidereal_lon // NAK_SEG)
    pada = int((sidereal_lon % NAK_SEG) // (NAK_SEG / 4)) + 1
    return {"name": NAKSHATRAS[idx], "pada": pada, "index": idx,
            "lord": NAK_LORDS[idx]}


def panchanga(jd, weekday_index):
    """Daily lunar almanac. Geocentric, so effectively global for the day."""
    sun, _ = _lon(jd, swe.SUN, sidereal=True)
    moon, _ = _lon(jd, swe.MOON, sidereal=True)

    diff = (moon - sun) % 360
    tithi_num = int(diff // 12)            # 0..29
    paksha = "Shukla (waxing)" if tithi_num < 15 else "Krishna (waning)"
    tithi_name = TITHI_NAMES[tithi_num % 15]

    yoga_idx = int(((sun + moon) % 360) // NAK_SEG)
    yoga_name = YOGA_NAMES[yoga_idx]

    nak = nakshatra(moon)

    return {
        "tithi_number": tithi_num + 1,
        "tithi": tithi_name,
        "paksha": paksha,
        "yoga": yoga_name,
        "nakshatra": nak["name"],
        "nakshatra_pada": nak["pada"],
        "nakshatra_lord": nak["lord"],
        "vara": WEEKDAYS[weekday_index],
        "moon_sidereal_sign": SIGNS[int(moon // 30)],
    }


# ---------------------------------------------------------------------------
# Vimshottari Dasha
# ---------------------------------------------------------------------------

def _year_days(years):
    return years * 365.25


def dasha_periods(moon_sidereal_lon, birth_utc):
    """Full mahadasha timeline anchored to the natal Moon's nakshatra."""
    nak_idx = int(moon_sidereal_lon // NAK_SEG)
    frac = (moon_sidereal_lon % NAK_SEG) / NAK_SEG   # fraction traversed
    start_lord = NAK_LORDS[nak_idx]

    start_i = DASHA_NAMES.index(start_lord)
    seq = DASHA_SEQUENCE[start_i:] + DASHA_SEQUENCE[:start_i]

    # The first mahadasha is partly used up before birth.
    first_lord, first_years = seq[0]
    already = frac * first_years
    cursor = birth_utc - timedelta(days=_year_days(already))

    periods = []
    for lord, years in seq * 2:  # two loops covers well past a lifetime
        end = cursor + timedelta(days=_year_days(years))
        periods.append({"lord": lord, "start": cursor, "end": end,
                        "years": years})
        cursor = end
        if cursor.year - birth_utc.year > 130:
            break
    return periods


def antardashas(maha):
    """Sub-periods inside one mahadasha, same 9-lord order."""
    start_i = DASHA_NAMES.index(maha["lord"])
    seq = DASHA_NAMES[start_i:] + DASHA_NAMES[:start_i]
    out = []
    cursor = maha["start"]
    for lord in seq:
        dur_years = maha["years"] * DASHA_YEARS[lord] / 120.0
        end = cursor + timedelta(days=_year_days(dur_years))
        out.append({"lord": lord, "start": cursor, "end": end})
        cursor = end
    return out


def active_dasha(periods, when_utc):
    """Current mahadasha and antardasha for a given moment."""
    maha = next((p for p in periods if p["start"] <= when_utc < p["end"]),
                None)
    if maha is None:
        return None, None
    antar = next((a for a in antardashas(maha)
                  if a["start"] <= when_utc < a["end"]), None)
    return maha, antar


# ---------------------------------------------------------------------------
# Aspects
# ---------------------------------------------------------------------------

def aspect(lon_a, lon_b, orb=6.0):
    diff = abs(lon_a - lon_b) % 360
    if diff > 180:
        diff = 360 - diff
    for angle, name in ASPECTS.items():
        delta = abs(diff - angle)
        if delta <= orb:
            return {"aspect": name, "orb": round(delta, 2), "exact_at": angle}
    return None


def transit_aspects(transit_pos, natal_pos, bodies=None, orb=6.0):
    """Every tight transit-to-natal aspect, tightest first."""
    if bodies is None:
        bodies = ["Sun", "Moon", "Mercury", "Venus", "Mars",
                  "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    hits = []
    for t_name in bodies:
        t_lon = transit_pos[t_name]["lon"]
        for n_name in bodies:
            if n_name not in natal_pos:
                continue
            hit = aspect(t_lon, natal_pos[n_name]["lon"], orb)
            if hit:
                hits.append({
                    "transiting": t_name,
                    "natal": n_name,
                    "aspect": hit["aspect"],
                    "orb": hit["orb"],
                    "retro": transit_pos[t_name]["retro"],
                })
    hits.sort(key=lambda h: h["orb"])
    return hits


# ---------------------------------------------------------------------------
# Natal profile builder
# ---------------------------------------------------------------------------

def build_natal(birth_local, tz_name, lat, lon):
    """One call that assembles the whole birth chart both ways."""
    birth_utc = to_utc(birth_local, tz_name)
    jd = julday(birth_utc)

    trop = positions(jd, sidereal=False)
    sid = positions(jd, sidereal=True)
    cusps, asc, mc = tropical_houses(jd, lat, lon)
    sid_asc = sidereal_ascendant(jd, lat, lon)

    moon_sid = sid["Moon"]["lon"]
    periods = dasha_periods(moon_sid, birth_utc)

    return {
        "birth_utc": birth_utc,
        "jd": jd,
        "tropical": trop,
        "sidereal": sid,
        "cusps": cusps,
        "asc_tropical": asc,
        "mc_tropical": mc,
        "asc_sidereal": sid_asc,
        "asc_sidereal_sign": SIGNS[int(sid_asc // 30)],
        "moon_nakshatra": nakshatra(moon_sid),
        "dasha_periods": periods,
    }
