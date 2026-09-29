# Plan: Longer replies and more starting credit

- **Date:** 2026-09-29 13:48
- **Study:** [../study/2026-09-29-1347-reply-limit-and-starting-credit.md](../study/2026-09-29-1347-reply-limit-and-starting-credit.md) (see its Review)
- **Status:** done

> **Approved 2026-09-29.** The Gardener replied "approved".

## Decisions (from the study review)

- Reply writing is capped at **25,000 output tokens** (0.50 credits at 20.00 per 1M), per model. Reading the conversation is charged on top.
- New accounts start with **5.00** credits. **+1.00** top-ups work up to **10.00** available.
- Existing wallets below 5.00 (today only `shm`) receive a one-time grant up to 5.00, memo "Starting credit raised to 5.00".

## Tasks

- [x] 1. Add a `--no-save` option to `probe_proxy`, so a probe can check a setting without overwriting the committed fixtures. → `chore(proxy): let probe_proxy run without saving fixtures`
- [x] 2. **Paid:** run `probe_proxy --no-save --max-tokens 25000` (3 requests with a one-line prompt, about 190 tokens each). If an interface rejects 25,000, find its largest accepted value with at most 2 more probes on that interface. Record the result in `external-dependencies.md`. → `docs(wiki): record proxy output-token limits`
- [x] 3. Data migration: set `max_output_tokens` on the three seeded models to 25,000 (or the verified per-interface maximum from task 2). Add a test that the hold for a one-line prompt is at least 0.50 and the price table shows the new limit. → `feat(catalog): allow replies up to 25,000 tokens`
- [x] 4. Raise the per-reply time limit (`MAX_DURATION`) from 5 to 20 minutes. The 90 s silence timeout stays. Add a test. → `feat(proxy): allow replies to stream for up to 20 minutes`
- [x] 5. Sign-up grant 5.00; top-up cap 10.00; update the tests that assumed 1.00 and 5.00. → `feat(billing): start new accounts with 5.00 credits`
- [x] 6. Data migration: grant each existing wallet whose available credit is below 5.00 the difference, as a ledger `grant` entry with the memo above, so the balance still equals the ledger total. Add a test. → `feat(billing): raise existing accounts to 5.00 credits`
- [x] 7. Verify: full test suite. Apply the migrations to the development database and confirm `shm` shows 5.0000. **Paid:** one live long reply ("write about 3,000 words") to confirm the proxy doesn't cut replies off below the new limit, and to measure its speed. Browser check that the Credits page and the cut-off notice show the new limit. Set Status to `awaiting-rendezvous`. → `docs(plan): mark reply-limit-and-starting-credit ready for rendezvous`

## Outcome

Accepted by the Gardener on 2026-09-29 ("everything works"). The wiki was synced in `docs(wiki): sync after reply-limit-and-starting-credit`.

## Execution notes

- **Task 2:** all three interfaces accepted `max_tokens` = 25,000 (HTTP 200, normal completion). One OpenAI run failed four connection attempts in a row before anything was sent (no cost) and succeeded when rerun.
- **Task 7:** the development database was migrated. `shm` now has 5.0000 available, with a ledger grant "Starting credit raised to 5.00". All three models are at 25,000 tokens.
- **Task 7 live check (paid):** a new account started at 5.0000 and top-up was enabled. The Credits page shows "25,000 tokens" and "stop at 10.00". A GPT-interface request for a 3,000-word essay completed normally at **3,140 output tokens** (past the old 2,048 cut-off) in **23 s**, about 135 tokens/s, and was charged 0.0638 credits, with the rest of the hold returned. At that speed a full 25,000-token reply takes about 3 minutes, well inside the new 20-minute limit.
- **Task 7:** the check left an account `vine-check` (4.9362 credits) in the development database. It can't be deleted through the admin: the ledger protects wallet history, so deleting any user who has credit history fails. This gap existed before this change and is reported, not fixed.
- **Paid usage:** 3 probe requests (~190 tokens each) and 1 long reply (199 in, 3,140 out).
- **Test suite:** 115 tests, all passing.

## Paid upstream usage this plan will make

At most 5 probe requests of about 190 tokens, plus 1 long reply of about 4,000–6,000 output tokens. All of it uses the shared proxy account, not users' demo credit.

## Blocked On

Nothing. The keys are in `.env`. If the proxy rejects 25,000 on an interface, task 2 finds that interface's limit and the Rendezvous reports it.
