# How It Affects You

A mobile-first current-events dashboard focused on practical daily-life impact.

## Included in this MVP
- Live National Weather Service active alerts for the selected point.
- Near-real-time global headline discovery using GDELT.
- Sections for fuel/energy, military/global events, weather, transportation and household impact.
- Impact-first presentation instead of partisan scoring.
- Responsive dark UI.
- Fort Worth and Cleburne location presets in the static MVP.

## Run it
Because browsers can restrict API calls from `file://`, serve this folder locally:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

It can also be uploaded directly to GitHub Pages.

## Production upgrades
1. Add a serverless API layer (Cloudflare Workers, Vercel or Netlify) for caching and API keys.
2. Add a nationwide ZIP/city geocoder.
3. Register for an EIA API key and wire EIA v2 gasoline, diesel and petroleum datasets.
4. Add source-ranking and deduplication for developing news.
5. Add push/email alerts based on user-selected location and interests.
6. Store user preferences without exposing precise location.
7. Add historical charts and a "what changed since yesterday" daily brief.

## Sources
- National Weather Service API: https://api.weather.gov
- EIA API: https://www.eia.gov/developer/
- GDELT DOC 2.0: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/

Important: This dashboard is informational. Users should confirm emergency warnings with official authorities.

## Nationwide location update
This build no longer defaults to Fort Worth. Visitors can:
- Enter a U.S. city/state or ZIP code.
- Use browser geolocation after granting permission.
- Keep the selected location locally in their browser for the next visit.
- Receive National Weather Service alerts for the chosen coordinates.

City/ZIP lookup uses the U.S. Census Geocoder. Browser geolocation coordinates are used client-side and are not sent to this demo's own server.
