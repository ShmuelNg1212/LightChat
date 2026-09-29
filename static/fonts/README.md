# Fonts (self-hosted)

| File | Family | Source | Licence |
|---|---|---|---|
| `public-sans-latin-var.woff2` | Public Sans, variable weight 100–900 | `github.com/google/fonts` `ofl/publicsans/PublicSans[wght].ttf`, commit `37caf6579420` | SIL OFL 1.1, `OFL-PublicSans.txt` |
| `barlow-semi-condensed-latin-500.woff2` | Barlow Semi Condensed Medium | `github.com/google/fonts` `ofl/barlowsemicondensed/BarlowSemiCondensed-Medium.ttf` | SIL OFL 1.1, `OFL-BarlowSemiCondensed.txt` |
| `barlow-semi-condensed-latin-600.woff2` | Barlow Semi Condensed SemiBold | same folder, `BarlowSemiCondensed-SemiBold.ttf`, commit `89f5431ff0db` | SIL OFL 1.1 |

Subset to Latin (U+0000-00FF plus common punctuation, arrows, € and ™) with `pyftsubset --layout-features='*' --flavor=woff2` (fontTools 4.60), keeping all OpenType features, including tabular figures (`tnum`) used by credit readouts. Downloaded 2026-09-29.
