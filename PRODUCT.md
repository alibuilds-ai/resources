# alibuilds / resources

Static site at `alibuilds-ai.github.io/resources`. One page per video that has a
setup worth writing down. Ali links the specific page from the video's caption or
bio, never the hub root.

**Register: brand.** The design is the product. There is no app, no login, no data.
Every page is a document.

## Who it is for

Someone who just paused a short vertical video on Instagram, TikTok or YouTube,
tapped a link, and wants the method behind what they watched. Phone, one hand,
often at night, high intent and very low patience. A real technical slice reads
these too, so the writing carries actual specifics (the model, the number, the
limitation) rather than motivational filler.

## Non-goals

- No email capture, no gated download, no course funnel, no newsletter box.
- No CMS, no build step, no framework. Hand-written HTML per guide.
- No comments. Feedback goes to the video the page came from.
- No light mode. Ali asked for dark.

## Content shape

- Hub index: masthead, one statement, a list of guides, footer.
- Guide page: title, standfirst, prose with h2 sections, an ordered procedure,
  occasional inline SVG diagram, a callout or two, a footer back to the video.

## Constraints

- GitHub Pages, static files only, `.nojekyll`.
- Must be fast on a phone over mobile data. No JS beyond what an effect needs.
- Google Fonts is the only permitted external host.
