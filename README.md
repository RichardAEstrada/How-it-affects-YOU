# How It Affects You

A public, mobile-first situational-awareness dashboard. Informational only, not an emergency notification service.

## Run and test

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/collect_news.py
python3 -m http.server 8000
```

The collector uses Python's standard library. Browser tests additionally require Playwright/Chromium (`node tests/browser.cjs` when installed). Open http://localhost:8000, not a `file:` URL.

## News delivery and honest failure states

`data/news.json` is same-origin public JSON built from the publishers' own RSS endpoints: NPR News, The Guardian World, BBC World, Fox News, NBCNews.com. No anonymous RSS-to-JSON proxy, API key, article-body scraping, or invented stories. Linked headlines, publisher attribution, authors when supplied, publication times and source categories are retained. Publisher content remains its owner's property; review publisher feed terms for any commercial reuse.

**Automatic collection is not yet enabled.** The currently published news JSON is a manually fetched snapshot. Browser rechecks never refresh publisher collection timestamps. An hourly collector workflow is prepared locally but is not part of the repository until its publishing-permission change is approved. GitHub schedules can be delayed or disabled for inactive repositories; this is not real-time. Browser checks every 15 minutes while visible. Each source keeps its own last-attempt and last-success timestamps. A failed source retains only its previously fetched headlines, never a fabricated replacement; healthy publishers remain visible. A source older than two hours is marked stale. The browser can retain the public snapshot in local storage; this does not reset source timestamps. Sports exclusion applies before display, filtering, rotation and retained cache use.

The manual collector reads the previous `data/news.json` and preserves per-publisher last-known data. The proposed scheduled version would retain the previous snapshot in GitHub Actions cache, with the committed snapshot as an honestly dated fallback if evicted. Public snapshots are the only cache contents. No user location or account data is included. The deploy artifact contains only the public HTML/config/news/build metadata, not scripts or test fixtures.

### Publishing configuration

Current publishing remains the existing **main branch / root** configuration; no Pages settings were changed. To enable the proposed hourly workflow after approval, the repository's GitHub Pages source would be **GitHub Actions**. The proposed build job has `contents: read` only; checkout credentials are not persisted. Its separate deploy job would use `pages: write` and short-lived `id-token: write` scoped to the `github-pages` environment. No added secrets, PAT, new OAuth scope, or paid service is needed. Verify the branch head and successful Pages deployment for the published revision. The proposed workflow would also publish `build.json`. Do not change account-wide permissions.

## Other data and limits

- Weather and air quality: modeled Open-Meteo/CAMS values, not local station measurements. Model-valid time and retrieval time are separate; stale/invalid model timestamps are flagged.
- U.S. weather alerts: National Weather Service for the selected rounded point. Unavailable/stale alerts are never treated as an all-clear. International official alerts are external links.
- Radar: unaltered NWS CONUS image. Its printed observation timestamps, not retrieval time, determine currency.
- Oncor and internet outages: verified outbound official resources only. No live counts, restoration estimates, home status, private APIs, iframes or account data. Provider is never inferred from a city. Broader Cloudflare Radar/IODA observations do not confirm a home outage. Internet outages do not by themselves prove or predict an electricity outage.
- Dallas reports: citywide aggregated police reports, not crimes proven, unique person counts, safety scores, or real-time incidents. Source publication may lag.
- Conflict and election information: manually sourced historical **20 October 2026** snapshots, not a live intelligence/voting-deadline feed. Follow linked official current sources.
- Doomsday Clock: the Bulletin's 2026 symbolic **85 seconds**, manually checked 26 October 2026. Not a countdown or a disaster prediction.
- Device/selected-city screen clock is separate from source timestamps, which are explicitly UTC.

## Privacy

No covert geolocation. City lookup occurs only when requested. Browser geolocation requires an explicit button click and browser permission; coordinates are rounded before weather requests. Remembered city and display preferences remain in local browser storage. Outage links contain no coordinates or account data. Internet-provider selection stays only in the current tab. Check the privacy/refresh details in the page for third-party services.
