#!/usr/bin/env python3
"""
Renders README.md to two local preview pages so the profile can be checked in a
browser on both GitHub canvases — the one thing a static SVG viewer cannot show you
(CLAUDE.md verification step 3).

  preview.html        GitHub light theme
  preview-dark.html   GitHub dark theme

Uses GitHub's own markdown renderer, so the output matches the real profile rather
than a local approximation. Needs network; no token required at this volume.

WHY TWO FILES RATHER THAN ONE PAGE WITH A TOGGLE. Both things that have to flip are
driven by prefers-color-scheme, which a button cannot fake: github-markdown-css
ships its themes behind that media query, and every art asset is chosen by a
<picture> source. An earlier single-page toggle silently left the markdown light
while swapping in the dark lockup, i.e. cream text on white. Two pages, each loading
the matching stylesheet and the matching art, cannot drift that way.

EVERY <picture> IS RESOLVED, NOT JUST THE FIRST. A headless browser renders with
prefers-color-scheme: light whatever the page background is, so any <picture> left
intact on the dark page silently serves its light asset. That produced a convincing
false alarm once — an on-dark Monoleaf logo that looked broken when the asset was
fine. So resolve_pictures() rewrites all of them, generically, by reading the
media="(prefers-color-scheme: dark)" source rather than hardcoding filenames.

Run:  python scripts/build_preview.py [source.md]

An optional path renders some other Markdown file instead of README.md — used to eyeball
what the release line will look like once scripts/update_release.py has filled it in,
without touching the real README.
"""
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
README = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "README.md")

CDN = "https://cdn.jsdelivr.net/npm/github-markdown-css@5"

# name, stylesheet, page background, is_dark, other page, its label
PAGES = [
    ("preview.html", f"{CDN}/github-markdown-light.css", "#f6f8fa",
     False, "preview-dark.html", "View dark"),
    ("preview-dark.html", f"{CDN}/github-markdown-dark.css", "#010409",
     True, "preview.html", "View light"),
]


def render(markdown: str) -> str:
    req = urllib.request.Request(
        "https://api.github.com/markdown",
        # "markdown", not "gfm": gfm is comment-field rendering, where a single
        # newline becomes a <br>. A README file is not rendered that way, and using
        # gfm here showed spurious line breaks the real profile does not have.
        data=json.dumps({"text": markdown, "mode": "markdown"}).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "profile-readme-preview"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def resolve_pictures(body: str, dark: bool) -> str:
    """Collapse every <picture> to the single source this page should show.

    Reads the dark source's srcset for the dark page and the <img> fallback for the
    light page, carrying alt and width across, so no asset filename is hardcoded here.
    """
    def one(match: re.Match) -> str:
        block = match.group(0)
        img = re.search(r"<img[^>]*>", block)
        inner = img.group(0) if img else ""

        src = None
        if dark:
            source = re.search(
                r'<source[^>]*prefers-color-scheme:\s*dark[^>]*>', block)
            if source:
                srcset = re.search(r'srcset="([^"]+)"', source.group(0))
                if srcset:
                    # first candidate, dropping any density descriptor
                    src = srcset.group(1).split(",")[0].strip().split()[0]
        if src is None:
            fallback = re.search(r'src="([^"]+)"', inner)
            if not fallback:
                print("warning: <picture> with no usable source; left as-is")
                return block
            src = fallback.group(1)

        attrs = [f'src="{src}"']
        for name in ("alt", "width"):
            found = re.search(rf'{name}="([^"]*)"', inner)
            if found:
                attrs.append(f'{name}="{found.group(1)}"')
        return "<img " + " ".join(attrs) + ">"

    out, n = re.subn(r"<picture>.*?</picture>", one, body, flags=re.S)
    print(f"  resolved {n} <picture> element(s) to their "
          f"{'dark' if dark else 'light'} source")
    if not n:
        print("  warning: no <picture> found — dark page may show light assets")
    return out


with open(README, encoding="utf-8") as fh:
    body = render(fh.read())

for filename, css, bg, is_dark, other, other_label in PAGES:
    print(filename)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>README preview — {filename}</title>
<link rel="stylesheet" href="{css}">
<style>
  body {{ background: {bg}; margin: 0; }}
  .bar {{ position: sticky; top: 0; z-index: 10; padding: 10px; text-align: center;
         font: 14px system-ui, sans-serif; background: rgba(110,118,129,0.12);
         backdrop-filter: blur(6px); }}
  .bar a {{ color: #4493f8; }}
  .markdown-body {{ box-sizing: border-box; max-width: 980px;
                    margin: 24px auto 60px; padding: 45px 32px; }}
</style>
</head>
<body>
  <div class="bar"><a href="{other}">{other_label} &rarr;</a></div>
  <article class="markdown-body">
{resolve_pictures(body, is_dark)}
  </article>
</body>
</html>
"""
    path = os.path.join(ROOT, filename)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("wrote", os.path.normpath(path), f"({len(html)} bytes)")
