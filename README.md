# Opera Atlas

Multilingual (ქართული / English / Italiano / Русский) opera calendar, premieres, reviews and a section on mezzo-soprano Nino Surguladze. Free to host.

## Files
- `index.html` – the site. Reads `data.json` and `feed.json` at load time.
- `data.json` – curated content: events, announcements, reviews, Nino's timeline (all four languages).
- `feed.json` – headlines collected automatically every day.
- `scripts/update.py` – the daily collector (Python standard library only).
- `.github/workflows/update.yml` – runs the collector daily and commits the result.

## Publish (about 5 minutes, free)
1. Create a GitHub account if you do not have one, then a new **public** repository named `opera-atlas`.
2. Upload every file in this folder (keep the folder structure, including `.github/workflows`).
3. Repository **Settings → Pages → Build and deployment**: Source `Deploy from a branch`, Branch `main`, folder `/ (root)`. Save.
4. Repository **Actions** tab: enable workflows, open "Update Opera Atlas", press **Run workflow** once to test.
5. The site address will be `https://<your-username>.github.io/opera-atlas/`.

## What updates by itself
- Upcoming and past lists change daily by the visitor's clock.
- Headlines and every new mention of Nino Surguladze appear from the feeds in `scripts/update.py`.

## What stays manual
New calendar entries, premieres, reviews and translated descriptions are written into `data.json`. Ask Claude to add them: paste a link or a season announcement and it will add the entry in all four languages.
