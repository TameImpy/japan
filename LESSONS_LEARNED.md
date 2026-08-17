# Lessons Learned

Running notes on the non-obvious things hit while building and deploying this page, so future-me (or anyone
picking it up) doesn't rediscover them. Newest at the bottom.

## 2026-08-15 — Fonts can't come from a CDN inside an Artifact; subset and inline them
**Problem:** The claude.ai Artifact viewer runs a strict Content-Security-Policy: no requests to any outside host, so
`<link href="fonts.googleapis.com…">` silently fails and everything falls back to system fonts.
**Fix:** Downloaded the TTFs once, then used `fonttools` (`pyftsubset` via `build.py`) to cut each font down to only the
characters actually used in the page (scan the HTML text, plus kana + basic Latin), saved as WOFF2 and inlined as
`data:font/woff2;base64,…` in `@font-face`. 27 MB of TTF became ~700 KB. The Japanese font (Shippori Mincho) is the
big one — subsetting it to the ~200 kanji on the page is what makes this feasible.
**Gotcha:** the Google Fonts CSS endpoint returns TTF (not WOFF2) unless you send a modern browser User-Agent.

## 2026-08-15 — Local `http.server` port was already taken by another project
`python3 -m http.server 8765` "started" but served a different project's files (an older server on the same port).
Always `curl` the exact file after starting, and pick an unusual port (`8931`) or check `lsof -i :PORT` first.

## 2026-08-15 — Chrome extension screenshots lie about sticky/scrolled layouts
While reviewing the page through the Claude-in-Chrome extension, screenshots after scrolling showed the sticky
left rail "scrolling away" and blank areas below — but `getBoundingClientRect()` said the layout was correct.
The capture is stale for composited/sticky layers. **Verify layout via DOM measurements or headless Chrome
(`Google Chrome --headless=new --screenshot --window-size=W,H`)**, not extension screenshots, when sticky is involved.

## 2026-08-15 — Headless Chrome won't go narrower than ~500 px
`--window-size=420,…` renders as if wider and then crops, so mobile layouts look broken when they aren't.
For narrow-viewport checks, load the page in a 400 px `<iframe>` inside a test page and inspect from there.

## 2026-08-15 — Grid `1fr` is `minmax(auto,1fr)`; use `minmax(0,1fr)` for mobile columns
Mobile overflow: the day grids resolved to 514 px in a 400 px viewport because `1fr` won't shrink below the
column's min-content. Every single-column mobile override now uses `grid-template-columns: minmax(0,1fr)`.

## 2026-08-15 — The "1 px gap on a coloured background" grid-border trick leaks
Using `gap:1px; background:var(--line)` to draw cell borders shows solid blocks wherever a row is incomplete
(8 items in a 5-column grid). Switched to real per-cell `border-right/bottom` plus `border-top/left` on the container.

## 2026-08-17 — Photos: also blocked by CSP, so they're embedded too (and licensed)
Images from other domains don't load in the Artifact either. Sourced CC-licensed photos through the Wikimedia
Commons API (`commons.py` searches, `fetch.py` downloads via `Special:FilePath/<name>?width=1400`), resized/compressed
with Pillow, and inlined as base64 JPEGs (~3.4 MB for 22 photos; artifact limit is 16 MB). CC BY / BY-SA require
attribution — every `<figcaption>` carries photographer, licence and a link back (`src/photo-credits.json`).
**Gotcha:** the API's `thumburl` is fixed at the width you asked for; string-replacing `400px-`→`1400px-` in it doesn't
work. Use `Special:FilePath` with `?width=`. Also throttle requests (~0.7 s) or Commons drops connections.

## 2026-08-17 — `aspect-ratio` on `<img>` is ignored if you also set the `height` attribute
Wrote `<img width height>` for layout stability and `.plate img{aspect-ratio:21/9; object-fit:cover}` — the
attribute height won and the images rendered at natural ratio. Adding `height:auto` in CSS lets `aspect-ratio` take over.

## 2026-08-17 — GitHub Pages: a green build can still 404 for a couple of minutes
The "pages build and deployment" workflow reported success while `https://tameimpy.github.io/japan/` returned 404 for
~2 more minutes — CDN propagation on first deploy. Poll with `curl -o /dev/null -w "%{http_code}"`; don't re-trigger.
`.nojekyll` in the root skips the Jekyll build entirely (we don't need it; the site is one self-contained file).

## How to rebuild the page
`src/momiji.src.html` is the editable source (fonts and images appear as `/*FONTS*/` and `<!--IMG:name|caption-->` /
`<!--FIG:name|caption-->` placeholders). `src/build.py` expects a `fonts/` folder of TTFs and `img/embed.json`
(produced by `fetch.py`) alongside it, and writes the finished `momiji.html` → copy to `index.html`, commit, push.

## 2026-08-17 — Currency conversion is a build step, not hand-edits
Sterling equivalents (~£) are generated in `build.py` from a single `RATE` constant (215 JPY/GBP, ECB mid-Aug 2026)
by regex over **text nodes only** (split the HTML on tags first, so `¥` inside attributes/captions-in-comments isn't
touched). Ranges (`¥900–1,100`) are handled; numbers use `\d{1,3}(?:,\d{3})*` so a trailing comma in prose isn't
swallowed. To refresh the rate before the trip: change `RATE`, rebuild, push. The footer states the rate used.

## 2026-08-17 — Research surprises worth remembering for any November Japan trip
November's Grand Sumo tournament is in Fukuoka (not Tokyo) and Tokyo stables travel there, so "watch morning
practice" is a non-starter that month; the Nintendo Museum lottery for a given month opens three months ahead
(August for November); Miraikan is shut Oct 2026–Apr 2027; Japan's tax-free shopping switches to refund-at-airport
on 1 Nov 2026. Check event calendars, not just opening hours.

## 2026-08-17 — Build inputs (fonts/, img/) aren't in the repo
`build.py` needs `src/fonts/*.ttf` and `src/img/embed.json`, but those were never committed (~30 MB of assets).
They live in an old session scratchpad (`/private/tmp/claude-501/-Users-matthewrance-Documents/d14f…/scratchpad/`).
**Fix used:** symlink `src/fonts` and `src/img` to that folder for the build, then remove the symlinks. If that
scratchpad is ever cleaned, re-run `fetch.py` (images) and re-download the Google Fonts TTFs (see the 2026-08-15 note).
Also: the shell cwd persists between commands, so `cd src && …` fails if you're already inside `src` — use absolute paths.
