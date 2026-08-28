"""
Sama
A front-facing astrology app. Sama is the Arabic word for sky.

Flow:
  1. Welcome and onboarding: name, birth date, exact time, place.
  2. A full "who you are" reading built from the birth chart.
  3. Daily divination and life-area guidance from the live sky.
  4. Export your data to Excel.

Design rule throughout: show the computed sky, then the interpretation,
then a plain caveat. Nothing here predicts events, and nothing here is
medical, financial, or legal advice.
"""

import datetime as dt
from datetime import timedelta
from zoneinfo import ZoneInfo

import streamlit as st

import astro
import domains
import reading
import export
import relocate
import geo

st.set_page_config(page_title="Sama", page_icon="*", layout="wide")

CAVEAT = ("Sama is for reflection and entertainment. Astrology is an "
          "interpretive tradition, not a science, and nothing here predicts "
          "events. For decisions about money, health, or law, consult a "
          "qualified professional. You are the one making the call.")

def fmt_deg(x):
    d = int(x)
    m = int(round((x - d) * 60))
    return f"{d} deg {m:02d} min"


def ordinal(n):
    return f"{n}{'th' if 11 <= n <= 13 else {1:'st',2:'nd',3:'rd'}.get(n%10,'th')}"


# ---------------------------------------------------------------------------
# Onboarding
# ---------------------------------------------------------------------------

if "profile" not in st.session_state:
    st.session_state.profile = None

if st.session_state.profile is None:
    st.markdown("# Sama")
    st.markdown("### Read the sky you were born under, and the sky today.")
    st.write(
        "Sama takes your birth moment and place, builds your chart in both "
        "the Western and Vedic systems, and gives you a full reading of who "
        "you are. After that you can check the sky day by day for whatever "
        "you are weighing, from love to a deal to a move."
    )
    st.info(CAVEAT)

    st.markdown("#### Enter your birth details")
    st.caption("Time matters. A birth certificate is the most reliable "
               "source. If you only know roughly, the sign-level reading "
               "still holds, but houses and timing need the exact minute.")

    name = st.text_input("Your name (optional)", "")
    c1, c2 = st.columns(2)
    b_date = c1.date_input("Birth date", dt.date(1990, 1, 1),
                           min_value=dt.date(1900, 1, 1),
                           max_value=dt.date(2100, 1, 1))
    b_time = c2.time_input("Birth time (24h)", dt.time(12, 0))

    city_query = st.text_input("Birth city", "",
                               placeholder="e.g. Merida, Oakland, Accra")
    chosen = None
    if city_query:
        matches = geo.search_cities(city_query)
        if matches:
            labels = [m["label"] for m in matches]
            pick = st.selectbox("Pick the right one", labels)
            chosen = matches[labels.index(pick)]
        else:
            st.warning("No city found by that name. Try a nearby larger city.")

    if st.button("Reveal my chart", type="primary", disabled=chosen is None):
        st.session_state.profile = {
            "name": name, "date": b_date, "time": b_time,
            "tz": chosen["tz"], "lat": chosen["lat"], "lon": chosen["lon"],
            "city": chosen["label"],
        }
        st.rerun()
    if chosen is None and city_query:
        st.caption("Choose a city match above to continue.")
    elif not city_query:
        st.caption("Type your birth city to continue.")
    st.stop()

# ---------------------------------------------------------------------------
# Build chart from stored profile
# ---------------------------------------------------------------------------

p = st.session_state.profile
birth_local = dt.datetime.combine(p["date"], p["time"])
try:
    natal = astro.build_natal(birth_local, p["tz"], p["lat"], p["lon"])
except Exception as e:
    st.error(f"Could not build the chart. Check your details. Details: {e}")
    if st.button("Start over"):
        st.session_state.profile = None
        st.rerun()
    st.stop()

# Sidebar
st.sidebar.markdown("# Sama")
st.sidebar.write(f"Reading for **{p['name'] or 'you'}**")
st.sidebar.caption(f"{p['date'].strftime('%B %d, %Y')} at "
                   f"{p['time'].strftime('%H:%M')}")
st.sidebar.caption(f"Born in {p.get('city', 'unknown')}")

st.sidebar.divider()
st.sidebar.markdown("**Where you are now**")
st.sidebar.caption("Update this whenever you travel.")

if "current" not in st.session_state:
    st.session_state.current = {
        "tz": p["tz"], "lat": p["lat"], "lon": p["lon"],
        "label": p.get("city", "birthplace"),
    }

cur_query = st.sidebar.text_input("Your current city", "",
                                  placeholder="type a city to update")
if cur_query:
    cur_matches = geo.search_cities(cur_query, limit=5)
    if cur_matches:
        cur_labels = [m["label"] for m in cur_matches]
        cur_pick = st.sidebar.selectbox("Confirm", cur_labels)
        if st.sidebar.button("Set as my location"):
            m = cur_matches[cur_labels.index(cur_pick)]
            st.session_state.current = {
                "tz": m["tz"], "lat": m["lat"], "lon": m["lon"],
                "label": m["label"],
            }
            st.rerun()
    else:
        st.sidebar.caption("No match. Try a larger nearby city.")

st.sidebar.success(f"Now in: {st.session_state.current['label']}")
view_tz = st.session_state.current["tz"]

if st.sidebar.button("Start over with new birth details"):
    st.session_state.profile = None
    st.session_state.pop("current", None)
    st.rerun()


def now_view():
    return dt.datetime.now(ZoneInfo(view_tz))


def sky_for(date):
    noon = dt.datetime.combine(date, dt.time(12, 0))
    utc = noon.replace(tzinfo=ZoneInfo(view_tz)).astimezone(ZoneInfo("UTC"))
    jd = astro.julday(utc)
    return jd, utc, astro.positions(jd, sidereal=False)


HOUSE_HINT = {
    1: "focus swings to you, your body, your presence.",
    2: "money, values, food, self-worth come forward.",
    3: "talking, writing, errands, siblings, short trips.",
    4: "home, roots, family, the private interior.",
    5: "play, creativity, romance, kids, risk.",
    6: "work, routine, health, service, the daily grind.",
    7: "partners, clients, the one across from you.",
    8: "depth, shared money, intimacy, what is hidden.",
    9: "meaning, travel, teaching, the big picture.",
    10: "career, reputation, the public eye.",
    11: "community, networks, goals, the future.",
    12: "rest, retreat, dreams, closure, the unseen.",
}

ASPECT_TONE = {
    "conjunction": "a fusing, intensifying contact",
    "sextile": "an easy, opportunity-flavored contact",
    "square": "a friction point that pushes action",
    "trine": "a smooth, supportive flow",
    "opposition": "a pull between two sides that wants balance",
}

PLANET_THEME = {
    "Sun": "identity and vitality", "Moon": "mood and needs",
    "Mercury": "thinking and messages", "Venus": "love and money",
    "Mars": "drive and conflict", "Jupiter": "growth and luck",
    "Saturn": "structure and limits", "Uranus": "surprise and change",
    "Neptune": "dreams and idealizing", "Pluto": "power and depth",
}

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

st.title(f"Welcome{', ' + p['name'] if p['name'] else ''}")

tab_you, tab_today, tab_guide, tab_range, tab_place, tab_export = st.tabs(
    ["Who you are", "Today", "Guidance", "Week and month",
     "Where you are now", "Export"])

# ---- Who you are ----
with tab_you:
    rd = reading.full_reading(natal)
    st.subheader(rd["headline"]["line"].split(".")[0])
    st.write(rd["headline"]["line"])

    st.divider()
    st.markdown("**Your balance**")
    b = rd["balance"]
    st.write(b["text"])
    st.caption("Elements: " + ", ".join(f"{k} {v}"
               for k, v in b["elements"].items())
               + "  |  Modes: " + ", ".join(f"{k} {v}"
               for k, v in b["modalities"].items()))

    st.divider()
    st.markdown("**Your placements**")
    for line in rd["placements"]:
        st.write(f"- {line}")

    st.divider()
    st.markdown("**The strongest connections in your chart**")
    for a in rd["aspects"]:
        st.write(f"- {a['text']}")

    st.divider()
    st.markdown("**Your Vedic layer**")
    st.write(rd["vedic"]["text"])

    st.info(CAVEAT)

# ---- Today ----
with tab_today:
    pick = st.date_input("Day", now_view().date(), key="todaypick")
    jd, utc, trans = sky_for(pick)
    st.subheader(pick.strftime("%A, %B %d, %Y"))

    moon = trans["Moon"]
    mh = astro.house_of(moon["lon"], natal["cusps"])
    st.markdown("**Where the Moon is for you**")
    st.write(f"Moon in {moon['sign']}, moving through your "
             f"{ordinal(mh)} house.")
    st.caption(HOUSE_HINT.get(mh, ""))

    st.divider()
    pan = astro.panchanga(jd, pick.weekday())
    st.markdown("**Vedic almanac**")
    c1, c2, c3 = st.columns(3)
    c1.metric("Tithi", pan["tithi"])
    c1.caption(pan["paksha"])
    c2.metric("Nakshatra", pan["nakshatra"])
    c2.caption(f"pada {pan['nakshatra_pada']}, lord {pan['nakshatra_lord']}")
    c3.metric("Yoga", pan["yoga"])

    st.divider()
    maha, antar = astro.active_dasha(natal["dasha_periods"], utc)
    st.markdown("**Your Vedic life chapter right now**")
    if maha:
        line = f"Mahadasha {maha['lord']}"
        if antar:
            line += f", sub-period {antar['lord']}"
        st.write(line)

    st.divider()
    st.markdown("**Tight contacts to your birth chart**")
    hits = astro.transit_aspects(trans, natal["tropical"], orb=5.0)
    if not hits:
        st.write("Quiet day, no tight aspects within 5 degrees.")
    for h in hits[:6]:
        r = " (retrograde)" if h["retro"] else ""
        st.write(f"- Transiting {h['transiting']}{r} {h['aspect']} "
                 f"natal {h['natal']} (orb {h['orb']})")
        st.caption(f"{ASPECT_TONE[h['aspect']]}: "
                   f"{PLANET_THEME[h['transiting']]} meeting your "
                   f"{PLANET_THEME[h['natal']]}.")
    st.info(CAVEAT)

# ---- Guidance ----
with tab_guide:
    st.subheader("What are you weighing?")
    st.caption("Pick an area and a day. Sama reads the timing for you, "
               "personalized through your Moon.")
    g_date = st.date_input("Day", now_view().date(), key="guidedate")
    g_jd, g_utc, g_trans = sky_for(g_date)
    g_wk = g_date.weekday()

    st.markdown("**All areas at a glance**")
    for row in domains.scan_all(natal, g_trans, g_jd, g_wk, natal["cusps"]):
        color = ("green" if row["score"] >= 2 else
                 "orange" if row["score"] >= -1 else "red")
        st.write(f":{color}[{row['verdict']}]  |  {row['domain']} "
                 f"(score {row['score']:+d})")

    st.divider()
    choice = st.selectbox("Look closer", list(domains.DOMAINS.keys()))
    r = domains.read_domain(choice, natal, g_trans, g_jd, g_wk,
                            natal["cusps"])
    color = ("green" if r["score"] >= 2 else
             "orange" if r["score"] >= -1 else "red")
    st.markdown(f"### :{color}[{r['verdict']}]")
    st.caption(f"Day nakshatra {r['day_nakshatra']} ({r['activity']} "
               f"nature), total score {r['score']:+d}")
    st.markdown("**Why**")
    for line in r["reasons"]:
        st.write(f"- {line}")
    st.warning(r["note"])
    st.info(CAVEAT)

# ---- Week and month ----
with tab_range:
    mode = st.radio("View", ["This week", "This month"], horizontal=True)

    if mode == "This week":
        start = st.date_input("Week starting", now_view().date(),
                              key="weekpick")
        st.markdown("**The Moon's path this week**")
        for i in range(7):
            d = start + timedelta(days=i)
            jd, _, trans = sky_for(d)
            pan = astro.panchanga(jd, d.weekday())
            mh = astro.house_of(trans["Moon"]["lon"], natal["cusps"])
            st.write(f"{d.strftime('%a %m/%d')}: Moon in "
                     f"{trans['Moon']['sign']} (your {ordinal(mh)} house), "
                     f"nakshatra {pan['nakshatra']}")
    else:
        today = now_view().date()
        c1, c2 = st.columns(2)
        yr = c1.number_input("Year", value=today.year, step=1)
        mo = c2.number_input("Month", value=today.month, min_value=1,
                            max_value=12, step=1)
        first = dt.date(int(yr), int(mo), 1)
        nxt = (dt.date(int(yr) + 1, 1, 1) if int(mo) == 12
               else dt.date(int(yr), int(mo) + 1, 1))
        last = nxt - timedelta(days=1)
        _, _, ta = sky_for(first)
        _, _, tb = sky_for(last)
        st.markdown(f"**Slow-planet weather for {first.strftime('%B %Y')}**")
        for pl in ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]:
            a, b = ta[pl], tb[pl]
            moved = ("holds in " + a["sign"]) if a["sign"] == b["sign"] else (
                f"moves {a['sign']} into {b['sign']}")
            retro = " (retrograde)" if b["retro"] else ""
            st.write(f"{pl}: {moved}{retro}")
    st.info(CAVEAT)

# ---- Where you are now ----
with tab_place:
    st.subheader("How this place is affecting you")
    st.caption("Your birth chart never changes. What changes with location "
               "is which planets sit on your angles. This is relocation "
               "astrology. Set your city in the sidebar, or preview another "
               "place below.")

    cur = st.session_state.current
    cur_lat, cur_lon, cur_label = cur["lat"], cur["lon"], cur["label"]

    preview = st.text_input("Preview a different city (optional)", "",
                            placeholder="e.g. Tokyo, Lagos, Lisbon",
                            key="previewcity")
    if preview:
        pm = geo.search_cities(preview, limit=5)
        if pm:
            plabels = [m["label"] for m in pm]
            ppick = st.selectbox("Which one", plabels, key="previewpick")
            chosen = pm[plabels.index(ppick)]
            cur_lat, cur_lon, cur_label = (chosen["lat"], chosen["lon"],
                                           chosen["label"])
        else:
            st.warning("No city found by that name.")

    st.write(f"Reading location: **{cur_label}**")
    st.divider()
    reloc = relocate.relocated_chart(natal, cur_lat, cur_lon)
    st.markdown("**Your angles here**")
    st.write(f"Rising sign becomes {reloc['asc_sign']}, "
             f"midheaven becomes {reloc['mc_sign']} at this location.")

    st.markdown("**What this place amplifies for you**")
    if reloc["angular"]:
        for a in reloc["angular"]:
            st.write(f"- {a['text']} (orb {a['orb']} deg)")
    else:
        st.write("No planet sits tightly on your angles here. This place "
                 "runs quieter for you, without a single loud theme.")

    if reloc["house_moves"]:
        movers = ", ".join(f"{m['planet']} (house {m['from']} to {m['to']})"
                           for m in reloc["house_moves"][:6])
        st.caption(f"Planets that shift house emphasis here: {movers}")

    st.divider()
    st.markdown("**The sky over you right now**")
    sky = relocate.local_sky(cur_lat, cur_lon, now_view().astimezone(
        ZoneInfo("UTC")))
    if sky["near"]:
        for n in sky["near"]:
            st.write(f"- {n['text']} (orb {n['orb']} deg)")
    else:
        st.write("No planet is exactly on your local horizon this moment.")
    st.info(CAVEAT)

# ---- Export ----
with tab_export:
    st.subheader("Keep your data")
    st.write("Export your full chart, your Dasha timeline, today's sky, and "
             "today's area guidance as an Excel file.")
    exp_date = now_view().date()
    jd, _, trans = sky_for(exp_date)
    data = export.build_workbook(natal, p["name"], trans, jd,
                                 exp_date.weekday())
    fname = f"sama_{(p['name'] or 'reading').lower().replace(' ', '_')}.xlsx"
    st.download_button(
        "Download my Sama reading (Excel)",
        data=data, file_name=fname,
        mime="application/vnd.openxmlformats-officedocument."
             "spreadsheetml.sheet",
    )
    st.info(CAVEAT)
