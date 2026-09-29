# Study: LightChat rebrand and design direction

- **Date:** 2026-09-29 13:57
- **Request:** Initialize Impeccable, rebrand the product as **LightChat**, and develop its design direction including a minimalist logo. Complete Study and Plan together, then pause for approval before implementing the interface or applying the rebrand. The aesthetic decision is delegated to the Vine. Preserve approved product decisions and working functionality.
- **Status:** awaiting-approval (together with the [plan](../plan/2026-09-29-1406-lightchat-rebrand.md) and the [design brief](../design/2026-09-29-1357-lightchat-identity-brief.md))

## Intended Outcome

LightChat has its own recognizable identity, and a first-time, nontechnical user can have a conversation and understand its cost more easily than today. Nothing that works today stops working.

Acceptance criteria for the first slice, all testable from the outside:

- **Name:** every user-facing surface says **LightChat**, spelled exactly so: page titles, header, sign-in and sign-up, the message box, error text, favicon/app name and the web manifest. No user-facing "Litechat" remains. Historical documents and external service names are unchanged.
- **Logo:** the header shows the LightChat lockup. The browser tab shows the symbol and it stays recognizable at 16 px. Installing or bookmarking to a phone home screen shows the app icon with the name LightChat.
- **Chat screen in the new system:** the credit readout is always visible and states available credit, plus held credit while a reply runs. The model picker shows each model's real rates and a worked example computed from them. Every reply ends with a reading line (model, tokens, credits charged or held), and statuses are printed words, never color alone.
- **Reading:** long answers (3,000+ words, headings, lists, code, tables) keep a comfortable line length at any window width. There's no horizontal page scrolling from 360 px up.
- **States:**
  - first run (empty) with three numbered steps;
  - streaming;
  - charged;
  - truncated;
  - stopped or under review;
  - failed and not charged, with Retry;
  - insufficient credit (showing the real "could cost up to" and "you have" figures);
  - no models available;
  - connection dropped.

  Each state is clear in words and correct in both themes.
- **Access:** WCAG 2.2 AA. Text contrast is ≥ 4.5:1 and UI marks ≥ 3:1 in light and dark. Every control is reachable and operable by keyboard with a visible focus ring. Screen readers hear reply completion and errors once each. Reduced motion stops the pulse and the settle animation.
- **Unchanged:** all 115 existing tests still pass, and every accepted behavior (billing, holds, duplicates, stop, retry, reconciliation, privacy) works as before.

## Current State

- **App:** Django 6.1, server-rendered templates, one stylesheet (`static/css/app.css`) and one script (`static/js/chat.js`). See [architecture.md](../wiki/architecture.md) and [features.md](../wiki/features.md).
- **Visual system:** a category-default chat clone with system fonts and a teal accent. It is recorded in the [brief, §9](../design/2026-09-29-1357-lightchat-identity-brief.md#9-incumbent-visual-system-recorded-before-replacement).
- **Impeccable status (verified this session):**
  - **Installed:** Impeccable **4.4.0**, a Claude Code marketplace plugin from `github.com/pbakaus/impeccable`. Not reinstalled; updates come through the plugin menu.
  - **Init:** done. [PRODUCT.md](../../PRODUCT.md) records users, purpose, positioning, capabilities, brand commitments and accessibility. Answers confirmed this session: the product is aimed at **real public users soon**; **WCAG 2.2 AA, English**; **fully independent** from Litechat and the providers.
  - **Automatic design checks:** the hook is **enabled** (shared `.impeccable/config.json`), with 1 recorded false-positive ignore (blockquote rule). No trust approval was needed: it already runs.
  - **Live Mode:** **prepared**. `.impeccable/live/config.json` targets `templates/base.html` (Django's shared shell). No CSP was detected, so no security change is needed. Nothing is injected until a Live session starts.
  - **Mockups:** **unavailable**, because no image-generation tool is available. Code-led is the only path, so no build-path default was recorded.
  - **Direction:** Impeccable `shape` → new-work flow; concept seed `00ad6455` (mode *operate*). The decision page (choosing between direction cards) was **not served**, because you delegated the aesthetic choice. The considered directions and verdicts are in the brief instead.
  - **Not written yet:** `DESIGN.md`. It will be generated from the built system after acceptance, as requested.

### Rebranding inventory

A case-insensitive search of tracked files found **"Litechat"/"litechat"** in these places:

| Where | Occurrence | Treatment |
|---|---|---|
| `templates/base.html` | `<title>… · Litechat</title>`, header brand text | **Change** to LightChat (lockup in header) |
| `templates/chat/chat.html` | Placeholder "Message Litechat" | **Change**: "Message LightChat" |
| `static/js/chat.js` | `document.title` suffix; "Couldn't reach Litechat…"; header comment | **Change** |
| `static/css/app.css` | Header comment | **Change** (names the product) |
| Favicon (inline data URI in `base.html`) | Old teal bubble | **Replace** with the LightChat symbol files |
| *(missing)* | No web manifest, app icons or apple-touch icon | **Add** `site.webmanifest` (name/short_name "LightChat"), 192/512 and maskable icons, apple-touch icon |
| Admin site header | Django default "Django administration" | **Later slice** (admins only) |
| `config/settings.py` `PROXY_BASE_URL` default `https://proxy.litechat.ai` | External service address | **Keep**: a real third-party service, not our brand |
| Logger names `litechat.chat`, `litechat.proxy`, `LOGGING["litechat"]` | Internal identifiers | **Keep**: not user-facing; renaming would only churn log config. Documented in the wiki at Sync |
| Repository folder `litechat_midterm`, Django apps, database, `.env` names | Internal | **Keep** |
| `doc/study/*litechat-core*`, `doc/plan/*litechat-core*`, `doc/fixtures/proxy/*` | Historical records and real captures | **Keep unchanged** (journal and evidence) |
| `doc/wiki/*.md` (README title "Wiki: Litechat replica", setup, features) | Current-state docs | **Change at Sync** (after acceptance), keeping references to the original Litechat product and the proxy domain |
| `PRODUCT.md` | Mentions Litechat as the functional reference | **Keep**: correct attribution |
| `AGENTS.md` / `CLAUDE.md` | No product name | No change |

No domain, trademark or store listing is claimed or renamed.

## Options & Tradeoffs

**Direction.** Options are summarized here; the full reasoning is in [brief §3](../design/2026-09-29-1357-lightchat-identity-brief.md#3-selected-direction-prepaid-meter).

| Option | Pros | Cons | Effort | Risk |
|---|---|---|---|---|
| **Prepaid Meter** (chosen) | The metaphor nontechnical users already live with; carries top-up, hold, settle and balance; distinct from the category | Must avoid skeuomorphic costume | Medium | Low–medium |
| Transit fare card and wayfinding | Balance-after-use, clear signage | More familiar trope; weak on holds | Medium | Medium |
| Polish the current look with a new name | Cheapest | Keeps a category-default clone; no identity | Low | High (fails the brief) |

**Build path.**

| Option | Pros | Cons | Effort | Risk |
|---|---|---|---|---|
| **Code-led** (chosen) | Coherent first pass; real states; no image credits | Less compositional ambition, offset by the direction contract and finish review | Medium | Low |
| Comp-led (mockups first) | Bolder composition | No image tool here; would need your API credit; the translation to code loses detail | High | Medium |

**Rebrand mechanics.**

| Option | Pros | Cons | Effort | Risk |
|---|---|---|---|---|
| **Targeted replacement** of user-facing strings plus an automated "no Litechat in rendered pages" test (chosen) | Precise; history and external names intact; regressions caught | Needs a curated list | Low | Low |
| Global search-and-replace | Fast | Would break the proxy URL, rewrite history, rename loggers | Low | High |

## Recommendation

- **Adopt the "Prepaid Meter" direction** and the **"Pulse bubble"** logo as specified in the [design brief](../design/2026-09-29-1357-lightchat-identity-brief.md).
- Build code-led.
- The first slice delivers:
  - the identity assets and naming;
  - the shared tokens and type (app-wide, one stylesheet);
  - the app shell;
  - the chat screen end to end across all its states;
  - sign-in and sign-up in the new system.
- The Credits page as a full "statement", secondary pages, and the admin header come in later slices. They still receive the new tokens automatically in slice 1, so nothing looks broken in between.
- Fonts are self-hosted (OFL) so there are no third-party requests.
- Framework defaults stay in place: plain templates, CSS custom properties and vanilla JS. No new front-end dependencies.

**One small behavior addition** is needed for the approved copy: the "not enough credit" response will also return the *needed* and *available* amounts the server already computes, so the message can state real figures. Nothing about billing changes.

## Exogenous Inputs

| Input | Why needed | Status | Owner |
|---|---|---|---|
| Name "LightChat" | Identity | verified (Gardener) | Gardener |
| Audience, accessibility and independence answers | PRODUCT.md | verified (answered 2026-09-29) | Gardener |
| Font files and licences | Self-hosted type and outlined wordmark | verified: Public Sans and Barlow Semi Condensed, SIL OFL 1.1, from `google/fonts` (`37caf6579420`, `89f5431ff0db`) | Vine |
| Image generation | Only for comp-led mockups | unavailable; not needed | — |
| Domain / trademark / app-store name | Would affect manifest `start_url`/`id` and claims | **not supplied; none claimed** (the manifest uses relative URLs) | Gardener, later |

## Risks & Open Questions

- **Logo distinctiveness:** bubble-plus-dot marks are common. Distinctiveness relies on the dot-as-tail and the UI's matching pulse. You may prefer a stronger departure after seeing the draft.
- **Metaphor overreach:** "meter" must stay a system discipline, not a costume (no LCD fonts or dials). The finish review checks this.
- **Scope creep:** the Credits "statement" redesign is deliberately deferred. In slice 1 it only inherits tokens, which will make it look plainer than the chat screen until slice 2.
- **Behavior regressions from restyling:** mitigated by the unchanged 115-test suite plus a browser run over every chat state.
- **Public launch:** you indicated real public users are coming. Deployment, domain, real payments and their UX remain separate requests, and nothing in this slice claims them.
