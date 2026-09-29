# Plan: Deploy LightChat to Vercel
- **Date:** 2026-09-29 16:41
- **Study:** [../study/2026-09-29-1641-vercel-deployment.md](../study/2026-09-29-1641-vercel-deployment.md)
- **Status:** done

The Gardener asked for the Study and Plan together, so both are approved in one step.

## Tasks

### A. Code (local, every commit green on SQLite)
- [x] 1. Add `psycopg[binary]` to requirements → `build(deps): add the PostgreSQL driver`
- [x] 2. Make the database settings safe behind a pooler. For Postgres: disable server-side cursors, turn on health checks, and read the connection age from `DB_CONN_MAX_AGE`. Add tests → `feat(config): make Postgres settings safe behind PgBouncer`
- [x] 3. Install Homebrew PostgreSQL locally and run the **full suite on Postgres**. Fix anything specific to Postgres → `fix(...)` only if needed
- [x] 4. Make the reply limits configurable: `REPLY_MAX_SECONDS` (default 1200) and `REPLY_CHUNK_TIMEOUT_SECONDS` (default 90). Add tests → `feat(proxy): make reply time limits configurable`
- [x] 5. Production security, active only when `VERCEL` is set or `HTTPS_ONLY=True`:
  - trust `X-Forwarded-Proto`, SSL redirect, `Secure` cookies, HSTS for one year;
  - build `ALLOWED_HOSTS` from the Vercel system variables;
  - silence mail.E001 with a comment.

  Add tests; `check --deploy` must come back clean → `feat(config): harden settings for HTTPS deployments`
- [x] 6. `vercel.json`:
  - `regions: ["fra1"]`;
  - `maxDuration: 300` on `config/wsgi.py`;
  - `git.deploymentEnabled: false`;
  - a build command that runs `migrate` over `DATABASE_URL_UNPOOLED`;
  - `excludeFiles` for the tests and the static folder.

  Add `.vercelignore`. Add `.vercel/` to `.gitignore` → `build(vercel): add Vercel project configuration`
- [x] 7. Update `.env.example` with `DB_CONN_MAX_AGE`, `REPLY_MAX_SECONDS`, `REPLY_CHUNK_TIMEOUT_SECONDS`, `HTTPS_ONLY` and the Neon variables → `docs(env): document deployment variables`

### B. Preview (needs the Gardener's logins and clicks)
- [x] 8. Create and link the Vercel project with `npx vercel@latest link`. No deploy yet, no Git auto-deploys
- [x] 9. ⏸ **Gardener:** add Neon (Free, Frankfurt, Production and Preview, Preview branching on) and turn on the automation bypass secret
- [x] 10. Set the env vars for Production and Preview:
  - `SECRET_KEY`: random, different per environment;
  - the three proxy keys, piped from `.env`;
  - `REPLY_MAX_SECONDS=260`;
  - `REPLY_CHUNK_TIMEOUT_SECONDS=25`;
  - `DB_CONN_MAX_AGE=0`.

  No commit; nothing in Git
- [x] 11. `vercel deploy` (**preview only**). Check the build log: migrations applied, `collectstatic` ran, Python 3.14
- [x] 12. Run the scripted preview smoke test (a local script in the scratchpad, not committed; it calls the metered proxy). It checks:
  - health;
  - `Secure` cookies and HSTS;
  - sign-up with 5.00 credits, then sign-in;
  - one short reply per model (3 paid calls): time to first byte vs. last byte, to prove it streams;
  - the charge and ledger;
  - a reload that shows the chat was saved;
  - a duplicate request ID charged once;
  - Stop (1 paid call);
  - a static CSS file and a font load from the CDN;
  - `.env` and `db.sqlite3` are not served;
  - one long reply (~3,000 tokens, 1 paid call) to check streaming past 20 s.
- [x] 13. Check the mobile layout at 360 px and 390 px with a headless browser (Playwright through npx, local, free), plus the drawer
- [x] 14. Set plan `Status: awaiting-rendezvous`. ⏸ **Rendezvous 1:** preview URL, results and open issues
### C. Production (only after acceptance)
- [x] 15. `vercel deploy --prod` from the accepted commit. The production build migrates the production Neon database
- [ ] 16. ⏸ **Gardener:** `createsuperuser` against production (I give you the exact command)
- [x] 17. Production smoke test: health, sign-up, one short reply (1 paid call), persistence
- [x] 18. Set plan `Status: awaiting-rendezvous`. ⏸ **Rendezvous 2:** the live URL
- [x] 19. Sync:
  - add `doc/wiki/deployment.md` (setup, env vars, deploying, migrations, rollback, reconciliation, limits);
  - update setup, architecture, external-dependencies and README.

  → `docs(wiki): sync after vercel-deployment`

**Paid proxy calls in total:** about 6 on the preview and 1 in production, plus retries if something fails. Each is short except the one long reply.

## Blocked On
- Approval of the Study and this Plan, and your answers on **plan (Hobby)** and **region (Frankfurt)**.
- ~~Task 8: your `npx vercel@latest login`.~~ Already logged in.
- Task 9: Neon setup and the bypass secret (dashboard).
- Task 16: your `createsuperuser` run.

## Notes
- Task 3: the full suite (135 tests at the time) passed on local PostgreSQL 17 with no changes needed.
- Task 4: the reply cap on Vercel is **260 s** instead of the Study's ~270 s. The worst case is the cap plus one 25 s wait between chunks, which is 285 s, safely under the 300 s function limit.
- Task 6 also added a guard (`271c9d0`): on Vercel the app refuses to start without `DATABASE_URL`, so it can never quietly run on a throwaway SQLite file.
- Task 8: created a new project, `lightchat`, under `shmuelng8310-5097s-projects` (Hobby). The existing `digitalcafe` project was not touched. The CLI created it with the generic preset, so `vercel.json` now pins `"framework": "django"` (`885b80f`). The CLI's own `.gitignore` edit was reverted, because the existing rules already cover `.vercel/` and `.env.local`.
- Task 10 was done before task 9, because it doesn't depend on Neon. Production and Preview each hold `SECRET_KEY` (random, different per environment, sensitive), the three `BUILD_*` keys (sensitive, piped from `.env`), `REPLY_MAX_SECONDS=260`, `REPLY_CHUNK_TIMEOUT_SECONDS=25` and `DB_CONN_MAX_AGE=0`.
- **Incident, task 11 (2026-09-29 ~17:05):** `vercel deploy` without `--prod` created a **production** deployment, because Vercel always makes a new project's first deployment production (docs: /docs/deployments/environments#first-deployment). The Study missed this.
  - Its build ran migrations on the production Neon database. The schema is empty and the migrations would run at launch anyway.
  - It was public at `lightchat-five.vercel.app` for about 3 minutes, because Standard Protection leaves production domains open.
  - It was removed with `vercel rm`, and the URL now returns 404. Whether anyone signed up in that window can't be read from the CLI, because Neon's variables are sensitive.
  - The project still has no production target, so any next deploy would again be production. Paused for the Gardener's decision.
- **Gardener decision (2026-09-29):** "protect my deployments temporarily while testing. go ahead and go-live once tests are complete and dont return failures."
  - Deployment Protection is set to **All Deployments** (Vercel Authentication, free on Hobby). Every URL, production included, needs a Vercel login.
  - A private bootstrap production deployment lets later `vercel deploy` runs create real previews.
  - **Rendezvous 1 is waived:** if every preview test passes, go live without pausing. That means deploying production and restoring **Standard Protection**, which makes the production domain public. Any failure stops the go-live and is reported.
- The CLI's permission classifier blocked the bootstrap `vercel deploy --prod`. The Gardener has to run it or allow it.
- Task 9 (Gardener): Neon Free was connected to Production and Preview, and the automation bypass secret was turned on.
- Task 15 was run by the Gardener: the bootstrap `vercel deploy --prod` built `ce1e0fe`. The preview (`lightchat-dyd1wc615-…`) was built from the **same commit**, so after the preview passed, going live only needed Deployment Protection restored to Standard (`all_except_custom_domains`), with no second production build. `https://lightchat-five.vercel.app` is now public, and preview and deployment URLs still need a Vercel login.
- **Neon preview branching did not happen for CLI deploys.** The preview deployment got no branch-specific `DATABASE_URL`, so **preview and production share one database.** The preview build reported "No migrations to apply". Test data now in production: the users `smoke7bceb75b` (one Stop-test reply left `needs_reconciliation`, with its hold kept), `smoke0f61ad88`, and one `mobile…` account from the phone check.
- Preview results: smoke test **36/36**, phone checks **17/17**. The three models, the charges and ledger, the double-send check, Stop, saved chats, secure cookies, HSTS, the HTTP→HTTPS redirect, static files from the CDN, secret files not served, and no key in any response.
  - Streaming: 2,401 deltas over 16.9 s for a ~2,000-word reply. First byte in about 0.3 s, first token in about 1 s.
  - The long reply finished in 17.9 s, so streaming past 20 s wasn't observed. Incremental delivery is proven, and the 300 s limit is untested in practice.
- Production results: **28/28** (one paid reply).
- Paid proxy calls: 7 (5 short, 1 stopped, 1 long, about 3,000 output tokens) plus 2 short on production.
- Task 16 is still open: the Gardener runs `createsuperuser` against production (steps in `doc/wiki/deployment.md`).
- Sync done. The only open item is task 16 (the Gardener's `createsuperuser`), which is a Gardener action, not code.
