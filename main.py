"""Aggregates Wyoming-located listings from every taildraggers.com
manufacturer scraper site into one page.

Each of the companion per-manufacturer repos (Aeronca, Piper, Cessna,
Van's RV, Stearman, Waco, Pitts, Taylorcraft, Swift, Beechcraft, Air
Tractor, Fairchild, Stinson, and the rest) already scrapes Barnstormers.com
and publishes its own listings to its own GitHub Pages site, one row per
listing with a Location column already formatted as "City, ST" (see
extract_location() in every one of those repos' scraper/common.py). This
repo doesn't scrape Barnstormers itself - it fetches each of those 23
already-published pages (same list the companion taildragger-ad-count
repo's totalizer uses), pulls out every listing row, and keeps only the
ones whose location ends in ", WY".

GitHub Pages serves plain static HTML with no bot protection (unlike
Barnstormers.com, which sits behind Cloudflare and needs a real headless
browser to clear it - see every scraper repo's common.py) - so this uses
a plain stdlib HTTP request instead of Playwright. No browser install
step needed in the workflow either.

This repo is a straight copy of the companion Alabama/Alaska/Arizona/Arkansas/
California/Colorado/Connecticut/Delaware/Florida/Georgia/Hawaii/Idaho/Illinois/
Indiana/Iowa/Kansas/Kentucky/Louisiana/Maine/Maryland/Massachusetts/Michigan/
Minnesota/Mississippi/Missouri/Montana/Nebraska/Nevada/New Hampshire/New
Jersey/New Mexico/New York/North Carolina/North Dakota/Ohio/Oklahoma/Oregon/
Pennsylvania/Rhode Island/South Carolina/South Dakota/Tennessee/Texas/Utah/
Vermont/Virginia/Washington/West Virginia/Wisconsin repos' approach, with
the state filter swapped to "WY".
"""
from __future__ import annotations

import datetime as dt
import html
import os
import re
import urllib.request
from dataclasses import dataclass

from bs4 import BeautifulSoup

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "docs", "index.html")
PAGE_TITLE = "Taildragger Ads in Wyoming"
STATE_ABBR = "WY"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT_SECONDS = 30

# Every taildraggers.com manufacturer scraper repo, each publishing its own
# listings page to its own GitHub Pages site at this URL pattern - the same
# list used by the companion taildragger-ad-count repo's totalizer.
SOURCE_SITES = [
    "aeronca",
    "airtractor",
    "american-champion",
    "aviat",
    "beech",
    "bellanca",
    "cessna",
    "cub-crafters",
    "de-Havilland",
    "fairchild",
    "just-aircraft",
    "kitfox",
    "luscombe",
    "maule",
    "piper",
    "pitts",
    "rans",
    "stearman",
    "stinson",
    "swift",
    "taylorcraft",
    "vans",
    "waco",
]


@dataclass
class Listing:
    title: str
    price: str
    location: str
    date_posted: str
    site: str
    url: str

    def key(self) -> str:
        return self.url


def fetch(url: str) -> str | None:
    """Fetch a plain static page over HTTP, or None on failure."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8", errors="replace")
    except Exception as exc:  # one site failing shouldn't kill the whole run
        print(f"  [warn] {url} -> {exc}")
        return None


def _parse_listing_rows(page_html: str) -> list[Listing]:
    """Pulls every listing row out of a companion repo's published
    docs/index.html - same 5-column table every one of those repos
    renders (see render_html() in each repo's main.py)."""
    soup = BeautifulSoup(page_html, "lxml")
    listings = []
    for row in soup.select("tbody tr"):
        cells = row.find_all("td")
        if len(cells) != 5:
            continue  # skips the "no listings found" empty-state row
        link = cells[0].find("a")
        if not link or not link.get("href"):
            continue
        listings.append(
            Listing(
                title=link.get_text(strip=True),
                url=link["href"],
                price=cells[1].get_text(strip=True),
                location=cells[2].get_text(strip=True),
                date_posted=cells[3].get_text(strip=True),
                site=cells[4].get_text(strip=True),
            )
        )
    return listings


_WYOMING_LOCATION_RE = re.compile(r",\s*WY\s*$", re.IGNORECASE)


def _is_wyoming(location: str) -> bool:
    return bool(_WYOMING_LOCATION_RE.search(location.strip()))


_DATE_POSTED_FORMATS = ("%B %d %Y", "%m/%d/%Y", "%m/%d/%y")


def _parse_listing_date(date_posted: str) -> dt.date | None:
    """Same parsing logic as parse_listing_date() in every companion
    repo's scraper/common.py, applied here to the already-rendered date
    text pulled back out of their published pages."""
    if not date_posted:
        return None
    cleaned = date_posted.replace(",", "").strip()
    for fmt in _DATE_POSTED_FORMATS:
        try:
            return dt.datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    return None


def collect_listings() -> list[Listing]:
    all_listings: list[Listing] = []
    for repo in SOURCE_SITES:
        url = f"https://taildraggers.github.io/{repo}/"
        page_html = fetch(url)
        if not page_html:
            continue
        rows = _parse_listing_rows(page_html)
        wyoming_rows = [row for row in rows if _is_wyoming(row.location)]
        print(f"  [{repo}] {len(rows)} listings, {len(wyoming_rows)} in Wyoming")
        all_listings.extend(wyoming_rows)

    seen = set()
    unique: list[Listing] = []
    for listing in all_listings:
        if listing.key() in seen:
            continue
        seen.add(listing.key())
        unique.append(listing)

    def _sort_key(listing: Listing):
        posted = _parse_listing_date(listing.date_posted)
        if posted is None:
            return (1, 0, listing.title.lower())
        return (0, -posted.toordinal(), listing.title.lower())

    unique.sort(key=_sort_key)
    return unique


def render_html(listings: list[Listing]) -> str:
    now = dt.datetime.now(dt.timezone.utc).strftime("%B %d, %Y %H:%M UTC")
    rows = []
    for listing in listings:
        rows.append(
            "\n        <tr>"
            f'<td><a href="{html.escape(listing.url)}" target="_blank" '
            f'rel="noopener noreferrer">{html.escape(listing.title)}</a></td>'
            f"<td>{html.escape(listing.price or 'Contact for price')}</td>"
            f"<td>{html.escape(listing.location or 'Unknown')}</td>"
            f"<td>{html.escape(listing.date_posted or '-')}</td>"
            f"<td>{html.escape(listing.site)}</td>"
            "</tr>"
        )

    rows_html = "".join(rows) if rows else (
        '\n        <tr><td colspan="5" class="empty">'
        "No Wyoming listings found in the latest run.</td></tr>"
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer">
<title>{html.escape(PAGE_TITLE)}</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
          margin: 0; padding: 1rem; background: #fff; color: #1a1a1a; }}
  h1 {{ font-size: 1.25rem; margin: 0 0 0.75rem; }}
  .updated {{ font-size: 0.8rem; color: #666; margin-bottom: 0.25rem; }}
  .disclaimer {{ font-size: 0.75rem; font-style: italic; color: #888; margin-bottom: 1rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
  th, td {{ text-align: left; padding: 0.5rem 0.6rem; border-bottom: 1px solid #e2e2e2; vertical-align: top; }}
  th {{ background: #f5f5f5; position: sticky; top: 0; }}
  tr:hover {{ background: #fafafa; }}
  a {{ color: #0b5fa5; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .empty {{ text-align: center; color: #888; padding: 1.5rem; }}
  @media (prefers-color-scheme: dark) {{
    body {{ background: #14161a; color: #e6e6e6; }}
    th {{ background: #1e2125; }}
    th, td {{ border-bottom-color: #2a2d31; }}
    tr:hover {{ background: #1a1c20; }}
    a {{ color: #6cb2f2; }}
    .updated {{ color: #9aa0a6; }}
    .disclaimer {{ color: #7a7f85; }}
  }}
  /* Below phone width, each row becomes a card: title + price on one line,
     location / date / site on a second line. Wider viewports (tablets,
     desktop embeds) keep the table exactly as it is above. */
  @media (max-width: 600px) {{
    table {{ display: block; }}
    thead {{ display: none; }}
    tbody {{ display: flex; flex-direction: column; gap: 0.6rem; }}
    tr {{ display: flex; flex-wrap: wrap; align-items: baseline; row-gap: 0.3rem;
          column-gap: 0.5rem; border: 1px solid #e2e2e2; border-radius: 8px;
          padding: 0.7rem 0.8rem; }}
    tr:hover {{ background: none; }}
    td {{ display: block; border: none; padding: 0; }}
    td:nth-child(1) {{ flex: 1 1 auto; min-width: 0; order: 1; font-weight: 600; font-size: 0.92rem; }}
    td:nth-child(2) {{ flex: 0 0 auto; order: 2; margin-left: auto; font-weight: 600;
                        font-variant-numeric: tabular-nums; white-space: nowrap; }}
    td:nth-child(3) {{ order: 3; flex-basis: 100%; font-size: 0.78rem; color: #666; }}
    td:nth-child(4) {{ order: 4; font-size: 0.78rem; color: #666; }}
    td:nth-child(4)::before {{ content: "\\00B7\\0020"; }}
    td:nth-child(5) {{ order: 5; font-size: 0.78rem; color: #666; }}
    td:nth-child(5)::before {{ content: "\\00B7\\0020"; }}
    td.empty {{ font-weight: 400; font-size: 0.9rem; }}
  }}
  @media (prefers-color-scheme: dark) and (max-width: 600px) {{
    tr {{ border-color: #2a2d31; }}
    td:nth-child(3), td:nth-child(4), td:nth-child(5) {{ color: #9aa0a6; }}
  }}
</style>
</head>
<body>
  <h1>{html.escape(PAGE_TITLE)}</h1>
  <div class="updated">Updated {html.escape(now)} &middot; {len(listings)} listing(s)</div>
  <div class="disclaimer">External listings are provided for informational purposes. Taildraggers.com is not affiliated with or endorsed by the originating listing sites. Listing information remains the responsibility of the original publisher. Clicking an external listing will take you to the source website.</div>
  <table>
    <thead>
      <tr><th>Title</th><th>Price</th><th>Location</th><th>Date Posted</th><th>Site Posted On</th></tr>
    </thead>
    <tbody>{rows_html}
    </tbody>
  </table>
<script>
  // Reports this page's rendered height to the parent window so an iframe
  // embed can size itself to fit, instead of using a fixed guessed height.
  // Requires a matching listener on the embedding page - see the repo README.
  (function () {{
    if (window.parent === window) return;
    var lastHeight = 0;
    function postHeight() {{
      var h = document.documentElement.scrollHeight;
      if (h !== lastHeight) {{
        lastHeight = h;
        window.parent.postMessage({{ type: "taildraggers:resize", height: h }}, "*");
      }}
    }}
    window.addEventListener("load", postHeight);
    window.addEventListener("resize", postHeight);
    if (window.ResizeObserver) {{
      new ResizeObserver(postHeight).observe(document.body);
    }}
    postHeight();
  }})();
</script>
</body>
</html>
"""


def main() -> None:
    listings = collect_listings()
    print(f"[main] total unique Wyoming listings: {len(listings)}")
    html_doc = render_html(listings)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_doc)
    print(f"[main] wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
