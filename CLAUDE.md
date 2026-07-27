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
- **Aesthetic:** minimal and professional. No emojis. No colored shield/badge images.
  Custom monochrome-teal SVG only.

## Design system

- Palette: base teal `#14b8a6`, mid `#2dd4bf`, bright `#5eead4`; dark reference bg `#14181d`.
- Type (inside SVGs): Georgia serif for display, Arial for letter-spaced caps.
- All SVG headers/footers are transparent and full-width (`viewBox 0 0 1200 130`).

## File map

- `README.md` — the profile. Header helix, academic-link icons, focus, publications,
  prepared featured-repos block (commented), footer.
- `assets/header-helix.svg` — spinning double helix (animated, SMIL). Generated.
- `assets/footer.svg` — molecular-field animation (aromatic rings + drifting particles).
- `assets/icons/{linkedin,orcid,scholar}.svg` — teal circular link badges.
- `scripts/build_helix.py` — regenerates the helix; see its header for tunables
  (`T` speed, `L` twist, `R` radius, `step` density). Run `python scripts/build_helix.py`.

## Common updates

- **New publication:** add to the `Selected publications` list, keep the surname
  **Schwalm MP** bolded, verify the DOI by web search before linking, and prune the
  list back to ~7 strongest if it grows.
- **Featured repositories:** uncomment the prepared block in README.md and add one
  line per public repo.
- **Google Scholar metrics (h-index / i10 / citations):** these CANNOT be fetched
  reliably — Google Scholar has no public API and blocks automated scraping. If a
  metrics line is wanted, add it as a static, manually-updated value with an
  "as of <date>" note; do not wire a live scraper.
- **Animations:** after editing an SVG, always open it in a browser to confirm motion
  and pacing. Static renderers only show the resting frame.

## Verification checklist before pushing

1. Every DOI link resolves.
2. No non-public content crept in.
3. Header, footer, and icons render in a browser (light and dark GitHub themes).
4. Repo name still matches the GitHub username.
