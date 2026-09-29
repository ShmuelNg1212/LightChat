# Wiki: LightChat

Living documentation. It describes the project **as it exists now**, not as planned. For decisions and their history, see `doc/study/`, `doc/plan/` and `doc/design/`.

## Current state

**LightChat** is a pay-as-you-go chat app for occasional, nontechnical users. They sign up, receive 5.00 demo credits, and chat with three models reached through BUILD LLM Proxy (all answered by DeepSeek Flash). Before sending, they see what a reply could cost. While it's written, they see the credit held. Afterwards they see exactly what it cost, and their chats are saved. It's live at **https://lightchat-five.vercel.app** (Vercel Hobby, with Neon Postgres, in Frankfurt), and it also runs locally.

The product was built as a replica of the Litechat product's core functionality and has since been rebranded as the independent LightChat, with its own identity. See [PRODUCT.md](../../PRODUCT.md).

Working agreement: [AGENTS.md](../../AGENTS.md), mirrored in [CLAUDE.md](../../CLAUDE.md).

## Pages

| Page | Contents |
|---|---|
| [setup.md](setup.md) | Install, `.env` keys, run, test, design checks, operational commands, the assessment package |
| [architecture.md](architecture.md) | Apps, data model, the metered send flow, money and concurrency rules, front end, security |
| [features.md](features.md) | What users and admins can do today, and how failures are handled |
| [external-dependencies.md](external-dependencies.md) | BUILD LLM Proxy contract (sample-verified), Vercel and Neon, connectivity notes, required keys |
| [deployment.md](deployment.md) | The live Vercel deployment: env vars, deploying, rollback, production admin commands, limits |

Real captured proxy responses (redacted) are in [`doc/fixtures/proxy/`](../fixtures/proxy/).

## Identity and design

| Where | What |
|---|---|
| [DESIGN.md](../../DESIGN.md) | **The visual system as built:** "Prepaid Meter" tokens, type, components, states, motion, responsive and accessibility rules. It's the authority for future UI work. |
| [PRODUCT.md](../../PRODUCT.md) | Product truth: users, purpose, capabilities, brand commitments (name, independence, honesty), WCAG 2.2 AA |
| [Identity brief](../design/2026-09-29-1357-lightchat-identity-brief.md) | Why this direction and logo were chosen (approved 2026-09-29) |
| [Logo usage](../design/brand/logo-usage.md) | Logo files, clear space, minimum sizes, backgrounds, provenance |
| `static/brand/` | Logo SVGs, favicon, app icons, `site.webmanifest` |
| `static/fonts/` | Self-hosted Public Sans and Barlow Semi Condensed (SIL OFL 1.1) |
| `.impeccable/` | Impeccable config: design hook, Live Mode target, chat surface brief with its direction contract |

**Naming:** the product is always **LightChat**. Some names deliberately still say "litechat", and they are not user-facing:

| Name | Why it stays |
|---|---|
| Proxy domain `proxy.litechat.ai` | A third-party service |
| `litechat.*` logger names | Internal |
| Historical studies, plans and fixtures | Journal records |

A test (`chat/tests/test_branding.py`) fails if "Litechat" appears on any user-facing page.

## Journal

| Request | Study | Plan | Status |
|---|---|---|---|
| Litechat core functionality | [study](../study/2026-09-29-1243-litechat-core.md) | [plan](../plan/2026-09-29-1258-litechat-core.md) | Done (accepted 2026-09-29) |
| Longer replies and more starting credit | [study](../study/2026-09-29-1347-reply-limit-and-starting-credit.md) | [plan](../plan/2026-09-29-1348-reply-limit-and-starting-credit.md) | Done (accepted 2026-09-29) |
| LightChat rebrand (slice 1) | [study](../study/2026-09-29-1357-lightchat-rebrand.md) | [plan](../plan/2026-09-29-1406-lightchat-rebrand.md) · [brief](../design/2026-09-29-1357-lightchat-identity-brief.md) | Done (accepted 2026-09-29) |
| Assessment submission package | [study](../study/2026-09-29-1456-assessment-package.md) | [plan](../plan/2026-09-29-1456-assessment-package.md) | Done (accepted 2026-09-29) |
| Vercel deployment | [study](../study/2026-09-29-1641-vercel-deployment.md) | [plan](../plan/2026-09-29-1641-vercel-deployment.md) | Done (live 2026-09-29) |
