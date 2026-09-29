# Plan: Longer replies and more starting credit

- **Date:** 2026-09-29 13:48
- **Study:** [../study/2026-09-29-1347-reply-limit-and-starting-credit.md](../study/2026-09-29-1347-reply-limit-and-starting-credit.md) (see its Review)
- **Status:** awaiting-approval

## Decisions (from the study review)

- Reply writing is capped at **25,000 output tokens** (0.50 credits at 20.00 per 1M), per model. Reading the conversation is charged on top.
- New accounts start with **5.00** credits. **+1.00** top-ups work up to **10.00** available.
- Existing wallets below 5.00 (today only `shm`) receive a one-time grant up to 5.00, memo "Starting credit raised to 5.00".

## Tasks

- [ ] 1. Add a `--no-save` option to `probe_proxy`, so a probe can check a setting without overwriting the committed fixtures. → `chore(proxy): let probe_proxy run without saving fixtures`
- [ ] 2. **Paid:** run `probe_proxy --no-save --max-tokens 25000` (3 requests with a one-line prompt, about 190 tokens each). If an interface rejects 25,000, find its largest accepted value with at most 2 more probes on that interface. Record the result in `external-dependencies.md`. → `docs(wiki): record proxy output-token limits`
- [ ] 3. Data migration: set `max_output_tokens` on the three seeded models to 25,000 (or the verified per-interface maximum from task 2). Add a test that the hold for a one-line prompt is at least 0.50 and the price table shows the new limit. → `feat(catalog): allow replies up to 25,000 tokens`
- [ ] 4. Raise the per-reply time limit (`MAX_DURATION`) from 5 to 20 minutes. The 90 s silence timeout stays. Add a test. → `feat(proxy): allow replies to stream for up to 20 minutes`
- [ ] 5. Sign-up grant 5.00; top-up cap 10.00; update the tests that assumed 1.00 and 5.00. → `feat(billing): start new accounts with 5.00 credits`
- [ ] 6. Data migration: grant each existing wallet whose available credit is below 5.00 the difference, as a ledger `grant` entry with the memo above, so the balance still equals the ledger total. Add a test. → `feat(billing): raise existing accounts to 5.00 credits`
- [ ] 7. Verify: full test suite. Apply the migrations to the development database and confirm `shm` shows 5.0000. **Paid:** one live long reply ("write about 3,000 words") to confirm the proxy doesn't cut replies off below the new limit, and to measure its speed. Browser check that the Credits page and the cut-off notice show the new limit. Set Status to `awaiting-rendezvous`. → `docs(plan): mark reply-limit-and-starting-credit ready for rendezvous`

## Paid upstream usage this plan will make

At most 5 probe requests of about 190 tokens, plus 1 long reply of about 4,000–6,000 output tokens. All of it uses the shared proxy account, not users' demo credit.

## Blocked On

Nothing. The keys are in `.env`. If the proxy rejects 25,000 on an interface, task 2 finds that interface's limit and the Rendezvous reports it.
