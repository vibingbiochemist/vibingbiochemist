#!/usr/bin/env python3
"""
Regenerates assets/header-helix.svg — the spinning DNA double helix.

The helix appears to rotate about its long axis. Each column is pinned in x and
its two backbone dots oscillate vertically while swapping front/back (encoded via
radius + opacity), and the base-pair rungs collapse to zero length at crossings.
Nothing translates horizontally, so it reads as rotation in place rather than a
sideways slide.

Tunable parameters:
  T     seconds per full rotation (larger = slower spin)
  L     wavelength / twist tightness (smaller = more turns across the width)
  R     helix radius / vertical amplitude
  step  column spacing in px (smaller = denser, larger file)
Run:  python scripts/build_helix.py    (writes assets/header-helix.svg)
"""
import math, os

VW, VH = 1200, 130
mid, R = 65, 30.0
L = 260.0
T = 6.0
N = 18
step = 24
COL = "#2dd4bf"; BACK = "#14b8a6"

def fmt(v): return f"{v:.2f}"
keytimes = ";".join(fmt(s/N) for s in range(N+1))
cy_vals   = ";".join(fmt(mid + R*math.sin(2*math.pi*s/N)) for s in range(N+1))
def depth_t(s): return (math.cos(2*math.pi*s/N)+1)/2
r_vals    = ";".join(fmt(1.3 + 2.4*depth_t(s)) for s in range(N+1))
op_vals   = ";".join(fmt(0.25 + 0.75*depth_t(s)) for s in range(N+1))
rung_vals = ";".join(fmt(0.05 + 0.45*abs(math.sin(2*math.pi*s/N))) for s in range(N+1))

def anim(attr, vals, begin):
    return (f'<animate attributeName="{attr}" values="{vals}" keyTimes="{keytimes}" '
            f'dur="{T}s" begin="{begin:.3f}s" repeatCount="indefinite" calcMode="spline" '
            f'keySplines="{";".join(["0.42 0 0.58 1"]*N)}"/>')

rungs, dotsA, dotsB = [], [], []
x = step//2
while x <= VW - step//2:
    phase = (2*math.pi/L) * x
    bA = -(phase/(2*math.pi)) * T
    bB = bA - T/2
    y0  = mid + R*math.sin(phase)
    y0b = mid + R*math.sin(phase+math.pi)
    rungs.append(f'<line x1="{x}" x2="{x}" y1="{y0:.1f}" y2="{y0b:.1f}">'
                 f'{anim("y1", cy_vals, bA)}{anim("y2", cy_vals, bB)}'
                 f'<animate attributeName="opacity" values="{rung_vals}" keyTimes="{keytimes}" dur="{T}s" begin="{bA:.3f}s" repeatCount="indefinite"/></line>')
    dotsA.append(f'<circle cx="{x}" cy="{y0:.1f}" r="2" fill="{COL}">'
                 f'{anim("cy", cy_vals, bA)}{anim("r", r_vals, bA)}'
                 f'<animate attributeName="opacity" values="{op_vals}" keyTimes="{keytimes}" dur="{T}s" begin="{bA:.3f}s" repeatCount="indefinite"/></circle>')
    dotsB.append(f'<circle cx="{x}" cy="{y0b:.1f}" r="2" fill="{COL}">'
                 f'{anim("cy", cy_vals, bB)}{anim("r", r_vals, bB)}'
                 f'<animate attributeName="opacity" values="{op_vals}" keyTimes="{keytimes}" dur="{T}s" begin="{bB:.3f}s" repeatCount="indefinite"/></circle>')
    x += step

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {VH}" width="{VW}" height="{VH}" role="img" aria-label="Spinning DNA double helix">\n'
       f'  <g stroke="{BACK}" stroke-width="1.3" stroke-linecap="round">{"".join(rungs)}</g>\n'
       f'  <g>{"".join(dotsA)}{"".join(dotsB)}</g>\n</svg>\n')
out = os.path.join(os.path.dirname(__file__), "..", "assets", "header-helix.svg")
open(out, "w").write(svg)
print("wrote", os.path.normpath(out), f"({len(svg)} bytes)")
