# Wyoming

Daily aggregator of Wyoming-located taildragger classified listings,
pulled from every one of the taildraggers.com per-manufacturer scraper
repos, published as a static page (`docs/index.html`) meant to be
embedded via `<iframe>` on taildraggers.com's state-listing pages.

A straight copy of the companion [Alabama](https://github.com/taildraggers/alabama)/
[Alaska](https://github.com/taildraggers/alaska)/[Arizona](https://github.com/taildraggers/arizona)/
[Arkansas](https://github.com/taildraggers/arkansas)/[California](https://github.com/taildraggers/california)/
[Colorado](https://github.com/taildraggers/colorado)/[Connecticut](https://github.com/taildraggers/connecticut)/
[Delaware](https://github.com/taildraggers/delaware)/[Florida](https://github.com/taildraggers/florida)/
[Georgia](https://github.com/taildraggers/georgia)/[Hawaii](https://github.com/taildraggers/hawaii)/
[Idaho](https://github.com/taildraggers/idaho)/[Illinois](https://github.com/taildraggers/illinois)/
[Indiana](https://github.com/taildraggers/indiana)/[Iowa](https://github.com/taildraggers/iowa)/
[Kansas](https://github.com/taildraggers/kansas)/[Kentucky](https://github.com/taildraggers/kentucky)/
[Louisiana](https://github.com/taildraggers/louisiana)/[Maine](https://github.com/taildraggers/maine)/
[Maryland](https://github.com/taildraggers/maryland)/[Massachusetts](https://github.com/taildraggers/massachusetts)/
[Michigan](https://github.com/taildraggers/michigan)/[Minnesota](https://github.com/taildraggers/minnesota)/
[Mississippi](https://github.com/taildraggers/mississippi)/[Missouri](https://github.com/taildraggers/missouri)/
[Montana](https://github.com/taildraggers/montana)/[Nebraska](https://github.com/taildraggers/nebraska)/
[Nevada](https://github.com/taildraggers/nevada)/[New Hampshire](https://github.com/taildraggers/new-hampshire)/
[New Jersey](https://github.com/taildraggers/new-jersey)/[New Mexico](https://github.com/taildraggers/new-mexico)/
[New York](https://github.com/taildraggers/new-york)/[North Carolina](https://github.com/taildraggers/north-carolina)/
[North Dakota](https://github.com/taildraggers/north-dakota)/[Ohio](https://github.com/taildraggers/ohio)/
[Oklahoma](https://github.com/taildraggers/oklahoma)/[Oregon](https://github.com/taildraggers/oregon)/
[Pennsylvania](https://github.com/taildraggers/pennsylvania)/[Rhode Island](https://github.com/taildraggers/rhode-island)/
[South Carolina](https://github.com/taildraggers/south-carolina)/[South Dakota](https://github.com/taildraggers/south-dakota)/
[Tennessee](https://github.com/taildraggers/tennessee)/[Texas](https://github.com/taildraggers/texas)/
[Utah](https://github.com/taildraggers/utah)/
[Vermont](https://github.com/taildraggers/vermont)/
[Virginia](https://github.com/taildraggers/virginia)/
[Washington](https://github.com/taildraggers/washington)/
[West Virginia](https://github.com/taildraggers/west-virginia)/
[Wisconsin](https://github.com/taildraggers/wisconsin) repos' approach,
with the state filter swapped to "WY".

This repo doesn't scrape Barnstormers.com itself. Every companion
manufacturer repo - [Aeronca](https://github.com/taildraggers/aeronca),
[American Champion](https://github.com/taildraggers/american-champion),
[Aviat](https://github.com/taildraggers/aviat),
[Beechcraft](https://github.com/taildraggers/beech),
[Bellanca](https://github.com/taildraggers/bellanca),
[Cessna](https://github.com/taildraggers/cessna),
[CubCrafters](https://github.com/taildraggers/cub-crafters),
[de Havilland](https://github.com/taildraggers/de-Havilland),
[Fairchild](https://github.com/taildraggers/fairchild),
[Just Aircraft](https://github.com/taildraggers/just-aircraft),
[Kitfox](https://github.com/taildraggers/kitfox),
[Luscombe](https://github.com/taildraggers/luscombe),
[Maule](https://github.com/taildraggers/maule),
[Piper](https://github.com/taildraggers/piper),
[Pitts](https://github.com/taildraggers/pitts),
[RANS](https://github.com/taildraggers/rans),
[Stearman](https://github.com/taildraggers/stearman),
[Stinson](https://github.com/taildraggers/stinson),
[Swift](https://github.com/taildraggers/swift),
[Taylorcraft](https://github.com/taildraggers/taylorcraft),
[Van's RV](https://github.com/taildraggers/vans), and
[Waco](https://github.com/taildraggers/waco) - already scrapes
Barnstormers on its own daily schedule and publishes its own listings
page. This repo fetches all 23 of those already-published GitHub Pages
sites, pulls every listing row back out, and keeps only the ones whose
Location column ends in `, WY`.

## How it works

- `main.py` fetches `https://taildraggers.github.io/<repo>/` for every
  repo in `SOURCE_SITES` (the same list the companion
  [taildragger-ad-count](https://github.com/taildraggers/taildragger-ad-count)
  repo's totalizer uses). GitHub Pages serves plain static HTML with no
  bot protection - unlike Barnstormers.com, which sits behind Cloudflare
  and needs a real headless browser to clear (see every scraper repo's
  `scraper/common.py`) - so this uses a plain stdlib HTTP request instead
  of Playwright; no browser install step needed in the workflow either.
- Each fetched page's listing table is parsed back into `(title, url,
  price, location, date posted, site)` rows - exactly the 5 columns every
  companion repo's `render_html()` produces. Rows are kept only if their
  Location cell ends in `, WY` (case-insensitive), then de-duplicated by
  URL and sorted newest-posted-first, same as every companion repo. One
  source site failing to fetch only drops that site's contribution for
  the run - it doesn't fail the whole job (check the Action logs for
  `[warn]` lines).
- The result is rendered into `docs/index.html` titled **"Taildragger Ads
  in Wyoming"**, using the exact same table/card layout, dark-mode
  styling, and auto-resize `postMessage` script as every companion repo -
  **except** there's no "Search More Listings" section linking out to
  Trade-A-Plane/Controller/ASO at the bottom, since those searches aren't
  state-scoped and wouldn't make sense here.
- `.github/workflows/daily-aggregate.yml` runs the whole thing once a day
  (13:30 UTC - 30 minutes after the manufacturer repos' own 13:00 UTC
  runs, so this picks up same-day updates rather than yesterday's pages),
  commits the regenerated `docs/index.html` if it changed, and can also
  be triggered manually from the Actions tab (`workflow_dispatch`).

## One-time setup: enable GitHub Pages

This repo publishes `docs/index.html` as a plain static file — GitHub Pages just needs
to be pointed at it once:

1. Go to **Settings → Pages** in this repository.
2. Under **Build and deployment → Source**, choose **Deploy from a branch**.
3. Branch: `main`, folder: `/docs`. Save.
4. GitHub will publish the page at `https://taildraggers.github.io/wyoming/`
   (may take a minute or two the first time).

Also check **Settings → Actions → General**:
- **Actions permissions**: "Allow all actions and reusable workflows".
- **Workflow permissions**: "Read and write permissions" (needed so the daily
  job can commit the regenerated page back to the repo).

## Embedding on taildraggers.com

```html
<iframe
  src="https://taildraggers.github.io/wyoming/"
  title="Taildragger Ads in Wyoming"
  style="width: 100%; height: 800px; border: 0;"
  loading="lazy">
</iframe>
```

The page also posts its rendered height to the parent window on load/resize
(`{ type: "taildraggers:resize", height }`) so it can be auto-sized instead
of using a fixed guessed height - add a matching `message` listener on the
embedding page to pick this up.

## Running locally

```bash
pip install -r requirements.txt
python main.py
```

This writes/overwrites `docs/index.html`. No browser/Playwright install needed.

## Notes

- If a companion repo changes its page markup (column order, table
  structure), update `_parse_listing_rows()` in `main.py` to match.
- If a companion repo hasn't had GitHub Pages enabled yet, or is
  otherwise unreachable, its listings just don't show up for that run
  (logged as a `[warn]`) - not a fatal error.
- Adding a new manufacturer repo to the family means adding its repo name
  to `SOURCE_SITES` in `main.py` - the same one-line change needed in the
  companion taildragger-ad-count repo.
- This repo could be copied/adapted for other states by changing
  `STATE_ABBR` and `_WYOMING_LOCATION_RE` in `main.py`, and updating
  `PAGE_TITLE`.
