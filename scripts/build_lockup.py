#!/usr/bin/env python3
"""
Regenerates the profile lockup: a still double-helix mark beside the name.

Writes two files, because GitHub serves the README on a white and on a near-black
canvas and an <img> cannot carry a media query:

  assets/lockup.svg        ink on white    (GitHub light theme)
  assets/lockup-dark.svg   cream on #0d1117 (GitHub dark theme)

README.md picks between them with <picture><source media="(prefers-color-scheme: dark)">.

Design rules (kept in step with CLAUDE.md):
  - Still, not animated. The mark is a logo, not a banner.
  - Gold is the only accent, and it is a fill/rule colour, never text: #E8A33D on
    white is 1.9:1. The backbones are gold because they are a shape; the name and
    the base pairs are ink.
  - Text stays live <text>, not outlines, so it remains selectable and legible at
    any zoom. It is set in a monospace stack that degrades cleanly (IBM Plex Mono
    where present, otherwise the platform's mono face) — the lockup is left-anchored
    and the rule is drawn past the longest plausible setting, so a wider or narrower
    fallback shifts nothing.

WHY THE MARK IS DRAWN IN FOUR LAYERS. Two sine strands alone do not read as a
helix; they read as a stack of lozenges, because nothing says which strand is in
front. So each strand is split at its crossings into front and back runs by the
sign of cos(phase): back runs are drawn dimmed, then the base pairs, then the front
runs get a casing stroke in the page background colour before the gold, which
punches out whatever passes behind them. That casing is why the file is
theme-specific rather than one transparent asset — opened on its own, against no
background, the casing shows as opaque strokes. It is built for the README.

Tunables: NAME, TURNS (twist), AMP (radius), MARK_H (mark height), RUNGS (density).
Run:  python scripts/build_lockup.py
"""
import math
import os

NAME = "MARTIN SCHWALM"

# --- canvas -----------------------------------------------------------------
VW, VH = 416, 116

# --- mark geometry ----------------------------------------------------------
MARK_CX = 26.0        # centre of the helix axis
MARK_TOP = 14.0
MARK_H = 88.0         # axis length
AMP = 16.0            # helix radius
TURNS = 2.0           # full twists across MARK_H
RUNGS = 11            # base pairs attempted; those near a crossing are dropped
SAMPLE = 1.0          # px between backbone samples
SEAM = 0.08           # front/back overlap, so the weave has no hairline gaps

# --- type -------------------------------------------------------------------
TEXT_X = 84.0
BASELINE = 62.0
FONT_SIZE = 27.0
TRACKING = 4.2
RULE_Y = 82.0
RULE_X2 = 400.0

MONO = ("&apos;IBM Plex Mono&apos;, ui-monospace, SFMono-Regular, Menlo, "
        "Consolas, &apos;Liberation Mono&apos;, monospace")

# Monoleaf palette. Gold is shared; ink and the casing flip per theme.
GOLD = "#E8A33D"
THEMES = {
    "lockup.svg":      {"ink": "#23252A", "rung": "#23252A", "bg": "#FFFFFF"},
    "lockup-dark.svg": {"ink": "#F5F1E8", "rung": "#B4B1A8", "bg": "#0D1117"},
}


def phase(y: float) -> float:
    """Helix phase at height y, measured from the top of the mark."""
    return 2 * math.pi * TURNS * (y - MARK_TOP) / MARK_H


def runs(offset: float, front: bool) -> list[str]:
    """The parts of one strand that face the viewer (or away), as SVG paths.

    `offset` is 0 or pi to select the strand. Depth is cos(phase): a point is in
    front when it is positive. SEAM widens each run slightly past its crossing so
    consecutive runs overlap instead of leaving a gap.
    """
    want = 1.0 if front else -1.0
    out, cur = [], []
    steps = int(MARK_H / SAMPLE)
    for i in range(steps + 1):
        y = MARK_TOP + MARK_H * i / steps
        ph = phase(y) + offset
        if math.cos(ph) * want > -SEAM:
            cur.append((MARK_CX + AMP * math.sin(ph), y))
        elif len(cur) > 1:
            out.append(cur)
            cur = []
        else:
            cur = []
    if len(cur) > 1:
        out.append(cur)
    return [f"M{p[0][0]:.2f},{p[0][1]:.2f}" + "".join(f"L{x:.2f},{y:.2f}" for x, y in p[1:])
            for p in out]


def rungs() -> str:
    """Base pairs, skipped near the crossings where they would collapse to a dot."""
    out = []
    for i in range(RUNGS):
        y = MARK_TOP + MARK_H * (i + 0.5) / RUNGS
        dx = AMP * math.sin(phase(y))
        if abs(dx) < AMP * 0.34:      # too close to a crossing to read
            continue
        out.append(f'<line x1="{MARK_CX - dx:.2f}" y1="{y:.2f}" '
                   f'x2="{MARK_CX + dx:.2f}" y2="{y:.2f}"/>')
    return "".join(out)


def paths(front: bool) -> str:
    both = runs(0.0, front) + runs(math.pi, front)
    return "".join(f'<path d="{d}"/>' for d in both)


def build(ink: str, rung: str, bg: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {VH}" width="{VW}" height="{VH}" role="img" aria-label="{NAME.title()}">
  <title>{NAME.title()}</title>

  <!-- mark, back to front: far strand, base pairs, then the near strand with a
       background-coloured casing that occludes whatever passes behind it -->
  <g fill="none" stroke-linecap="round">
    <g stroke="{GOLD}" stroke-width="4.6" opacity="0.35">{paths(False)}</g>
    <g stroke="{rung}" stroke-width="1.9" opacity="0.7">{rungs()}</g>
    <g stroke="{bg}" stroke-width="9">{paths(True)}</g>
    <g stroke="{GOLD}" stroke-width="5">{paths(True)}</g>
  </g>

  <!-- wordmark -->
  <text x="{TEXT_X}" y="{BASELINE}" fill="{ink}" font-family="{MONO}"
        font-size="{FONT_SIZE}" letter-spacing="{TRACKING}">{NAME}</text>

  <!-- the one accent rule -->
  <line x1="{TEXT_X}" y1="{RULE_Y}" x2="{RULE_X2}" y2="{RULE_Y}" stroke="{GOLD}" stroke-width="2"/>
</svg>
"""


assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
for filename, theme in THEMES.items():
    path = os.path.join(assets, filename)
    svg = build(theme["ink"], theme["rung"], theme["bg"])
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print("wrote", os.path.normpath(path), f"({len(svg)} bytes)")
