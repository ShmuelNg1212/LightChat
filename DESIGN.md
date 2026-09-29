---
name: LightChat
description: Pay-as-you-go AI chat that reads like a calm prepaid-meter faceplate with one backlit credit readout.
colors:
  ground: "#F1F2EF"
  surface: "#FBFBFA"
  surface-sunk: "#E7E9E5"
  ink: "#1B1F1D"
  muted: "#565D59"
  line: "#D5D9D4"
  line-strong: "#808883"
  readout: "#DCE4D3"
  readout-ink: "#16211A"
  pulse: "#8F5200"
  pulse-mark: "#AE6800"
  danger: "#AE2A1F"
  on-ink: "#FBFBFA"
  selection: "#DCE4D3"
  logo-light: "#C27400"
  ground-dark: "#121513"
  surface-dark: "#1A1E1C"
  surface-sunk-dark: "#232826"
  ink-dark: "#E7EAE6"
  muted-dark: "#9BA39E"
  line-dark: "#2C322F"
  line-strong-dark: "#6B736E"
  readout-dark: "#1D2A21"
  readout-ink-dark: "#CFE6C7"
  pulse-dark: "#F0A93A"
  pulse-mark-dark: "#F0A93A"
  danger-dark: "#F2857A"
  on-ink-dark: "#121513"
  selection-dark: "#2F4535"
typography:
  display:
    fontFamily: "Public Sans, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 650
    lineHeight: 1.2
    letterSpacing: "-0.015em"
  headline:
    fontFamily: "Public Sans, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "1.6rem"
    fontWeight: 650
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Public Sans, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "1.2rem"
    fontWeight: 650
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  body-reading:
    fontFamily: "Public Sans, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.65
  body:
    fontFamily: "Public Sans, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.45
    fontFeature: "lnum"
  readout:
    fontFamily: "Barlow Semi Condensed, Public Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.2rem"
    fontWeight: 600
    lineHeight: 1
    fontFeature: "tnum, lnum"
  reading:
    fontFamily: "Barlow Semi Condensed, Public Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.9rem"
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "0.01em"
    fontFeature: "tnum, lnum"
  label:
    fontFamily: "Barlow Semi Condensed, Public Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.06em"
  wordmark:
    fontFamily: "Barlow Semi Condensed, Public Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.3rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.01em"
  code:
    fontFamily: "ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "0.86em"
    lineHeight: 1.55
rounded:
  plate: "6px"
  light: "50%"
spacing:
  "1": "4px"
  "2": "8px"
  "3": "12px"
  "4": "16px"
  "5": "24px"
  "6": "32px"
  "7": "48px"
components:
  button:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.plate}"
    padding: "0 16px"
    height: "40px"
  button-hover:
    backgroundColor: "{colors.surface-sunk}"
  button-active:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-ink}"
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-ink}"
    rounded: "{rounded.plate}"
    padding: "0 16px"
    height: "40px"
  button-small:
    padding: "0 12px"
    height: "32px"
  button-danger:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.danger}"
    rounded: "{rounded.plate}"
  icon-button:
    textColor: "{colors.ink}"
    rounded: "{rounded.plate}"
    size: "40px"
  icon-button-expanded:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-ink}"
  readout:
    backgroundColor: "{colors.readout}"
    textColor: "{colors.readout-ink}"
    typography: "{typography.readout}"
    rounded: "{rounded.plate}"
    padding: "0 12px"
    height: "40px"
  readout-held:
    textColor: "{colors.pulse}"
  readout-charged:
    textColor: "{colors.readout-ink}"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.plate}"
    padding: "8px 12px"
    height: "44px"
  composer-box:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.plate}"
    padding: "8px"
  tariff-label:
    backgroundColor: "{colors.surface-sunk}"
    textColor: "{colors.muted}"
    typography: "{typography.label}"
    padding: "0 8px"
  tariff-select:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    padding: "0 36px 0 12px"
    height: "36px"
  prompt:
    backgroundColor: "{colors.surface-sunk}"
    textColor: "{colors.ink}"
    rounded: "{rounded.plate}"
    padding: "12px 16px"
  reading-line:
    textColor: "{colors.muted}"
    typography: "{typography.reading}"
  convo-link:
    textColor: "{colors.ink}"
    rounded: "{rounded.plate}"
    padding: "8px 12px"
  convo-link-current:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-ink}"
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.plate}"
    padding: "24px"
  code-block:
    backgroundColor: "{colors.surface-sunk}"
    typography: "{typography.code}"
    rounded: "{rounded.plate}"
    padding: "12px 16px"
  pulse-light:
    backgroundColor: "{colors.pulse-mark}"
    rounded: "{rounded.light}"
    size: "8px"
---

# Design System: LightChat

## Overview

**Creative North Star: "The Prepaid Meter"**

LightChat looks and behaves like a well-made prepaid electricity meter and its printed usage statement. There are three materials and no others: a calm grey **faceplate** (ground and panels), **printed ink** (text, settled amounts, primary controls), and one **backlit readout** in sage that always shows the credit you have left. A single amber **pulse light** blinks only while credit is in use. Every reply ends in a printed **reading line** that says what it used and what it cost. The metaphor is a household utility meter, so it needs no explanation for occasional, nontechnical users, and it carries the product's mechanism exactly: top up, hold while running, settle, balance returned.

Density is comfortable where people read (answers at 17px on a fixed 68ch measure) and compact where the meter speaks (readout, reading line, tariff rate: one line, condensed, tabular figures). Surfaces are flat planes separated by 1px hairlines with 6px corners. Meaning comes from printed words and inversion, never from colour alone. Light is the default; dark follows the OS, and every token has a measured counterpart in both themes, gated by `doc/design/check_contrast.py` (all text pairs 4.5:1 or better, control borders and the pulse mark 3:1 or better).

The world refuses the chat category's defaults: no grey chat bubbles for both sides, no glowing AI orb, no gradients, glow or glassmorphism, and no skeuomorphic meter costume (no seven-segment LCD face, screws, dials or knobs).

**Key Characteristics:**
- One backlit panel (the credit readout) on a flat grey faceplate.
- Amber means credit in motion and nothing else.
- State by inversion: selected, pressed, open and primary controls are ink with light text.
- States print themselves as words in the reading line.
- Two type voices: Public Sans for words, Barlow Semi Condensed with tabular figures for numbers and labels.
- Flat planes, 1px hairlines, 6px corners, no blurred shadows.
- A fixed reading measure; wider windows get more margin, not longer lines.
- Three motions only: the pulse, the settle, the drawer.

## Colors

A restrained, near-neutral green-grey faceplate with one sage backlight and one amber signal; two semantic accents in total, each with a single job.

### Primary
- **Printed Ink** (`ink`; dark `ink-dark`): all text, settled amounts, and the fill of every inverted control (primary button, pressed button, current chat, open menu, expanded drawer toggle). Charged amounts are ink, not green: paying is normal, not a victory.
- **Paper on Ink** (`on-ink`; dark `on-ink-dark`): text and icons on inverted controls, and the inset ring on primary-button hover.

### Secondary
- **Backlit Sage** (`readout` / `readout-ink`; dark `readout-dark` / `readout-ink-dark`): the credit readout panel in the top bar and nothing else. The selection highlight (`selection`) reuses the light sage value; in dark it is a deeper sage (`selection-dark`).

### Tertiary
- **Pulse Amber, text** (`pulse`; dark `pulse-dark`): the held amount in the readout, "Holding up to" and "Under review" in reading lines. Darkened from the logo amber so it reads as text at 4.5:1 on surface, ground and readout.
- **Pulse Amber, light** (`pulse-mark`; dark `pulse-mark-dark`): the 8px pulse light, the light in the header brand mark, and the text caret. In light theme this is deliberately darker than the logo file amber (`logo-light`) so the mark holds 3:1 on surface and on the sage readout. Standalone logo files keep `logo-light`; the in-app header mark uses `pulse-mark`.
- **Signal Red** (`danger`; dark `danger-dark`): "No reply" and failure notes, the low-credit warning border and heading, field and form errors, and destructive buttons (red text with a red hairline).

### Neutral
- **Faceplate Grey** (`ground`; dark `ground-dark`): page background and the composer dock. Also the favicon plate, the manifest background and the light `theme-color`.
- **Panel White** (`surface`; dark `surface-dark`): the top bar, rail, composer box, cards, menu panel, inputs and secondary buttons.
- **Sunk Well** (`surface-sunk`; dark `surface-sunk-dark`): the user's prompt block, code, the tariff "MODEL" label cell, and hover wells on buttons and list rows.
- **Muted Print** (`muted`; dark `muted-dark`): secondary text, the reading line, the tariff rate, step numbers, help text, placeholders, the account name.
- **Hairline** (`line`; dark `line-dark`): every divider: under the top bar, the rail edge, reading-line rule, step rules, card borders, table rows.
- **Control Edge** (`line-strong`; dark `line-strong-dark`): borders of controls you operate (buttons, inputs, tariff selector, composer box, menu panel, the phone drawer edge) and the scrollbar thumb. Light value raised to reach 3:1 on surface and ground.

### Named Rules
**The One Light Rule.** Amber means credit in motion (held, holding, under review) and nothing else, anywhere. If a thing is not money moving, it is not amber.

**The One Backlight Rule.** Sage is the credit readout. No other panel, badge or highlight is backlit (the text-selection tint is the single sanctioned echo).

**The Plain Charge Rule.** A settled charge is printed ink. Never colour a charge green or celebrate it.

**The Gate Rule.** A token value changes only if `doc/design/check_contrast.py` still passes in both themes.

## Typography

**Display Font:** Public Sans (variable 100 to 900, self-hosted), with ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto
**Body Font:** Public Sans
**Label/Mono Font:** Barlow Semi Condensed 500 and 600 (self-hosted) for readouts, reading lines, labels and the wordmark; the system monospace stack for code in answers

**Character:** Public Sans is a sober, public-sector grotesk that disappears under long answers; Barlow Semi Condensed is the DIN-lineage faceplate face of meters and signage, used only where the interface reports a figure or names a control.

### Hierarchy
- **Display** (650, 1.75rem, 1.2, -0.015em): the first-run heading only. 1.5rem on phones.
- **Headline** (650, 1.6rem, 1.2, -0.01em): page headings on inherited pages; the auth card heading sets it at 1.5rem.
- **Title** (650, 1.2rem, 1.2): section headings (h2). The chat header title is 600 at 1rem, single line with ellipsis.
- **Body, reading** (400, 17px, 1.65, max 68ch): answers. 16px on phones. Answer headings step down gently (1.3em / 1.15em / 1em at 650); paragraphs 0.9em apart, list items 0.35em. Prompts are 1rem at 1.55.
- **Body, interface** (400, 15px, 1.45, lining figures): everything else.
- **Readout** (Barlow 600, 1.2rem, tabular lining figures): the available amount; unit 500 at 0.9rem; held segment 600 at 0.95rem. Stat values on the Credits page use Barlow 600 at 1.6rem.
- **Reading** (Barlow 500, 0.9rem, 1.4, +0.01em, tabular): the reading line under replies; the tariff rate uses the same voice at 0.875rem (0.8125rem on phones). Model name and amounts step up to 600 ink.
- **Label** (Barlow 600, 0.75rem, +0.06em, uppercase): control and panel labels only: AVAILABLE on the readout, MODEL on the tariff, the CHATS list heading, table column heads (0.8125rem, +0.04em).
- **Step numeral** (Barlow 600, 1.35rem, muted, tabular): the first-run margin numbers.
- **Code** (system mono, 0.86em; blocks 0.86rem/1.55): scrollable blocks, never wrapped mid-token.

### Named Rules
**The Two Voices Rule.** Words are Public Sans; figures and control labels are Barlow Semi Condensed with tabular lining figures. Credit amounts never render in Public Sans proportional figures.

**The Fixed Measure Rule.** Answers and the composer share one measure (68ch). Wider windows get more margin, never longer lines.

## Layout

A 4px base with a seven-step scale (4 / 8 / 12 / 16 / 24 / 32 / 48). The chat screen is a sticky 56px top bar over a two-column grid: a 264px rail and the conversation column, filling the dynamic viewport height. The top bar carries the lockup, then the readout directly beside it, then the account at the far right. The conversation column centres a 68ch measure (plus 2px for borders); the composer dock sits at the bottom on the ground colour and aligns to the same measure. Messages sit 32px apart; the prompt block is right-aligned and capped at 60ch (88%).

The first-run empty state is a column at the reading measure: display heading, the balance sentence, and three steps set in a two-column grid (a 3rem margin column for the numeral, then text), ruled with hairlines above and below each step. This is the one place numbering is used.

Inherited pages (sign in, sign up, Credits, delete confirmation) use a centred 880px page, narrowed to 440px for auth and confirmation.

**At 800px and below:** the rail becomes a fixed drawer (min(86vw, 264px)) below the top bar, opened by a menu icon button; the brand name and the readout's AVAILABLE label are hidden visually but kept for screen readers; the account name is dropped. Reading lines put the model name on its own line. The composer compacts: the tariff selector takes the full width, the full rate, worked example, hold sentence and DeepSeek note are hidden; a single price line with a short hold clause ("Holds at least N per reply; unused credit comes back") remains, the disclosure moves behind a `<details>` labelled "How models and prices work", and when credit is too low the warning replaces the price line. Send and Stop stretch to fill the bar. Nothing scrolls horizontally from 360px; code blocks and tables scroll inside themselves.

## Elevation & Depth

Flat. Depth is expressed by plane colour (ground under surface, sunk wells for prompts and code) and 1px hairlines, never by blurred shadows. The only box-shadows in the build are inset rings that mark state inside an element's own edge.

### Shadow Vocabulary
- **Readout hover ring** (`box-shadow: inset 0 0 0 1px var(--readout-ink)`): the readout is a link to Credits; hovering prints its edge.
- **Primary hover ring** (`box-shadow: inset 0 0 0 2px var(--on-ink)`): an inverted button on hover gets a light inner rule instead of a colour change.
- **Composer focus ring** (`box-shadow: inset 0 0 0 1px var(--ink)` with an ink border): the message box doubles its edge while typing.

### Named Rules
**The Flat Plate Rule.** No blurred or offset drop shadows, anywhere. Menus and the phone drawer separate from the page with a Control Edge border, not a shadow.

## Shapes

One corner language: 6px on every panel and control (buttons, inputs, readout, composer, tariff, cards, prompt, code blocks, list rows, menu panel, notices). Inline code is the only smaller radius (4px). The only circle is the pulse light (8px). Borders are always 1px: Hairline for structure, Control Edge for things you operate, Signal Red for danger. The reading line and step rows divide their segments with 1px vertical and horizontal rules, like a printed statement.

**The logo** is the Pulse bubble: an open, round-capped speech bubble whose tail is a solid dot, the meter's light. The header uses the small optical size (3.4-unit stroke, 7.2-unit light) inline at 24px, ink bubble with a `pulse-mark` light; the auth card sets it at 40px. The favicon is the small symbol on a Faceplate Grey rounded plate with the logo amber, the same in both OS themes. Full usage rules live in `doc/design/brand/logo-usage.md`.

**Icons** are an in-house SVG sprite on a 20-unit grid, 1.75 stroke, round caps and joins: menu, plus, send, stop, more, chevron, close. Rendered at 20px (18px inside buttons), `currentColor`, always paired with a visible or visually hidden word.

## Components

### Buttons
Printed, plain, and inverted when they matter.
- **Shape:** gently squared plate (6px), 40px tall; small 32px.
- **Secondary (default):** Panel White with a Control Edge border and ink text, 600 weight. Hover sinks to Sunk Well; pressed inverts to ink.
- **Primary:** inverted ink with Paper on Ink text (Send, Sign in, Add demo credits). Hover adds a 2px inner light ring; colours do not change.
- **Danger:** red text with a red border on panel (Delete chat in the chat menu).
- **Disabled:** 45% opacity, not-allowed cursor.
- **Text buttons:** underlined ink, 1px underline thickening to 2px on hover (Sign out, Retry).
- **Icon buttons:** 40px square, transparent at rest, sunk on hover, inverted when expanded or open.
- **Focus (all controls):** 2px ink outline, 2px offset.

### Credit Readout (signature)
The one backlit panel. Sage plate, 40px tall, in the top bar beside the lockup and linking to Credits. It prints AVAILABLE (label voice), the amount to four decimals in the readout voice, and "credits". Only while credit is held, a segment appears after a faint vertical rule: a blinking pulse light and the held amount in Pulse Amber with the word "held".
- **The pulse:** the light blinks in hard steps (1.1s cycle, dim to 20% at 55%), like a meter's usage LED, not a soft breathe.
- **The settle:** when a reply finishes, the available figure counts to its new value over 520ms (quartic ease-out), and the held segment turns to readout ink, its light stops, and it reads "X charged" for 3.5s (entering with a 420ms, 3px rise) before returning to the held state or hiding.
- **Reduced motion:** the pulse is steady and the settle is instant.

### Reading Line (signature)
Printed under every reply, above a 1px hairline: model name (ink, 600), tokens in and out, and "N credits charged" (amount in ink), each segment divided by a 1px vertical rule, in the reading voice. While running: a live pulse light and "Holding up to N credits" in amber. Other states are printed words in the same line: "Not charged", "Under review · up to N credits held", "charged after review". Notes below (cut off, filtered, failed, didn't finish) are body text at the measure; a failure leads with "No reply." in red, with **Retry** as a text button.

### Tariff Selector
A native select styled as a faceplate switch: a Control Edge frame whose left cell is a sunk MODEL label, then the select on panel with a drawn chevron. Hover or focus darkens the frame to ink. Beneath it, the rate line in the reading voice prints the per-million rates, a worked example ("A 1,000-token question with a 500-token answer costs N credits") and the minimum hold. When the balance cannot cover the hold, a red-bordered warning with the needed and available figures and an "Add demo credits" link appears.

### Inputs / Fields
- **Style:** Panel White, Control Edge border, 6px, 44px tall, 8px by 12px padding; label above at 600.
- **Hover:** border darkens to ink.
- **Composer:** a panel box with the Control Edge; the textarea is borderless inside it. On focus the box gets an ink border plus an inset 1px ink ring.
- **Error:** red text below the field at 0.875rem, 500.

### Navigation
- **Top bar:** Panel White with a hairline below; lockup (Barlow wordmark with the small symbol), readout, then account name (muted, truncated at 16ch) and Sign out.
- **Rail:** Panel White with a hairline edge; a full-width New chat button, the CHATS label, then chat rows (6px, 8px by 12px, single-line ellipsis). Hover sinks; the current chat is inverted ink at 600. A hairline-topped foot links to Credits & history. On phones it is a drawer that slides in over 240ms (instant with reduced motion).
- **Chat menu:** a "more" icon button opening a panel with a Control Edge border (rename field, then Delete chat).

### Prompt Block
The user's words in a Sunk Well plate, right-aligned, capped at 60ch, pre-wrapped. Replies have no container at all: they are printed on the ground at the measure.

### Cards / Containers
- **Corner Style:** 6px.
- **Background:** Panel White.
- **Shadow Strategy:** none (see Elevation & Depth).
- **Border:** 1px Hairline.
- **Internal Padding:** 24px; auth cards 32px by 24px.

### Inherited surfaces
The Credits page (notice, stat row, data tables) and the delete confirmation inherit these tokens and generic components only; they are not yet full applications of the world and should not be treated as reference compositions.

## Do's and Don'ts

### Do:
- **Do** keep amber for credit in motion only: held amounts, "Holding up to", "Under review", and the pulse light.
- **Do** show state by inversion (ink fill, Paper on Ink text) for primary, pressed, current and open controls.
- **Do** print every state as a word in the reading line; colour is never the only signal.
- **Do** set every credit figure in Barlow Semi Condensed with tabular lining figures.
- **Do** hold answers and the composer to the 68ch measure and give wider windows more margin.
- **Do** separate planes with 1px Hairlines and give operable controls the Control Edge border.
- **Do** use the 6px corner on every panel and control, and the 4px spacing scale.
- **Do** make the pulse steady and the settle instant under `prefers-reduced-motion`.
- **Do** re-run `doc/design/check_contrast.py` after any token change, in both themes.

### Don't:
- **Don't** use blurred or offset drop shadows, gradients, glow or glassmorphism.
- **Don't** backlight anything but the credit readout.
- **Don't** colour a charge green or use amber for warnings, limits or errors.
- **Don't** add motion beyond the pulse, the settle and the drawer.
- **Don't** dress the meter as a costume: no seven-segment LCD face, screws, dials or knobs.
- **Don't** put both sides of the conversation in grey bubbles; replies are printed on the ground.
- **Don't** recolour the logo light except amber or mono, or separate the light from the bubble.
- **Don't** use icon fonts, emoji or pictographic glyphs as icons; use the sprite.
