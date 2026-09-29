# Design brief: LightChat identity, "Prepaid Meter"

- **Date:** 2026-09-29 13:57
- **Status:** proposed, awaiting the Gardener's approval (with the [study](../study/2026-09-29-1357-lightchat-rebrand.md) and [plan](../plan/2026-09-29-1406-lightchat-rebrand.md))
- **Product truth:** [PRODUCT.md](../../PRODUCT.md). This brief adds no product facts.
- **Method:** Impeccable 4.4.0 `init` → `shape` → new-work direction flow (concept seed `00ad6455`, mode *operate*). The aesthetic decision was delegated to the Vine.

---

## 1. Job and audience

An occasional, nontechnical person opens LightChat to get one thing done: ask, read a good answer, and know what it cost. They come back days later on a phone or laptop.

**Visitor mode: Operate.** Success is completing the task (a conversation) with money understood, not being impressed. Brand lives in precise details. It must never slow down reading or writing.

## 2. Outcome and proof

The one thing LightChat can show that a generic chat app can't: **every reply is metered in plain view.** The price is shown before sending, the most it could cost is held while it's written, and the reply is charged only for what it used, with the rest visibly returned. The identity has to make that mechanism feel as ordinary and trustworthy as a household utility meter.

## 3. Selected direction: **Prepaid Meter**

> LightChat looks and behaves like a well-made prepaid electricity meter and its printed usage statement: calm faceplate surfaces, one backlit readout that always shows what you have left, a pulse that blinks only while you are using credit, and a printed reading under every reply.

**Why this world, for these users.** Pay-as-you-go already has a form people know by heart: prepaid electricity and prepaid mobile load. You top up in advance, a pulse light shows usage, and a readout tells you what's left. "Light" is literally what a prepaid meter sells. The metaphor needs no explanation for a nontechnical user, and it carries LightChat's exact mechanism: top-up, hold while running, settle, remaining balance. It is also *not* the chat-app default: no soft gray bubbles, no violet gradient, no glowing AI orb.

**How the direction was reached.** From the audience's world I ranked seven grounded candidates. Each was one line of reasoning; together they span four material families.

1. *Transit fare card and station wayfinding:* tap, see the fare, see the balance.
2. *Thermal till receipt:* an itemised cost for each reply.
3. *Bank passbook:* a printed running balance.
4. *Postal franking meter:* each letter stamped with what it cost.
5. **Prepaid utility meter and its statement:** metered use, a pulse, a readout.
6. *Prepaid load scratch card:* denominations and top-up.
7. *Lighthouse/beacon:* the literal reading of the name; one slot, by rule.

The seed assigned **#5**. My own top pick was #1 (transit card), which shares the "balance after every use" idea but is more familiar as a design trope and weaker on *holds* and *settling*. The meter wins on both audience fit and product clarity, so it is the direction.

The seed also dealt six catalog challengers. Each was fused with LightChat's facts and judged on audience identification and product clarity. **All six were declined** (a green-phosphor terminal and a HyperCard stack read as technical or nostalgic to nontechnical users; a copy-shop zine, an industrial painting, an origami sequence and a surreal rain garden obscure the money). Each still donated one system discipline, written into the direction as its own named line:

- **Raise (phosphor terminal): states print themselves.** Held, charged, stopped, failed and not-sent are printed words in the reply's reading line, not colored pills or banners.
- **Raise (HyperCard stack): state by inversion.** Pressed, selected and primary controls invert (ink fill, light text). Meaning never depends on color alone.
- **Raise (copy-shop zine): a fixed reading measure.** Answers hold a constant measure (about 68 characters). Wider windows get more margin, never longer lines.
- **Raise (precisionist plate): one light, flat planes.** No blurred drop shadows. Depth comes from flat planes and 1 px hairlines only.
- **Raise (origami sequence): numbered steps in a margin column.** First run teaches the loop as three numbered steps, the one place numbering is used.
- **Raise (rain garden): one color, one force.** Amber means *credit in motion* (held, estimating, streaming) and nothing else, anywhere.

**Coherence.** One idea runs through every choice. The *readout* is the backlit panel; *usage* is the amber pulse; *settled* is plain printed ink. The faceplate, the readout and the printed statement are the only three materials.

**Anti-goals.** No skeuomorphic meter costume: no seven-segment LCD font, fake screws, dials or knobs. No gamified "energy" language. No "AI sparkle", gradients, glow or glassmorphism. No borrowed provider brand colors or logos. No copying Litechat's look.

**Implementation consequence.** Replace the current tokens, type and component styling app-wide (one stylesheet). Rebuild the chat screen's hierarchy around the readout and the reading line. Keep all behavior, routes, copy facts and accepted states.

## 4. The system

### 4.1 Information hierarchy and navigation

- **Top bar (faceplate):** LightChat lockup (links home), then the **credit readout**: a backlit panel with the label *Available*, the amount to 4 decimals, "credits", and, only when something is held, an amber *held* amount. It links to the Credits page. The account name and **Sign out** sit at the right.
- **Rail (left; a drawer on phones):** **New chat** and the saved chats list. Topology unchanged from today: users already know it.
- **Conversation column:** prompts and replies at a fixed reading measure. Every reply ends with its **reading line**.
- **Composer dock (bottom):** message box, the **tariff selector** (model plus its rates), Send/Stop.
- Order of emphasis on the chat screen: *the conversation* > the composer > the credit readout > the rail > model and price details.

### 4.2 Typography and long-form readability

| Role | Face | Setting |
|---|---|---|
| Answers, prompts, UI text | **Public Sans** (variable, 400–700), SIL OFL 1.1, `google/fonts@37caf6579420` | Answers 17 px / 1.65, measure ~68ch; UI 15 px / 1.45 |
| Readouts, reading lines, labels, wordmark | **Barlow Semi Condensed** 500/600, SIL OFL 1.1, `google/fonts@89f5431ff0db` | Tabular lining figures; small caps-style labels at 12 px, +0.04em tracking, used sparingly (AVAILABLE, HELD, RATE) |
| Code in answers | System monospace stack (`ui-monospace, SF Mono, Menlo, Consolas`) | 0.88em, scrollable blocks, never wrapped mid-token |

Both faces are self-hosted as latin-subset WOFF2 with their OFL texts. There are no third-party font requests. Headings inside answers step down gently (1.3 / 1.15 / 1em at 600 weight) so a 3,000-word answer scans without shouting. Paragraph spacing is 0.9em and list items are 0.35em apart.

### 4.3 Color and semantic status

**Strategy: Restrained.** Neutrals, the backlit readout, and one semantic accent. **Physical scene:** a person on a phone in daylight between errands, or at a laptop in the evening. Light is the default; dark follows the OS. Neither theme is an afterthought.

| Token | Light | Dark | Only used for |
|---|---|---|---|
| `ground` (faceplate) | `#F1F2EF` | `#121513` | Page background |
| `surface` (panel) | `#FBFBFA` | `#1A1E1C` | Rail, composer, cards |
| `ink` | `#1B1F1D` | `#E7EAE6` | Text, settled amounts, primary controls (inverted) |
| `muted` | `#565D59` | `#9BA39E` | Secondary text |
| `line` | `#D5D9D4` / UI `#8C948F` | `#2C322F` / UI `#6B736E` | Hairlines / control borders (≥3:1) |
| `readout` / `readout-ink` | `#DCE4D3` / `#16211A` | `#1D2A21` / `#CFE6C7` | The credit readout panel only |
| `pulse` text / mark | `#8F5200` / `#C27400` | `#F0A93A` | **Credit in motion only:** held, estimate, streaming |
| `danger` | `#AE2A1F` | `#F2857A` | Not sent, failed, destructive actions |

All text pairs were measured at ≥ 4.5:1 and UI marks at ≥ 3:1 (WCAG 2.2 AA), in both themes. "Charged" is plain ink, not green: paying is normal, not a victory. Every status carries a word, so color is never the only signal.

### 4.4 Layout, spacing and density

- 4 px base; spacing scale 4 / 8 / 12 / 16 / 24 / 32 / 48. More space above a heading than below.
- One corner language: 6 px on panels and controls. The only round shape is the pulse light.
- Density: *comfortable* for reading (answers), *compact* for readouts and reading lines (one line, small).
- Rail 264 px on desktop. The conversation column is centered at its fixed measure. The composer dock aligns to the same column.

### 4.5 Components, iconography and motion

- **Credit readout:** backlit panel; amount in Barlow tabular figures; an amber *held* segment appears only while credit is held.
- **Reading line** (end of every reply, hairline above): `model · 199 in / 3,140 out · 0.0638 credits charged`. While running: an amber pulse light and "holding up to 0.5231". Stopped, failed or not sent: printed words in the same line, with **Retry** as a text button where allowed.
- **Tariff selector:** a native `<select>` (keyboard and screen-reader safe) styled as a faceplate switch. Beside it: the selected rate and a worked example computed from the real rates ("A 1,000-token question with a 500-token answer costs 0.0150 credits.").
- **Prompt block:** the user's words in a surface panel, right-aligned, measure capped at ~60ch.
- **Buttons:** primary = inverted ink; secondary = hairline outline; destructive = danger text; text buttons for Retry/Stop inside lines.
- **Icons:** a small in-house set drawn on a 20 px grid, 1.75 px stroke, round caps: menu, plus, send, stop, more. Nothing decorative.
- **Motion (three moments only):**
  1. The **pulse**: the amber light blinks about once a second while credit is held.
  2. The **settle**: when a reply finishes, the held segment collapses and the available figure counts down to its new value (~500 ms, ease-out).
  3. The **drawer**: the phone rail slides.

  With `prefers-reduced-motion`, the pulse is steady and the settle is instant. Signature interaction: **the settle.** You watch a hold become a charge and the rest come back.

### 4.6 Voice, labels, onboarding and errors

**Voice:** plain, calm, specific, second person, numbers stated exactly. Never cute, never alarming, no jargon in primary labels ("tokens" appears only as secondary detail).

| Situation | Message (proposed) |
|---|---|
| First run (empty) | "You have 5.0000 demo credits, not real money." Then three numbered steps: **1** Pick a model; each shows its price. **2** Ask anything. **3** See exactly what it cost; unused credit comes straight back. |
| While replying | "Holding up to 0.5231 credits while this is written." |
| Charged | "0.0638 credits charged · 199 in / 3,140 out" |
| Not enough credit | "Not sent. This reply could cost up to 0.5231 credits and you have 0.1000. Add demo credits to continue." (uses the real needed/available figures) |
| Busy (429) | "The model service is busy. Nothing was charged. Try again in a moment." |
| Stopped / interrupted | "Stopped. Up to 0.5231 credits are held while the cost is checked. Anything unused comes back." |
| Cut off at limit | "This reply reached the 25,000-token limit and stopped. Ask it to continue." |
| No models available | "No models are available right now, so nothing can be sent or charged." |

Exact wording is finalised in the plan's *clarify* pass. Facts and figures always come from the server.

### 4.7 Responsive behavior and keyboard access

- **≤ 800 px:** the rail becomes a drawer (☰), and the readout shows the amount only (label hidden visually, kept for screen readers). Reading lines may wrap to two lines, and the tariff selector takes the full width with the rate below it. Nothing scrolls horizontally from 360 px up; code blocks and tables scroll inside themselves.
- **Keyboard:** tab order is skip link → brand → readout → account → rail → messages region → message box → tariff → Send/Stop. Enter sends; Shift+Enter adds a new line; Esc closes the drawer. The focus ring is 2 px ink with a 2 px ground offset, visible in both themes and on inverted buttons.
- **Screen readers:** one polite live region announces "Reply finished", "Stopped" and errors, never streamed words. The readout has an accessible name ("Available credit: 4.9362 credits").

## 5. Scope, states and ranges

**Slice 1 (this plan):**
- The identity: logo, favicon, icons, manifest and name.
- The shared system: tokens, type, components.
- The app shell.
- The chat screen end to end.
- Sign-in and sign-up, restyled so the first impression carries the identity.

**Later slices:**
- The Credits page as a full "statement".
- Remaining pages (delete confirmation, error pages).
- The admin site header.

**States covered by slice 1:**
- empty/first-run;
- streaming (short and 3,000+ word answers, headings, lists, code, tables);
- charged;
- truncated at 25,000 tokens;
- stopped and under review;
- failed and not charged, with Retry;
- insufficient credit;
- no models available;
- dropped connection;
- long chat titles;
- 1 to 200 chats in the rail.

**Ranges:**
- balances from 0.0000 to 10.0000;
- holds up to about 0.53;
- replies from one word to 25,000 tokens.

## 6. Logo: "Pulse bubble"

**Concept.** An open speech bubble whose tail is a single solid dot: the meter's pulse light. Chat plus light, drawn with two shapes. In the interface, the same amber light is what blinks while credit is in use, so the mark and the product behave as one.

**Construction.** 24-unit grid; rounded-rect bubble 20×16 with 5-unit corners; 2.5-unit round-capped stroke, open at the lower-left corner; the light a 5.5-unit circle set in the gap. A **small optical size** (3.4-unit stroke, 7.2-unit light) is used from 16–32 px, where the regular drawing lost its light (verified in 1× browser tabs). The wordmark "LightChat" is Barlow Semi Condensed SemiBold, outlined, with a light +12/1000 tracking. Its cap height is 13 units, centered on the bubble body, with an 8-unit gap.

**Colorways.**
- *Signal:* ink bubble with an amber light (light and dark variants).
- *Mono:* all ink, or all white.

Transparent background always. No gradients, effects or sparkles.

**Usage (to be finalised with the assets):**
- **Clear space:** at least the light's diameter on all sides.
- **Minimum sizes:** symbol 16 px (small optical size up to 32 px); lockup 20 px tall.
- **Backgrounds:** signal on `ground`/`surface` in either theme; mono anywhere else; never on photos.
- **Don'ts:** don't recolor the light except amber or mono; don't rotate, outline, or separate the light from the bubble.

**Honest risk.** A bubble with a dot belongs to a crowded family of messaging marks. Distinctiveness rests on the dot being *the tail* and on the amber pulse behavior repeating in the UI. The wordmark face is a DIN-lineage grotesk, familiar by intent (it's the faceplate type of meters and signage).

**Draft:** [drafts/2026-09-29-logo-draft-v1/](drafts/2026-09-29-logo-draft-v1/) (preview sheet and 16 px tab comparison). Not integrated.

**Accessibility.** In the header, the symbol is `aria-hidden` next to the visible text "LightChat" inside the home link, so screen readers announce "LightChat, link" once. Standalone exported SVGs carry `role="img"` and a title.

## 7. Build path: code-led

Code-led, for three reasons:
- There is no image-generation tool in this environment. Impeccable's comp-led path would require one, or spending your API credit, which you haven't authorised.
- LightChat is an *Operate* surface inside a working app, where real states (streaming, holds, errors) matter more than a static composition.
- Code-led yields a more coherent first pass.

The ambition lives in the direction contract (below) and is audited at the finish review.

## 8. Direction contract (to be recorded in the chat surface brief at Execute)

- **THESIS:** every reply is metered in plain view. The chat reads like a calm faceplate with one backlit readout, refusing the category's gray-bubble, glowing-orb default.
- **OWN-WORLD:** faceplate gray ground, printed ink, one sage backlit readout, an amber pulse that only ever means credit in motion; Public Sans text and Barlow Semi Condensed readouts; flat planes, 1 px hairlines, 6 px corners.
- **STORY:** the visitor sees what they have, picks a model with its price in view, reads the answer comfortably, and sees the hold become a charge and the rest come back.
- **FIRST VIEWPORT:**
  - *Top bar:* lockup on the left, then the credit readout.
  - *Rail:* on the left.
  - *Empty state:* a first-run column with the balance and three numbered steps.
  - *Composer dock:* at the bottom, with the tariff selector and inverted Send as the primary action.
- **FORM:** Prepaid Meter, #5 of 7 grounded candidates, seed key `00ad6455`.
- **FINISH:** unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.

## 9. Incumbent visual system (recorded before replacement)

For the record, the current look (to be replaced, not polished):
- **Type:** system UI sans.
- **Color:** a warm off-white or near-black ground, with teal `#0f766e`/`#2dd4bf` as the only accent.
- **Shape:** 10 px/6 px corners and a soft shadow.
- **Layout:** ChatGPT-style, with a 272 px sidebar, a centered 760 px column, gray right-aligned user bubbles and pill tags.
- **Brand:** the text "Litechat" plus an inline speech-bubble favicon.

It is coherent but category-default and carries no identity. It's recorded here, rather than in a DESIGN.md, because DESIGN.md will describe the new world once it's accepted.

## 10. Open decisions (not for the builder to invent)

- Whether the rail should later show per-chat spend (data exists; slice 2 candidate).
- Admin-site branding (later slice).
- Any domain, trademark or app-store listing: none claimed.
