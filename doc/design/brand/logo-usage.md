# LightChat logo: usage

The mark is the **Pulse bubble**: an open speech bubble whose tail is a single dot, the meter's pulse light. The concept and rationale are in the [identity brief §6](../2026-09-29-1357-lightchat-identity-brief.md#6-logo-pulse-bubble).

## Files (`static/brand/`)

| File | Use |
|---|---|
| `lightchat-lockup-{signal,signal-dark,black,white}.svg` | Symbol plus the "LightChat" wordmark (outlined; no font needed). Viewbox 105.6 × 24. |
| `lightchat-symbol-{…}.svg` | Symbol, **regular** optical size, for 32 px and up |
| `lightchat-symbol-small-{…}.svg` | Symbol, **small** optical size (heavier stroke, larger light), for 16–32 px |
| `favicon.svg` | Small symbol; switches ink and light for the browser's dark theme |
| `favicon-32.png`, `apple-touch-icon.png`, `icon-192.png`, `icon-512.png`, `icon-maskable-512.png` | Raster exports, see *Provenance* |

Colorways:
- `signal`: ink `#1B1F1D` with an amber light `#C27400`, on light grounds.
- `signal-dark`: `#E7EAE6` with `#F0A93A`, on dark grounds.
- `black` / `white`: single-color.

All files have transparent backgrounds except the app icons, which need a solid plate.

## Rules

- **Clear space:** keep at least the light's diameter (about a quarter of the symbol's height) empty on every side.
- **Minimum size:**
  - symbol: 16 px, using the small optical size up to 32 px and the regular above;
  - lockup: 20 px tall. Below that, use the symbol alone.
- **Backgrounds:** use `signal` on the LightChat ground/surface colors or white, `signal-dark` on the dark theme or near-black, and `black`/`white` everywhere else (single-color print, embossing, busy backgrounds). Never place it on photographs.
- **Color:** the light is amber or matches the ink, nothing else. Don't recolor the bubble.
- **Don't:** stretch, rotate, outline, add shadows, glows or gradients; separate the light from the bubble; set "LightChat" in another font next to the symbol; write it any other way than **LightChat**.

## Accessibility

- **In the app header,** the symbol is inline and `aria-hidden="true"`, next to the visible text **LightChat** inside the home link. Screen readers say "LightChat, link" once.
- **Standalone SVG files** carry `role="img"`, `aria-label="LightChat"` and a `<title>`. Where an image *is* the only name (e.g. an `<img>` with no text beside it), give it `alt="LightChat"`. Beside visible text, use `alt=""`.

## Typography

The wordmark is Barlow Semi Condensed SemiBold, © 2017 The Barlow Project Authors, SIL Open Font License 1.1. Source: `github.com/google/fonts`, `ofl/barlowsemicondensed/`, commit `89f5431ff0db`. Glyphs are outlined with light positive tracking (+12/1000 em). The cap height is 13 of the 24 units, centred on the bubble body, with an 8-unit gap after the symbol.

## Regenerating

`doc/design/brand/generate_logo.py <BarlowSemiCondensed-SemiBold.ttf> static/brand` rebuilds every SVG (needs `fonttools`).

## Provenance

Raster icons are rendered from the SVGs above with headless Chrome. The exact method is recorded in each PNG's `Description` metadata and in the plan task that made them. No image-generation model was used for any brand asset.
