# Wiki: Litechat replica

Living documentation. It describes the project **as it exists now**, not as planned. For decisions and their history, see `doc/study/` and `doc/plan/`.

## Current state

Litechat is a pay-as-you-go chat app. Users sign up, receive 5.00 demo credits, and chat with three models reached through BUILD LLM Proxy (all answered by DeepSeek Flash). They see each reply's cost and their remaining balance, and their chats are saved. It runs locally. It is not deployed yet.

Working agreement: [AGENTS.md](../../AGENTS.md), mirrored in [CLAUDE.md](../../CLAUDE.md).

## Pages

| Page | Contents |
|---|---|
| [setup.md](setup.md) | Install, `.env` keys, run, test, operational commands |
| [architecture.md](architecture.md) | Apps, data model, the metered send flow, money and concurrency rules, security |
| [features.md](features.md) | What users and admins can do today, and how failures are handled |
| [external-dependencies.md](external-dependencies.md) | BUILD LLM Proxy contract (sample-verified), connectivity notes, required keys |

Real captured proxy responses (redacted) are in [`doc/fixtures/proxy/`](../fixtures/proxy/).

## Journal

| Request | Study | Plan | Status |
|---|---|---|---|
| Litechat core functionality | [study](../study/2026-09-29-1243-litechat-core.md) | [plan](../plan/2026-09-29-1258-litechat-core.md) | Done (accepted 2026-09-29) |
| Longer replies and more starting credit | [study](../study/2026-09-29-1347-reply-limit-and-starting-credit.md) | [plan](../plan/2026-09-29-1348-reply-limit-and-starting-credit.md) | Done (accepted 2026-09-29) |
| LightChat rebrand (slice 1) | [study](../study/2026-09-29-1357-lightchat-rebrand.md) | [plan](../plan/2026-09-29-1406-lightchat-rebrand.md) · [brief](../design/2026-09-29-1357-lightchat-identity-brief.md) | Study + plan awaiting approval |
