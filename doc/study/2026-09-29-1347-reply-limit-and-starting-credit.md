# Study: Longer replies and more starting credit

- **Date:** 2026-09-29 13:47
- **Request:** "Increase the limit so that each response can use up to 0.5 credits. Also make the available credits 5 and keep the option to add 1 credit. Follow the workflow."
- **Status:** approved (see Review)

## Intended Outcome

Replies can be much longer before being cut off, up to about 0.5 credits of writing each, and users start with enough credit to use that comfortably. The demo top-up stays.

Acceptance criteria (testable from the outside):

- A reply can run to the new limit (proposed: 25,000 output tokens, i.e. 0.50 credits at the current 20.00 per 1M output rate) instead of stopping at 2,048 tokens. The cut-off notice, the Credits page's price table and the "Up to X credits held" estimate all show the new numbers.
- A long reply isn't cut off by the app's own time limit while it's still arriving.
- A new account starts with **5.00** demo credits.
- **Add 1.00 demo credits** still works for a user who has 5.00, up to the new cap (see question 2).
- Users are still charged only for what the model writes; the unused part of the hold is returned, as today.
- If the proxy refuses the larger limit on any interface, that model is not offered with a limit it can't honor.

## Current State

See [architecture.md](../wiki/architecture.md) and [features.md](../wiki/features.md).

- **Reply limit:** `ModelOffering.max_output_tokens` = 2,048 for all three models, seeded by `catalog/migrations/0002_seed_proxy_models.py` and editable in the admin. The hold for the reply part is `max_output_tokens × output_rate` (currently 2,048 × 20 µcr = 0.0410 credits).
- **Reply duration:** `proxy/client.py` stops any reply after `MAX_DURATION = 300` s and marks it for reconciliation. The proxy's streaming speed hasn't been measured, but a 25,000-token reply would very likely take longer than 5 minutes.
- **Credits:** `config/settings.py` has `SIGNUP_GRANT_MICRO = 1.00`, `TOPUP_AMOUNT_MICRO = 1.00`, `TOPUP_MAX_AVAILABLE_MICRO = 5.00`. With a 5.00 start and the current cap, the top-up button would be disabled until the user spends 1.00.
- **Existing accounts:** one (`shm`, 0.9198 available). A grant change affects only new sign-ups unless existing wallets are topped up deliberately.

## Options & Tradeoffs

**Reply limit.** What "up to 0.5 credits" should cap:

| Option | Pros | Cons | Effort | Risk |
|---|---|---|---|---|
| A. Cap the **reply's writing** at 0.50: `max_output_tokens` = 25,000 | Matches "each response"; simple; cost of reading the conversation stays separate and predictable | Total charge for a reply in a very long chat can exceed 0.50 (reading cost is extra) | Small | Low |
| B. Cap the **whole reply cost** (reading + writing) at 0.50: shrink the writing allowance as the chat grows | A hard 0.50 ceiling per reply | Long chats get shorter possible replies; harder to explain; more code | Medium | Medium |
| C. Only edit the admin value | No code | Loses the change on a fresh database; doesn't fix the 5-minute cut-off | Tiny | Medium |

**Top-up cap** with a 5.00 start:

| Option | Pros | Cons |
|---|---|---|
| D. Raise the cap to **10.00** | "Add 1 credit" works right away and keeps working | Demo users can hold more |
| E. Keep the cap at 5.00 | Unchanged rule | The button stays disabled until a user spends 1.00 |

## Recommendation

- **A:** a data migration sets `max_output_tokens` to **25,000** on the three seeded models, so fresh databases get it too. The admin stays the place to fine-tune.
- Raise `MAX_DURATION` to fit the longest reply (proposed **20 minutes**; the per-chunk silence timeout of 90 s stays). Streaming holds one server thread per reply, which is fine locally. It's noted for any future deployment.
- **Sign-up grant: 5.00.** Keep top-up at **+1.00** with option **D** (cap 10.00).
- Existing accounts are unchanged unless you choose otherwise (question 3). A top-up to 5.00, if chosen, is recorded as a normal ledger grant with a clear memo.
- Before changing anything, verify with **cheap paid probes** that each interface accepts `max_tokens` = 25,000 (a one-line prompt; cost ≈ 190 tokens each). Any interface that rejects it gets the largest value it accepts, found by the same probe.
- The UI text already reads the limit from the model, so the cut-off notice and price table update without template changes. Tests cover the new hold and the duration cap.

## Exogenous Inputs

| Input | Why needed | Status | Owner |
|---|---|---|---|
| Proxy's maximum output tokens per interface | A limit above it would make every reply fail | **needed**: not documented; verify with probes during Execute (3 paid requests, ~190 tokens each) | Vine |
| Proxy streaming speed for long replies | Sets a safe `MAX_DURATION` | **assumed** ≥ 25 tokens/s (25,000 tokens in under 20 min); checked by one optional long-reply test | Vine |
| Product choices below | Define the rules | needed | Gardener |

## Risks & Open Questions

1. **What does "up to 0.5 credits" cap?** Recommended: the reply's *writing* (A, 25,000 tokens), with reading the conversation charged on top. Choose B for a hard 0.50 per reply in total.
2. **Top-up cap:** raise to 10.00 so "add 1 credit" works from a 5.00 start (D, recommended), or keep 5.00 (E).
3. **Existing account (`shm`):** leave it as is (recommended; it can use the top-up button), or grant it up to 5.00?
4. **Actual length vs. limit:** the model may still end long replies on its own well before 25,000 tokens. The limit allows longer replies but doesn't force them.
5. **Proxy limits:** if an interface accepts less than 25,000, its model gets a lower limit and the plan's Rendezvous reports it.
6. **Upstream cost:** long replies consume more of the shared proxy account's budget (outside users' demo credit). No budget was given; the plan's live verification uses at most one long reply.

---

## Review (2026-09-29 13:48)

**Outcome:** approved, with the Gardener's answers:

1. The 0.5-credit cap applies to the **reply's writing** (option A): `max_output_tokens` = 25,000, with reading charged on top.
2. The top-up cap is raised to **10.00** (option D); top-ups stay +1.00.
3. The existing account `shm` is **topped up to 5.00** as a one-time grant recorded in its credit history. This is implemented for every existing wallet below 5.00 (today only `shm`), so it behaves the same on any copy of the database.
