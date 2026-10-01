# Directing My Digital Double

An illustrated artist production story about character replacement with MiniMax H3, a custom dispatcher, local and rented GPUs, and an agent crew.

The new artist draft is `site/index.html`; the earlier account is preserved in `site/production_article.html`. Actual comparison videos, frame grabs and character references are included. No ComfyUI source, credentials, job databases or internal machine paths are included.

## Cloudflare Pages

Connect this repository through Workers & Pages → Create → Pages → Import an existing Git repository.

- Production branch: `main`
- Framework: None
- Build command: `exit 0`
- Build output directory: `site`

The site is static HTML and requires no packages or build service. Media is kept below the 25 MiB per-file Pages limit. Pushes to main deploy after the Git integration is connected.

## Local preview

Run `python -m http.server 8766 --directory site` and visit http://localhost:8766.

The source performance is used as context for this character-replacement experiment. No ownership of the original music or footage is claimed.
