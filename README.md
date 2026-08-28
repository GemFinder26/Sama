Sama

Sama means sky in Arabic.

This is an open source astrology app. It reads the sky you were born under, in both the Western and Vedic traditions, and it reads the sky wherever you are right now. The idea behind it, and why it's free, is in ABOUT.md.

What's in it

Give it your birth date, time, and city, and you get a full natal reading in both systems: Sun, Moon, rising, your placements, your strongest aspects, and your Vedic Moon nakshatra.

From there you can check the sky day by day. There's a daily read (where the Moon is for you, the Vedic almanac, your current Dasha, and any tight transits hitting your chart), a week and month view for the slower-moving stuff, and a guidance section for the things people actually ask an astrologer about: money, deals, love, health, family, career, travel. That last part is personalized to your Moon through Tarabala and Chandra Bala, and it shows its reasoning rather than just handing you a verdict.

There's also a relocation tab, since your birth chart doesn't change when you travel but the angles do. Type in any city and see what shifts. And you can export the whole reading to Excel if you want to keep it.

Why the math comes first

I didn't want another astrology app where you just have to trust the output. astro.py is pure calculation, no interpretation in it at all, so you can check every number against any other ephemeris if you want to. The interpretation is built on top of that, kept separate, so the two never blur together.

This is a tool for reflection, not a prediction machine. Health and finance sections carry their own caveat, and it shows up everywhere: for real decisions about money, health, or law, talk to an actual professional.

Running it
bash
pip install pyswisseph streamlit openpyxl tzdata geonamescache
streamlit run app.py

That opens it locally. Enter your birth details and go. City lookup is bundled and works offline, no API key needed.

On Replit: import this repo, open the Shell, run the same pip install line above, then hit Run.

Free hosting: connect this repo to Streamlit Community Cloud and it deploys to a public URL for free, no domain needed.

A note on birth time

Houses, the ascendant, and your Dasha timeline are all sensitive to the exact minute you were born. A birth certificate is the best source if you have access to one. If you only know roughly, the sign-level reading still holds, just take the house-level stuff with a grain of salt.

Files
app.py — the interface and onboarding
geo.py — city name to coordinates and timezone, offline
astro.py — the calculation engine, no interpretation
reading.py — the natal reading
domains.py — life-area timing
relocate.py — relocation astrology
export.py — Excel export
Contributing

If you know this material and see something off, open an issue or a pull request. Calculation errors are the most useful thing to flag.

License

AGPL-3.0, see LICENSE. Sama runs on the Swiss Ephemeris via pyswisseph, which is dual licensed AGPL or commercial. If you fork this and run it closed-source or as a paid service, you'll likely need a commercial license from Astrodienst — confirm that with them directly.
Sama uses the [Swiss Ephemeris](https://www.astro.com/swisseph/) via
`pyswisseph`, which is dual licensed under the AGPL or a commercial license
from Astrodienst. This project is released under the AGPL accordingly. If you
fork this and run it as a closed-source or paid service, you will likely need
a commercial license from Astrodienst. That is your responsibility to confirm,
not legal advice from me.
