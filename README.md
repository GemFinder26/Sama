# Sama

**Sama** is the Somali word for sky.

An open source astrology app that reads the sky you were born under, and the
sky wherever you are today. Western and Vedic systems side by side, computed
from a real ephemeris, with the math shown before the meaning.

Read [ABOUT.md](ABOUT.md) for why this exists.

## What it does

- **Who you are.** A full natal reading in both the Western (tropical) and
  Vedic (sidereal) systems: your Sun, Moon and rising, your element and mode
  balance, every placement, the tightest aspects in your chart, and your Vedic
  Moon nakshatra.
- **Today.** Daily reading from the live sky: where the Moon is for you, the
  Vedic almanac (Panchanga), your current life chapter (Vimshottari Dasha),
  and tight transits to your birth chart.
- **Guidance.** Timing for the things people actually ask about: finances,
  deals and contracts, love, health, family, career, travel. Personalized
  through your Moon using Tarabala and Chandra Bala, with a plain verdict and
  every reason shown.
- **Week and month.** The slower weather ahead.
- **Where you are now.** Relocation astrology. Type any city and see which
  planets sit on your angles there.
- **Export.** Download your full reading as an Excel file.

## Honest by design

Every view shows the computed sky first and the interpretation second, so the
two never blur. Sama predicts nothing. It is a tool for reflection, not a
forecast of events. Health and finance carry their own note, and every screen
carries the standing caveat: for real decisions about money, health, or law,
consult a qualified professional.

The calculation engine (`astro.py`) contains no interpretation at all. You can
check every number it produces against any other ephemeris.

## Run it

```bash
pip install pyswisseph streamlit openpyxl tzdata geonamescache
streamlit run app.py
```

Then open the local URL it prints. Enter your birth date, exact time, and
birth city. City lookup is bundled and offline, so there is no API key and no
network call.

### On Replit

1. Create a Python Repl and add these files.
2. In the Shell: `pip install pyswisseph streamlit openpyxl tzdata geonamescache`
3. Press Run.

### Deploy free

Connect this repo to [Streamlit Community Cloud](https://share.streamlit.io)
and it deploys to a free public URL. No domain purchase needed.

## Birth time matters

The ascendant, the houses, and the Dasha timeline are all sensitive to the
exact minute of birth. A birth certificate is the most reliable source. If you
only know roughly, the sign-level reading still holds, but treat the house and
timing layers with appropriate skepticism.

## Files

| File | What it does |
|---|---|
| `app.py` | The interface and onboarding flow |
| `geo.py` | City name to coordinates and timezone (bundled, offline) |
| `astro.py` | The calculation engine. No interpretation inside it |
| `reading.py` | The natal interpretation engine |
| `domains.py` | Life-area timing (electional astrology) |
| `relocate.py` | Relocation astrology and the live local sky |
| `export.py` | Excel export |

## Contributing

Contributions are welcome, especially from people who know this material well.
Open an issue or a pull request. If you find a calculation error, that is the
most valuable thing you can report.

## License

AGPL-3.0. See [LICENSE](LICENSE).

Sama uses the [Swiss Ephemeris](https://www.astro.com/swisseph/) via
`pyswisseph`, which is dual licensed under the AGPL or a commercial license
from Astrodienst. This project is released under the AGPL accordingly. If you
fork this and run it as a closed-source or paid service, you will likely need
a commercial license from Astrodienst. That is your responsibility to confirm,
not legal advice from me.
