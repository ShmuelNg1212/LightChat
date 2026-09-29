# Architecture

One Django 6.1 project using server-rendered templates, with one small vanilla-JavaScript file for streaming. SQLite runs locally, and PostgreSQL can be used through `DATABASE_URL`.

## Apps

| App | Responsibility | Key files |
|---|---|---|
| `config` | Settings (from `.env`), root URLs, health check `/healthz` | `settings.py`, `urls.py` |
| `accounts` | Custom `User` (AbstractUser), sign-up/login/logout. `LoginRequiredMiddleware` protects every page by default | `models.py`, `views.py`, `forms.py` |
| `billing` | Wallets, append-only ledger, demo top-ups, Credits page | `models.py`, `services.py`, `money.py` |
| `catalog` | `ModelOffering`: the selectable models and their demo rates | `models.py`, `migrations/0002_seed_proxy_models.py` |
| `proxy` | HTTP client for BUILD LLM Proxy: SSE parser and one adapter per interface | `client.py`, `sse.py`, `types.py`, `adapters/` |
| `chat` | Conversations, messages, the metered generation lifecycle, streaming endpoint, reconciliation | `models.py`, `services.py`, `views.py`, `markdown.py` |

Templates are in `templates/`, and CSS and JS in `static/` (`css/app.css`, `js/chat.js`).

## Data model

```
User ─1:1─ Wallet ─1:n─ LedgerEntry            (append-only)
  │
  ├─1:n─ Conversation ─1:n─ Message             (role: user | assistant)
  │                     └─1:n─ Generation ──→ ModelOffering (nullable)
  └─1:n─ Generation ── user_message ──→ Message
                    └─ assistant_message ─1:1→ Message
```

- **Money** is integer **micro-credits** (µcr, 1 credit = 1,000,000 µcr). No floats. `billing/money.py` converts and formats, rounding costs up.
- **Wallet:** `balance` (settled) and `held` (reserved). Spendable = `balance − held`. Amounts: sign-up grant `SIGNUP_GRANT_MICRO` (5.00), top-up `TOPUP_AMOUNT_MICRO` (1.00) up to `TOPUP_MAX_AVAILABLE_MICRO` (10.00), all in `config/settings.py`.
- **LedgerEntry:** kind (`grant`, `topup`, `hold`, `release`, `charge`, `adjust`), balance change, held change, and snapshots after the change. A test checks that the wallet always equals the sum of its entries. The admin view is read-only. `LedgerEntry.wallet` is `PROTECT`, so deleting a user with any history fails. Credit changes to existing users go through the ledger, as in the data migration `billing/0002_raise_existing_to_five`.
- **Generation:** one metered request. It stores a **price snapshot** (model label, provider, upstream ID, rates, max output tokens), the `reserved` hold, the final `charged`, token counts, status, finish reason and error. It is unique per `(user, client_request_id)`. Deleting a conversation keeps its generations (and so the ledger) intact.

## Sending a message (data flow)

```
browser ──POST /send/ (JSON, CSRF header)──▶ chat.views.send
   1. services.start(): one short transaction
        refuse duplicate request_id · check model available · ≤1 active reply per chat, ≤3 per user
        create chat/user message · build history · compute hold · billing.hold()
        create empty assistant Message + Generation(pending)
   2. services.run(): no transaction open while streaming
        proxy.client.stream_reply() ──httpx──▶ proxy.litechat.ai
        yield deltas → NDJSON {"type":"delta"} to browser
   3. finalize: one short transaction
        completed       → settle(charge actual usage at snapshot rates, release the rest)
        certain no-cost → release (400/401/403/404/413/422/429, connection never made)
        usage unknown   → keep hold, status needs_reconciliation
   4. {"type":"end"} carries the server-rendered message HTML and the new balance
```

The response is NDJSON over `StreamingHttpResponse` from a **sync (WSGI) view**. Each active stream holds one server thread, which is acceptable at this scale.

### Credit hold (reservation)

hold = ⌈input bound × input rate⌉ + ⌈max_output_tokens × output rate⌉, where input bound = 1,024 + Σ(UTF-8 bytes + 16) over the history sent. A token is never shorter than a byte, and the 1,024 covers the proxy's hidden prompt (about 175 tokens observed). If a charge ever exceeds the hold, it is still applied and the generation is flagged `overage`.

### Concurrency safety

Every wallet change is a conditional `UPDATE … WHERE balance − held >= amount` in a short transaction, followed by a ledger insert. Duplicates are stopped by the unique `(user, client_request_id)` constraint. SQLite runs with `transaction_mode=IMMEDIATE`, a 20 s busy timeout and WAL, so concurrent writers wait instead of failing. Threaded tests show parallel tabs cannot overspend or double-charge.

### Never retry a sent request

The proxy client uses `httpx.HTTPTransport(retries=3)`, which retries **connection attempts only** (nothing was sent). A request that was sent is never retried, following the proxy docs. Timeouts are 5 s to connect, 90 s between chunks, and 20 minutes per reply (sized for the 25,000-token limit).

### Stop and disconnects

**Stop** calls `POST /g/<id>/cancel/`, which sets `cancel_requested`. The stream loop checks it every 0.5 s. If the service stays silent, the browser aborts after 5 s. If the browser disconnects, the server closes the response generator, and the generation is marked `needs_reconciliation`. Partial text is always saved.

### Reconciliation

Generations in `needs_reconciliation` keep their hold. In `/admin/` → Generations, the actions **charge the held amount** and **release the hold** settle each one exactly once (claimed by a conditional status update). `reconcile_stale_generations` flags replies whose worker died.

## Conversation context

`services.history_for()` sends each earlier prompt only if its reply **completed**, together with that reply. Failed or interrupted exchanges are left out. Adapters merge neighboring messages with the same role, so roles alternate. History is plain text, so switching models mid-chat works on any interface.

## Rendering and security

- Replies are rendered with `markdown-it-py` (CommonMark plus tables and strikethrough, raw HTML **off**), then sanitized by `nh3`, which allows a fixed tag list and http/https/mailto links with `rel="noopener noreferrer nofollow"`. While streaming, text is shown as plain `textContent`.
- Every conversation lookup goes through `chat.views.owned()` / `owner=request.user`, so another user's chat returns 404.
- Keys live only in settings and the proxy client. A test checks that they never appear in any page or stream.
- The `litechat.*` loggers record IDs, statuses and amounts, never prompts, replies or headers. The admin shows conversation metadata only.
