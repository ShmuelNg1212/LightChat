# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

**Primary:** occasional, nontechnical people who want to use capable AI models now and then without paying for a monthly subscription. They arrive with an ordinary question or task (write something, explain something, summarise something), may not know what a "token" or a "model" is, and care about two things: getting a good answer, and not being surprised by what it cost.

**Situation:** short, irregular sessions on a phone or a laptop. They come back days later and expect their earlier chats and their remaining credit to be where they left them.

**Audience plan (confirmed 2026-09-29):** LightChat is intended for **real public users soon**. It is not yet public. See *Capabilities and Constraints* for what that does and does not mean today.

## Product Purpose

LightChat gives pay-as-you-go access to AI models reached through several providers' interfaces, with no subscription. The core loop:

1. Have credit and understand it.
2. Choose a model with its price in view.
3. Hold a conversation.
4. See what each reply cost and what remains.
5. Return to saved chats.

Success means a first-time user can send a message and understand its cost without help, and never pays for something that didn't arrive or pays twice for the same thing.

## Positioning

Metered, à la carte access where spending is **transparent and safe by construction**. Before each reply, LightChat holds the most that reply could cost, charges only what was actually used, and returns the rest. When usage is unknown, the held amount is reviewed instead of being guessed. Every charge is visible, per reply and in a full credit history. It is honest about what the models are: all current models are answered by DeepSeek Flash through different provider interfaces, and the product says so.

## Operating Context

- Web app, used in desktop and phone browsers. Sessions are signed in (username and password).
- Chats persist server-side; users revisit, rename and delete them.
- An administrator reviews replies whose cost is unknown (stopped or interrupted replies) in the admin, and can change model rates and reply limits.
- Functional reference: the Litechat product (litechat.ai). LightChat is an **independent** product with its own identity (see Brand Commitments).

## Capabilities and Constraints

Implemented and accepted (see `doc/wiki/features.md`, the source of truth):

- **Accounts:** sign-up, sign-in and sign-out; every page requires an account; users see only their own data.
- **Credits:** **demo credits, not real money**. 5.00 at sign-up, and **Add 1.00 demo credits** up to 10.00 available. Balance shown to 4 decimals. Credits page with price table and full history.
- **Models:** exactly three, all at 5.00 input / 20.00 output credits per 1M tokens, with replies up to 25,000 tokens:
  - GPT-5.6 Luna · OpenAI interface
  - Claude Haiku 4.5 · Anthropic interface
  - Gemini 3.8 Flash · Google interface

  All are answered by DeepSeek Flash. A model is offered only when its key is configured.
- **Chat:** streaming replies, sanitized Markdown, model switching mid-chat, per-reply model, tokens and cost. "Held (estimate)" while in progress, "Charged" when settled. Stop, explicit Retry on the latest failed message, and clear states for insufficient credit, busy service, truncation, and "under review".
- **Hard rules:** never double-charge; never overspend; never retry a sent request automatically; unknown usage is held for review, never assumed free; proxy keys never reach the browser.

Not available. Future work must not imply these exist:

- **Real payments**, attachments/uploads, web search, Google sign-in, password reset by email, any public deployment or domain.

Open decisions (undecided; do not assume):

- The launch date, hosting, domain, and whether and when real payments replace demo credits.
- Any LightChat domain or trademark. None is claimed or verified.

Terminology in the UI: "credits" (never a currency symbol), "model", "reply", "chat". Avoid "tokens" as the headline unit; show them as secondary detail.

## Brand Commitments

- **Name:** **LightChat**, exactly this spelling (capital L, capital C, one word). Confirmed by the Gardener.
- **Independence (confirmed 2026-09-29):** no borrowed logos or identity from Litechat, OpenAI, Anthropic or Google; no "official" or partnership claims. Provider names appear only as the interfaces used, alongside the DeepSeek disclosure.
- **Honesty commitments** carried from accepted work: demo credits are labeled as not real money; model backing is disclosed; costs are never hidden.
- The visual identity and logo are **not yet decided**. They are set by the design brief (`doc/design/`), not here.

## Evidence on Hand

- A working, accepted app (this repository). Real, redacted proxy responses are in `doc/fixtures/proxy/`.
- Measured behavior: about 135 tokens/s streaming. A 3,140-token reply cost 0.0638 credits.
- **Absent. Do not fabricate:** testimonials, user counts, reviews, press, benchmarks, uptime figures, real prices in currency, payment-provider logos.

## Product Principles

1. **Cost is never a surprise.** The price is visible before sending, the hold while waiting, and the charge after, always in the same unit.
2. **Say what's true.** Label demo credit as demo; disclose what answers the models; state when a reply failed and whether it cost anything.
3. **The conversation comes first.** Reading and writing the chat is the main task; money and model details support it without crowding it.
4. **Plain words for occasional users.** No jargon in primary labels; technical detail (tokens, rates) is available but secondary.
5. **Safe by construction.** Duplicate clicks, several tabs and dropped connections must never cost extra.

## Accessibility & Inclusion

- **WCAG 2.2 AA** (confirmed 2026-09-29): contrast, full keyboard operation with visible focus, labeled controls, screen-reader announcements for reply completion and errors (not every streamed word), respect for reduced motion. Usable at phone width (from 360 px) without horizontal scrolling.
- **English only** for now.
