# Redirect stubs only

The resources site moved to **https://alibuilds.blog/resources/**.

This branch is what GitHub Pages publishes: one stub per old URL, each
canonical + meta-refresh + JS redirect to its new home, so links in already
published video captions keep working. `404.html` catches anything else.

The real site lives on `main` and deploys to the box with `scripts/deploy.sh`.
Add a guide there; only add a stub here if the old URL was ever published.
