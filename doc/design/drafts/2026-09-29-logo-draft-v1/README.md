# LightChat logo: DRAFT v1 (design artifact for review)

**Status:** draft for the Gardener's review. **Not integrated** into the app; nothing in `templates/` or `static/` references these files. Final assets are produced only after the plan is approved (plan task "logo assets").

Concept, rationale and usage rules: [LightChat identity brief](../../2026-09-29-1357-lightchat-identity-brief.md#6-logo-pulse-bubble).

| File | What it is |
|---|---|
| `lightchat-symbol.svg` | Symbol, regular optical size (use at 32 px and up), `currentColor` monochrome |
| `lightchat-symbol-signal.svg` | Symbol, regular size, ink `#1B1F1D` + amber pulse `#C27400` |
| `lightchat-symbol-small.svg` / `-small-signal.svg` | Small optical size (16–32 px: favicons, tabs): heavier stroke, larger light |
| `lightchat-lockup.svg` / `-signal.svg` | Symbol + "LightChat" wordmark, outlined (no font needed) |
| `preview.png` | Symbol at 16/24/32/48/96 px and lockups on light, dark, black and white (rendered 2×) |
| `favicon-compare-2x.png` | Regular vs small symbol in browser tabs at 16 px (rendered 2×; the 1× check was also inspected) |
| `generate_logo.py` | The script that built these (needs `fonttools` and the Barlow Semi Condensed SemiBold TTF, not committed) |

**Wordmark font:** Barlow Semi Condensed SemiBold, SIL Open Font License 1.1, © 2017 The Barlow Project Authors. Source: `github.com/google/fonts` `ofl/barlowsemicondensed/`, last changed in commit `89f5431ff0db` (2018-12-05).
