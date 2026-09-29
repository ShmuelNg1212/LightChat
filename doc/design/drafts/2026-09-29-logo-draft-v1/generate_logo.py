"""Draft LightChat logo: symbol + wordmark, pure vector geometry.

Symbol (24-unit grid): an open speech bubble whose tail is a single solid
dot, the meter's pulse light. Wordmark: "LightChat" outlined from
Barlow Semi Condensed SemiBold (SIL OFL 1.1) so the SVG needs no font.
"""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import sys, os

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

# --- Symbol --------------------------------------------------------------
STROKE = 2.5
BUBBLE = ("M9 18H17A5 5 0 0 0 22 13V7A5 5 0 0 0 17 2H7A5 5 0 0 0 2 7V12")
DOT = (4.75, 19.25, 2.75)  # cx, cy, r: the pulse light sits where a tail would be

def symbol_group(ink="currentColor", light=None):
    light = light or ink
    cx, cy, r = DOT
    return (f'<path d="{BUBBLE}" fill="none" stroke="{ink}" stroke-width="{STROKE}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{light}"/>')

def symbol_svg(ink="currentColor", light=None, title=True):
    t = '<title>LightChat</title>' if title else ''
    a11y = ' role="img" aria-label="LightChat"' if title else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"'
            f'{a11y}>{t}{symbol_group(ink, light)}</svg>\n')

# --- Wordmark ------------------------------------------------------------
font = TTFont(os.path.join(os.path.dirname(__file__), "fonts/ofl_barlowsemicondensed_BarlowSemiCondensed-SemiBold.ttf"))
gs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
upm = font["head"].unitsPerEm
cap = font["OS/2"].sCapHeight
TEXT = "LightChat"
CAP_UNITS = 13.0            # wordmark cap height in symbol units
scale = CAP_UNITS / cap
TRACK = 0.012 * upm         # slight positive tracking for small sizes

def wordmark_path(x0, baseline):
    pen = SVGPathPen(gs)
    x = 0
    for ch in TEXT:
        g = cmap[ord(ch)]
        tpen = TransformPen(pen, (scale, 0, 0, -scale, x0 + x * scale, baseline))
        gs[g].draw(tpen)
        x += hmtx[g][0] + TRACK
    return pen.getCommands(), (x - TRACK) * scale

# Lockup: symbol 24 tall; cap height 13 centred on the bubble body (y 2..18 -> centre 10)
baseline = 10 + CAP_UNITS / 2
GAP = 8.0
d, width = wordmark_path(24 + GAP, baseline)
LOCK_W = 24 + GAP + width

def lockup_svg(ink="currentColor", light=None):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LOCK_W:.2f} 24" height="24" '
            f'width="{LOCK_W:.2f}" role="img" aria-label="LightChat"><title>LightChat</title>'
            f'{symbol_group(ink, light)}<path d="{d}" fill="{ink}"/></svg>\n')

open(f"{OUT}/lightchat-symbol.svg", "w").write(symbol_svg())
open(f"{OUT}/lightchat-lockup.svg", "w").write(lockup_svg())
open(f"{OUT}/lightchat-symbol-signal.svg", "w").write(symbol_svg("#1B1F1D", "#C27400"))
open(f"{OUT}/lightchat-lockup-signal.svg", "w").write(lockup_svg("#1B1F1D", "#C27400"))
print("lockup width", round(LOCK_W, 2), "units; scale", scale)

# --- Preview sheet (draft, for review only) ------------------------------
def tile(bg, ink, light, label):
    sizes = [16, 24, 32, 48, 96]
    syms = "".join(
        f'<svg viewBox="0 0 24 24" width="{s}" height="{s}" style="margin-right:18px;vertical-align:bottom">{symbol_group(ink, light)}</svg>'
        for s in sizes)
    lock = f'<svg viewBox="0 0 {LOCK_W:.2f} 24" height="28" style="display:block;margin-top:22px">{symbol_group(ink, light)}<path d="{d}" fill="{ink}"/></svg>'
    lock_big = f'<svg viewBox="0 0 {LOCK_W:.2f} 24" height="64" style="display:block;margin-top:18px">{symbol_group(ink, light)}<path d="{d}" fill="{ink}"/></svg>'
    return (f'<section style="background:{bg};color:{ink};padding:28px 32px;border-radius:6px">'
            f'<p style="margin:0 0 16px;font:600 13px/1 system-ui;opacity:.75">{label}</p>'
            f'<div>{syms}</div>{lock}{lock_big}</section>')

html = f"""<!doctype html><meta charset="utf-8"><title>LightChat logo draft v1 (review only)</title>
<body style="margin:0;padding:32px;background:#ddd;font-family:system-ui">
<h1 style="font:700 20px system-ui;margin:0 0 4px">LightChat logo · DRAFT v1 · for review, not integrated</h1>
<p style="margin:0 0 24px;font:14px system-ui">Symbol at 16 / 24 / 32 / 48 / 96 px, lockup at header (28 px) and large size.</p>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
{tile("#FBFBFA", "#1B1F1D", "#C27400", "Light · signal (ink + amber pulse)")}
{tile("#121513", "#E7EAE6", "#F0A93A", "Dark · signal")}
{tile("#FFFFFF", "#000000", None, "Monochrome black")}
{tile("#000000", "#FFFFFF", None, "Monochrome white")}
</div></body>"""
open(f"{OUT}/preview.html", "w").write(html)
