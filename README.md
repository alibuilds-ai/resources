# alibuilds / resources

The resource hub behind the videos. Static site, no build step, self-hosted at
<https://alibuilds.blog/resources/>.

The old GitHub Pages host (`alibuilds-ai.github.io/resources/`) now serves redirect
stubs from the `gh-pages` branch so links in published captions keep working. Never
publish a new video against that host.

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
5. Every tool, repo, model or service named in a sheet gets a direct link the
   first time it appears, and always in the `Repo` / source column of a
   `table.spec`. Link the whole cell (`<a><code>owner/repo</code></a>`), point
   at the exact page rather than the org root (a plugin links to its own
   subdirectory), and curl each URL for a 200 before publishing. A reader who
   wants the thing should never have to search for it.
6. Run the body text through the humanizer skill before publishing. No AI-tell
   prose ships: no bolded inline-header lists, no significance inflation,
   no em-dash chains, no rule-of-three padding.
7. Commit, then `./scripts/deploy.sh`. Nothing is live until you do — pushing to
   GitHub does not deploy.

## Local preview

```bash
python3 -m http.server 8777 --bind 127.0.0.1
```

Then open <http://127.0.0.1:8777/>.

## Deploying

```bash
./scripts/deploy.sh            # ship to the box + verify the live URLs
./scripts/deploy.sh --verify   # verify only
```

Manual and deliberate: tar over SSH into a read-only bind mount on `warmline-box`,
no build, no CI credentials on the box. Rollback is `git checkout <sha> &&
./scripts/deploy.sh`.

The site runs as an `nginx-unprivileged` container behind the box's Traefik, with
Cloudflare in front. `deploy/` holds the three server-side files (nginx config,
Traefik routers, container run-config) — edit them there, not on the box, then
reinstall. Changing `deploy/nginx.conf` needs a container restart
(`/usr/local/sbin/redeploy-resources.sh`), not just an `nginx -s reload`: the config
is a bind-mounted single file, so replacing it swaps the inode out from under the
running container.

`alibuilds.blog/` currently 302s to `/resources/`. When the home page is built it
takes the Traefik priority-1 router and `/resources` is untouched.

## Design

Lane, tokens and constraints are in `PRODUCT.md` and the header comment of
`assets/css/main.css`. Committed dark, no light variant.
