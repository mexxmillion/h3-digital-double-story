# Directing My Digital Double

An illustrated artist production story about character replacement with MiniMax H3, a custom dispatcher, local and rented GPUs, and an agent crew.

The casual visual breakdown (vertical film + chapters) is `site/breakdown/index.html`, with its media in `site/media/v3/`. The artist draft is `site/index.html`; the earlier account is preserved in `site/production_article.html`. Actual comparison videos, frame grabs and character references are included. No ComfyUI source, credentials, job databases or internal machine paths are included.

## GitHub Pages

The dance case study is `site/dance/index.html`: exact-cut auditing, rejected and repaired takes, native pose anchors, target-only inversion/depth tests, and the rejected protected-overlap experiment. Public media, frame/audio verification, and a sanitized first-take workflow/input bundle are included. Article: https://mexxmillion.github.io/h3-digital-double-story/dance/

To rebuild its public assets from the local experiment outputs, run `python tools/build_dance_media.py /path/to/ComfyUI`. This requires FFmpeg/FFprobe and the recorded source jobs; it exports only selected media and sanitized workflow assets. Public full-video audio and frame counts are checked during export.

Public site: https://mexxmillion.github.io/h3-digital-double-story/

Pages publishes the root of `gh-pages`. The authoring files remain in `site/` on `main`. After an update, commit and push main, then publish with `git subtree push --prefix site origin gh-pages`.

## Cloudflare Pages alternative

Connect this repository through Workers & Pages → Create → Pages → Import an existing Git repository.

- Production branch: `main`
- Framework: None
- Build command: `exit 0`
- Build output directory: `site`

The site is static HTML and requires no packages or build service. Media is kept below the 25 MiB per-file Pages limit. Pushes to main deploy after the Git integration is connected.

## Local preview

Run `python -m http.server 8766 --directory site` and visit http://localhost:8766.

The source performance is used as context for this character-replacement experiment. No ownership of the original music or footage is claimed.
