# CLAUDE.md — maintenance guide for this profile repository

This repo is Martin Schwalm's GitHub **profile README** (it renders on the profile
because the repo is named after the GitHub username). Use this file as context when
updating anything here.

## Hard rules

- **Public information only.** Nothing about current-employer internal projects,
  unpublished manuscripts, regulatory/NDA work, internal tools, or named colleagues
  in an internal context. If unsure whether something is public, leave it out.
- **No fabricated citations or DOIs.** Every publication link must resolve to a real,
  verified article. If a DOI can't be verified, list the citation without a link
  rather than guessing.
- **No em dashes in README.md.** Martin's explicit instruction. Use a colon, a comma
  or a semicolon. This applies to the HTML comments too, so a future edit copying the
  house style does not reintroduce one. En dashes stay: they are correct in page
  ranges (`1032–1041`) and compounds (`ubiquitin–proteasome`), and are a different
  character (U+2013, not U+2014).
- **Aesthetic:** minimal and professional, modelled on the Monoleaf project's
  ink-on-paper design language. No emojis. No shield/badge images. No animation.
  Imagery is limited to the lockup, project brand marks, and product screenshots —
  nothing decorative, and no GitHub stats/streak cards.

## Design system

Borrowed wholesale from Monoleaf, so Martin's profile and his flagship project read
as one identity.

- Palette: ink `#23252A`, cream (on dark) `#F5F1E8`, muted cream `#B4B1A8`.
  **Gold `#E8A33D` is the only accent, and there must not be a second one.**
- Gold is a fill and rule colour, never a text colour: `#E8A33D` on white is 1.9:1.
  The lockup's backbones and its rule are gold; the name is ink.
- Type (inside SVGs): a monospace stack led by IBM Plex Mono, letter-spaced caps.
  Web fonts cannot load in a GitHub-hosted SVG, so the stack must degrade to the
  platform mono face — keep text left-anchored so a narrower fallback shifts nothing.
- **Still, not animated.** The mark is a logo, not a banner. The previous spinning
  helix header and molecular footer were deliberately removed; do not reinstate
  motion without being asked.
- Body typography is whatever GitHub renders. Markdown cannot set fonts, so do not
  try — `##` headings already draw the hairline rule that carries the aesthetic.

## File map

- `README.md` — the profile. Lockup, one-line identity, links, publications,
  open work, prepared featured-repos block (commented).
- `assets/lockup.svg`, `assets/lockup-dark.svg` — the name beside a still double
  helix, one per GitHub canvas. Generated; do not hand-edit.
- `assets/monoleaf-logo.svg`, `assets/monoleaf-logo-dark.svg`,
  `assets/monoleaf-showcase.png` — **copies** of `Monoleaf/branding/monoleaf-logo.svg`,
  `…-logo-ondark.svg` and `Monoleaf/docs/screenshots/monoleaf-showcase.png`. Refresh by
  re-copying from that repo when Monoleaf's branding or UI changes; do not edit them
  here, or the two will silently diverge.
- `scripts/build_lockup.py` — regenerates both lockups; see its header for tunables
  (`TURNS` twist, `AMP` radius, `MARK_H` height, `RUNGS` density) and for why the
  mark is drawn in four layers. Run `python scripts/build_lockup.py`.
- `scripts/build_preview.py` — renders README.md to `preview.html` /
  `preview-dark.html` via GitHub's own markdown API, for browser checking. The
  preview files are gitignored build output. Takes an optional source path, so you
  can preview a variant without touching README.md.
- `scripts/update_release.py` + `.github/workflows/monoleaf-release.yml` — fill the
  Monoleaf version in from the Releases API, daily and on `workflow_dispatch`. See
  "Monoleaf release line" below.

Two lockups exist because an `<img>` cannot carry a media query and the mark's
weave uses a background-coloured casing stroke to occlude the strand behind it —
so each file is pinned to one canvas (`#FFFFFF` / `#0D1117`). Opened on its own,
against no background, that casing shows as opaque strokes; the asset is built for
the README, not for standalone viewing.

## Common updates

- **New publication:** add to the `Selected publications` list, keep the surname
  **Schwalm MP** bolded, verify the DOI by web search before linking, and prune the
  list back to ~7 strongest if it grows.
- **Featured repositories:** uncomment the prepared block in README.md and add one
  line per public repo. Check the URL resolves first — as of 2026-08-02 the Monoleaf
  repo is **private** (both `vibingbiochemist/Monoleaf` and `…/Monoleaf_beta` return
  404), so it must not be linked yet, and neither may anything else unverified.
- **Monoleaf release line:** never hand-edit it. It sits between
  `<!-- MONOLEAF_RELEASE:START -->` and `<!-- MONOLEAF_RELEASE:END -->` on the
  Monoleaf links row and is written by `scripts/update_release.py`. Empty markers
  render as nothing, which is the correct pre-release state — do not substitute
  placeholder text. The script rewrites only on a confirmed HTTP 200, so a private
  repo, an unpublished release, a rate limit or a network failure all leave the file
  untouched rather than blanking a good line. Two things gate it going live: the
  `vibingbiochemist/Monoleaf` repo must have a published release, and while that repo
  is private the profile repo needs a `MONOLEAF_TOKEN` secret (a fine-grained PAT with
  Contents:read on Monoleaf) — a repo's own `GITHUB_TOKEN` cannot read a *different*
  private repo. Delete the secret once Monoleaf is public.

- **Deliberately dead links.** As of 2026-08-02 `monoleaf.org` has no DNS record and
  `github.com/vibingbiochemist/Monoleaf` 404s (still private). Martin asked for both
  to be linked anyway, ahead of launch — this is a known, accepted state, not an
  oversight to "fix" by removing them. Do re-check them before any other push.

- **Google Scholar metrics (h-index / i10 / citations):** these CANNOT be fetched
  reliably — Google Scholar has no public API and blocks automated scraping. If a
  metrics line is wanted, add it as a static, manually-updated value with an
  "as of <date>" note; do not wire a live scraper.
- **The lockup:** after changing `build_lockup.py`, regenerate and *look at it* —
  render it against both canvases, do not just check the SVG parses. Two sine strands
  without the front/back weave read as a stack of lozenges rather than a helix, and
  that failure is invisible in the source.

## Verification checklist before pushing

1. Every DOI link resolves. Publisher sites (ACS, RSC) 403 automated requests even
   when the DOI is fine — confirm those against `api.crossref.org/works/<doi>`
   instead of treating a 403 as a dead link.
2. No non-public content crept in.
3. `python scripts/build_preview.py`, then open `preview.html` and `preview-dark.html`
   and read both. GitHub serves the profile on a white and a near-black canvas. Check
   the run says it resolved **every** `<picture>` — a headless or default-light browser
   serves the light asset for any it missed, which once looked exactly like a broken
   on-dark logo when the asset was fine.
4. Repo name still matches the GitHub username.
