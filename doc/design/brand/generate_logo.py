"""Build the LightChat logo files in static/brand/ from vector geometry.

Usage: python generate_logo.py <BarlowSemiCondensed-SemiBold.ttf> <out-dir>
Requires fontTools. The wordmark is outlined, so the SVGs need no font.
Font: Barlow Semi Condensed SemiBold, SIL OFL 1.1, google/fonts@89f5431ff0db.
"""
import os
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

TTF, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

# Symbol, 24-unit grid. Regular optical size (>= 32 px) and small (16-32 px).
SIZES = {
    "regular": dict(d="M9 18H17A5 5 0 0 0 22 13V7A5 5 0 0 0 17 2H7A5 5 0 0 0 2 7V12", w=2.5, dot=(4.75, 19.25, 2.75)),
    "small": dict(d="M9.6 18.2H16.8A5 5 0 0 0 21.8 13.2V7A4.8 4.8 0 0 0 17 2.2H7A4.8 4.8 0 0 0 2.2 7V11.4", w=3.4, dot=(4.9, 19.1, 3.6)),
}
COLORWAYS = {  # ink, light
    "signal": ("#1B1F1D", "#C27400"),       # on light grounds
    "signal-dark": ("#E7EAE6", "#F0A93A"),  # on dark grounds
    "black": ("#000000", "#000000"),
    "white": ("#FFFFFF", "#FFFFFF"),
}


def symbol(size, ink, light):
    s = SIZES[size]
    cx, cy, r = s["dot"]
    return (f'<path d="{s["d"]}" fill="none" stroke="{ink}" stroke-width="{s["w"]}" '
            f'stroke-linecap="round" stroke-linejoin="round"/><circle cx="{cx}" cy="{cy}" r="{r}" fill="{light}"/>')


font = TTFont(TTF)
gs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
scale = 13.0 / font["OS/2"].sCapHeight   # cap height 13 units
track = 0.012 * font["head"].unitsPerEm
baseline, gap = 10 + 13.0 / 2, 8.0      # cap height centred on the bubble body


def wordmark(x0):
    pen, x = SVGPathPen(gs), 0
    for ch in "LightChat":
        g = cmap[ord(ch)]
        gs[g].draw(TransformPen(pen, (scale, 0, 0, -scale, x0 + x * scale, baseline)))
        x += hmtx[g][0] + track
    return pen.getCommands(), (x - track) * scale


word_d, word_w = wordmark(24 + gap)
lock_w = round(24 + gap + word_w, 2)
HEAD = 'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="LightChat"'

for name, (ink, light) in COLORWAYS.items():
    for size in SIZES:
        suffix = "" if size == "regular" else "-small"
        with open(f"{OUT}/lightchat-symbol{suffix}-{name}.svg", "w") as f:
            f.write(f'<svg {HEAD} viewBox="0 0 24 24" width="24" height="24"><title>LightChat</title>{symbol(size, ink, light)}</svg>\n')
    with open(f"{OUT}/lightchat-lockup-{name}.svg", "w") as f:
        f.write(f'<svg {HEAD} viewBox="0 0 {lock_w} 24" width="{lock_w}" height="24"><title>LightChat</title>'
                f'{symbol("regular", ink, light)}<path d="{word_d}" fill="{ink}"/></svg>\n')

# Favicon: small optical size, follows the browser/OS theme.
with open(f"{OUT}/favicon.svg", "w") as f:
    f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><style>'
            '.i{stroke:#1B1F1D}.l{fill:#C27400}@media (prefers-color-scheme:dark){.i{stroke:#E7EAE6}.l{fill:#F0A93A}}'
            f'</style><path class="i" d="{SIZES["small"]["d"]}" fill="none" stroke-width="{SIZES["small"]["w"]}" '
            'stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle class="l" cx="{SIZES["small"]["dot"][0]}" cy="{SIZES["small"]["dot"][1]}" r="{SIZES["small"]["dot"][2]}"/></svg>\n')
print("lockup viewBox width", lock_w)
