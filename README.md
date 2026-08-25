# alibuilds / resources

The resource hub behind the videos. Static site, no build step, served by GitHub Pages
at <https://alibuilds-ai.github.io/resources/>.

Videos never link to the hub root. Each video links to its own sheet under `guides/`.

## Layout

```
index.html                  hub index: table / gallery views + search
assets/css/main.css         the whole design system, one file
assets/icons/               tab icon, generated from the CSS tokens
guides/<slug>/index.html    one sheet per video
.nojekyll                   serve files verbatim, no Jekyll processing
```

## Icons

`assets/icons/make-icons.py` writes `icon.svg`, `icon-32.png` and `icon-192.png`
from the OKLCH values in `main.css`, so the tab icon can never drift from the
palette. Re-run it if those tokens change:

```bash
python3 assets/icons/make-icons.py --selfcheck   # assertions only, writes nothing
python3 assets/icons/make-icons.py               # regenerate all three
```

## Adding a guide

1. Copy an existing folder under `guides/` and rewrite the body.
2. Add one `<tr>` to `#rows` in `index.html`. That row is the single source of
   truth: the gallery cards and the search index are both built from it.
   - `data-status` — `published` or `queued`
   - `data-name`, `data-cat`, `data-tags`, `data-created`, `data-n`, `data-blurb`
   - `data-href` — omit for queued rows so the row is not a link
3. Give each `.tag` chip a `data-c`: `cyan` (agent mechanics), `blue` (planning
   artefacts), `violet` (tooling), `green` (platform), `amber` (cost), `rose`
   (craft). Leave it off and the chip falls back to the neutral style.
   `data-tags` on the row stays plain text and only feeds search.
4. Update the `sheet NN` labels in the hero dimension line.
5. Run the body text through the humanizer skill before publishing. No AI-tell
   prose ships: no bolded inline-header lists, no significance inflation,
   no em-dash chains, no rule-of-three padding.

## Local preview

```bash
python3 -m http.server 8777 --bind 127.0.0.1
```

Then open <http://127.0.0.1:8777/>.

## Design

Lane, tokens and constraints are in `PRODUCT.md` and the header comment of
`assets/css/main.css`. Committed dark, no light variant.
