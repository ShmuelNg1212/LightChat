# Plan: LightChat rebrand, slice 1 (identity + chat screen)

- **Date:** 2026-09-29 14:06
- **Study:** [../study/2026-09-29-1357-lightchat-rebrand.md](../study/2026-09-29-1357-lightchat-rebrand.md)
- **Design brief:** [../design/2026-09-29-1357-lightchat-identity-brief.md](../design/2026-09-29-1357-lightchat-identity-brief.md)
- **Status:** done

> **Approved 2026-09-29.** The Gardener replied "approved" to the study, brief and plan.

Code-led. Nothing below starts before approval. Every task leaves the app working, with all tests passing.

## Tasks

### A. Direction on record
- [x] 1. Report the approved choice to Impeccable (`concept-seed --kind assigned --from 00ad6455`). Write the direction contract (brief §8) into the chat surface brief with `impeccable surface-brief write templates/chat/chat.html`, and verify all six blocks and the seed key are present. → `docs(design): record the Prepaid Meter direction contract`

### B. Identity assets
- [x] 2. Final logo SVGs in `static/brand/`: symbol (regular and small optical size), lockup, each in signal, mono-ink and mono-white variants. Plus `doc/design/brand/logo-usage.md` (clear space, minimum sizes, backgrounds, don'ts, font source and licence). Promote from the draft, with geometry reviewed at 16, 24, 32, 48 and 96 px. → `feat(brand): add LightChat logo symbol and lockup`
- [x] 3. `favicon.svg` (small optical size, with a dark-mode media query), `favicon-32.png`, `apple-touch-icon.png` (180), `icon-192.png`, `icon-512.png`, `icon-maskable-512.png`, and `site.webmanifest` (`name`/`short_name` "LightChat", relative `start_url`, theme colors from the tokens). Rasters are rendered from the SVGs with headless Chrome, with their provenance recorded in the usage doc. Add a test that the manifest is served and valid, and that the icon files exist. → `feat(brand): add favicon, app icons and web manifest`

### C. Shared system (app-wide)
- [x] 4. Self-host Public Sans (variable) and Barlow Semi Condensed 500/600 as latin-subset WOFF2 in `static/fonts/`, with their `OFL.txt` files and a source note. → `build(ui): self-host Public Sans and Barlow Semi Condensed`
- [x] 5. Replace the tokens in `app.css` with the Prepaid Meter system: color (light and dark), type scale, spacing, 6 px corners, hairlines, no blurred shadows, focus ring. Every page inherits it. A contrast script checks each token pair against AA. → `feat(ui): replace design tokens with the Prepaid Meter system`
- [x] 6. Draw the in-house icon set (menu, plus, send, stop, more) as a single inline SVG sprite partial. → `feat(ui): add LightChat interface icons`

### D. Rebrand
- [x] 7. Replace user-facing "Litechat" per the study inventory: titles, placeholder, JS title and error string, CSS/JS comments. Add a test that renders every user-facing page (sign-in, sign-up, chat empty/with messages, credits, delete) and the streamed `end` HTML, asserting "LightChat" is present and "Litechat" is absent. → `feat(brand): rename the product to LightChat`

### E. Shell and chat screen
- [x] 8. App shell: header with the lockup (symbol `aria-hidden` plus visible text in the home link), credit readout (accessible name, held segment), account area; rail restyle; drawer under 800 px. → `feat(ui): rebuild the app shell with the LightChat header and credit readout`
- [x] 9. Conversation: prompt blocks; answers at a fixed ~68ch measure in Public Sans 17/1.65; answer typography for headings, lists, code, tables and blockquotes. → `feat(chat): set conversations for long-form reading`
- [x] 10. Reading line under each reply, with states printed as words: holding (amber pulse), charged, cut off, stopped/under review, failed and not charged with Retry, reviewed. Server-rendered from `_message.html` and mirrored in the streaming placeholder. → `feat(chat): print a reading line under every reply`
- [x] 11. Composer dock and tariff selector: native select, rate display, and a worked example computed from the real rates; inverted Send; Stop. → `feat(chat): add the tariff selector and composer dock`
- [x] 12. Insufficient credit with real figures: the `/send/` rejection JSON gains `needed` and `available` (already computed by the server), and the UI prints "could cost up to X · you have Y". Add a test. → `feat(chat): state needed and available credit when a message can't be sent`
- [x] 13. First-run empty state (balance, demo note, three numbered steps) and the no-models state. → `feat(chat): add first-run steps and the no-models state`
- [x] 14. Motion: the pulse while credit is held, and the settle on the readout when a reply finishes. Both honor `prefers-reduced-motion`. → `feat(ui): add the pulse and settle motion`

### F. Entry screens
- [x] 15. Sign-in and sign-up in the new system: lockup, one-line promise from PRODUCT.md facts only ("Pay only for what you use. No subscription."), demo-credit note on sign-up. → `feat(accounts): bring sign-in and sign-up into the LightChat identity`

### G. Impeccable passes (targeted, not exhaustive)
- [x] 16. `/impeccable clarify` on chat and entry copy: empty, errors, reading lines, labels. Apply the agreed wording. → `fix(copy): clarify chat states and labels`
- [x] 17. `/impeccable harden` on the chat screen: a 3,000-word answer, a 25,000-token cut-off, wide code and tables, 200 chats, long titles, zero balance, no models, dropped stream. → `fix(chat): harden long content and failure states`
- [x] 18. `/impeccable audit` (accessibility, responsive, theming) plus axe-core in headless Chrome on every slice-1 page in both themes; fix findings. → `fix(a11y): address audit findings`
- [x] 19. `/impeccable critique` of the chat screen against the direction contract, then `/impeccable polish` in one batched round. → `style(ui): polish the chat screen`

### H. Verification and finish
- [x] 20. Seed a **separate** SQLite database (not your dev data) with every chat state via the fake proxy, and capture desktop 1280 and phone 390 × light/dark. Then:
  - check keyboard-only use (tab order, focus visible, Enter/Shift+Enter/Esc);
  - check the favicon at real 16 px in a tab and the lockup in the header;
  - run the naming test;
  - run the Impeccable detector on the changed templates and CSS;
  - make one **paid** live reply (short) to confirm the settle on the real proxy.

  Spawn Impeccable's finish reviewer with the contract and screenshots. Act on its disposition (at most two rounds). → fixes as `fix(...)` / `style(...)` commits
- [x] 21. All tests pass; `git log` reads cleanly; set Status to `awaiting-rendezvous`. → `docs(plan): mark lightchat-rebrand ready for rendezvous`

### After acceptance (Sync)
- Generate **DESIGN.md** (and `.impeccable/design.json`) from the built system with Impeccable's documenter. Update the wiki: rename the README title and current-state text to LightChat, add a visual-system section and logo usage links, and note the kept internal names (`litechat.*` loggers, repo folder, proxy domain). → `docs(design): record the LightChat visual system in DESIGN.md`, `docs(wiki): sync after lightchat-rebrand`

## Outcome

Accepted by the Gardener on 2026-09-29 ("ok move on to the final steps"). At Sync, Impeccable's documenter wrote [DESIGN.md](../../DESIGN.md) and `.impeccable/design.json` from the built system, and the wiki was updated in `docs(wiki): sync after lightchat-rebrand`.

**Drift the documenter found. Reported to the Gardener, not fixed during Sync:**
1. The "Demo top-ups stop at…" flash message is amber (`.flash-warning`), which breaks "amber means credit in motion only".
2. The delete confirmation's button is the ink primary instead of the danger style.
3. Dead CSS: the unused alias tokens block, a duplicated `.content.streaming` rule, and conflicting `overflow-wrap` values.
4. A stale reason text on the `.impeccable/config.json` blockquote ignore (the rule is now 1px).
5. Build vs. brief micro-differences (label tracking 0.06em, answer headings weight 650, code 0.86em). DESIGN.md records the build.

## Execution notes

- **Task 1:** direction choice reported to Impeccable (`concept-seed --kind assigned`, "choice recorded"). Contract at `.impeccable/surfaces/templates-chat-chat-html.md`.
- **Task 5:** the contrast script caught two pairs the brief had not measured (light control borders on the ground, 2.77:1; the amber light on the readout, 2.78:1). They are now `#808883` and `#AE6800`; all 36 pairs pass. The logo keeps `#C27400`.
- **Task 8:** stream events now also report held credit, so the readout's held segment stays live.
- **Task 19:** the second screenshot round showed no remaining material defects, so no `style(ui)` polish commit was needed. The critique was carried by the finish reviewer instead (task 20).
- **Task 20, inspection:** two screenshot rounds (7 page states × desktop/phone × light/dark) on a **separate practice database** seeded through the fake proxy. The Gardener's data was untouched. Round 1 found 6 defects, fixed in `fix(chat): harden…`. axe-core 4.13: 2 findings, fixed, then **0 violations** across 8 pages × 2 themes × 2 widths. The keyboard walk-through passed and added a chat skip link. Impeccable detector: 0 findings.
- **Task 20, finish review** (`impeccable-finish-reviewer`, fresh context): disposition **fix** with 8 material findings. 6 were accepted and applied in `fix(ui): act on the finish review`: the settle prints the charge; low credit is refused up front with the reason; the minimum hold is shown before sending; an authored select with no phone clipping; the phone readout keeps its unit; sign-up help in our own words; a plated favicon. 2 were declined with reasons (4-decimal sign-up grant; itemised held credit in the header, which belongs to slice 2). It also found a regression: new chats auto-scrolled past their heading. Fixed.
- **Finish review, verdict round** (same reviewer): all 8 findings closed (6 resolved; both declines accepted with their reasons). One recapture was requested (first-run shots had been taken on an account the live test had used) and redone with a chat-free account. One regression was found (the phone dock was too tall) and fixed in `fix(ui): compact the phone composer dock`. That fix was verified by measurement (dock top 620/844, 577 with the low-credit warning; step 3 fully visible), axe (0), the detector (0) and contrast (pass). It was **not** re-scored by the reviewer, because the two-round review budget ended there.
- **Paid usage:** 2 short live replies on the practice server (188 in / 49 out and 188 in / 46 out tokens), for the live settle before and after the fix.

## Later slices (separate requests)

1. **Credits as a statement:** a summary readout, top-up, tariffs table, and ledger lines with a running balance.
2. **Secondary pages:** delete confirmation, 404/500 pages, and admin site header "LightChat admin".
3. **Optional:** per-chat spend in the rail; a PWA offline page.

## Paid upstream usage

One short live reply in task 20. Everything else uses the fake proxy.

## Blocked On

Nothing, pending your approval of the study, brief and plan.
