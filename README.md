# alibuilds / resources

The resource hub behind the videos. Static site, no build step, served by GitHub Pages
at <https://alibuilds-ai.github.io/resources/>.

Videos never link to the hub root. Each video links to its own sheet under `guides/`.

## Layout

```
index.html                  hub index: table / gallery views + search
assets/css/main.css         the whole design system, one file
guides/<slug>/index.html    one sheet per video
.nojekyll                   serve files verbatim, no Jekyll processing
```

## Adding a guide

1. Copy an existing folder under `guides/` and rewrite the body.
2. Add one `<tr>` to `#rows` in `index.html`. That row is the single source of
   truth: the gallery cards and the search index are both built from it.
   - `data-status` — `published` or `queued`
   - `data-name`, `data-cat`, `data-tags`, `data-created`, `data-n`, `data-blurb`
   - `data-href` — omit for queued rows so the row is not a link
3. Update the `sheet NN` labels in the hero dimension line.

## Local preview

```bash
python3 -m http.server 8777 --bind 127.0.0.1
```

Then open <http://127.0.0.1:8777/>.

## Design

Lane, tokens and constraints are in `PRODUCT.md` and the header comment of
`assets/css/main.css`. Committed dark, no light variant.
