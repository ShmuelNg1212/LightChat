"""Check the LightChat colour tokens in static/css/app.css against WCAG 2.2 AA.

Run: python doc/design/check_contrast.py   (exit 1 if any pair fails)
Reads the light :root block and the dark prefers-color-scheme block.
"""
import re
import sys
from pathlib import Path

css = (Path(__file__).resolve().parents[2] / "static/css/app.css").read_text()
light_block = re.search(r":root \{(.*?)\n\}", css, re.S).group(1)
dark_block = re.search(r"prefers-color-scheme: dark\) \{\s*:root \{(.*?)\n  \}", css, re.S).group(1)


def tokens(block):
    return dict(re.findall(r"--([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6})", block))


def luminance(hex_):
    r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5))
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def ratio(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


TEXT, UI = 4.5, 3.0
PAIRS = [  # foreground, background, minimum
    ("ink", "ground", TEXT), ("ink", "surface", TEXT), ("ink", "surface-sunk", TEXT),
    ("muted", "ground", TEXT), ("muted", "surface", TEXT), ("muted", "surface-sunk", TEXT),
    ("readout-ink", "readout", TEXT), ("pulse", "surface", TEXT), ("pulse", "ground", TEXT),
    ("pulse", "readout", TEXT), ("danger", "surface", TEXT), ("danger", "ground", TEXT),
    ("on-ink", "ink", TEXT), ("ink", "selection", TEXT),
    ("line-strong", "surface", UI), ("line-strong", "ground", UI), ("pulse-mark", "surface", UI),
    ("pulse-mark", "readout", UI),
]

failed = False
for name, block in (("light", light_block), ("dark", dark_block)):
    t = {**tokens(light_block), **tokens(block)} if name == "dark" else tokens(block)
    for fg, bg, need in PAIRS:
        r = ratio(t[fg], t[bg])
        ok = r >= need
        failed |= not ok
        print(f"{name:5} {fg:12} on {bg:12} {r:5.2f} (>= {need}) {'ok' if ok else 'FAIL'}")
sys.exit(1 if failed else 0)
