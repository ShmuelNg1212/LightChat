# Plan: Deploy LightChat to Vercel
- **Date:** 2026-09-29 16:41
- **Study:** [../study/2026-09-29-1641-vercel-deployment.md](../study/2026-09-29-1641-vercel-deployment.md)
- **Status:** awaiting-approval

The Gardener asked for the Study and Plan together, so both are approved in one step.

## Tasks

### A. Code (local, every commit green on SQLite)
- [ ] 1. Add `psycopg[binary]` to requirements → `build(deps): add the PostgreSQL driver`
- [ ] 2. Make the database settings safe behind a pooler. For Postgres: disable server-side cursors, turn on health checks, and read the connection age from `DB_CONN_MAX_AGE`. Add tests → `feat(config): make Postgres settings safe behind PgBouncer`
- [ ] 3. Install Homebrew PostgreSQL locally and run the **full suite on Postgres**. Fix anything specific to Postgres → `fix(...)` only if needed
- [ ] 4. Make the reply limits configurable: `REPLY_MAX_SECONDS` (default 1200) and `REPLY_CHUNK_TIMEOUT_SECONDS` (default 90). Add tests → `feat(proxy): make reply time limits configurable`
- [ ] 5. Production security, active only when `VERCEL` is set or `HTTPS_ONLY=True`:
  - trust `X-Forwarded-Proto`, SSL redirect, `Secure` cookies, HSTS for one year;
  - build `ALLOWED_HOSTS` from the Vercel system variables;
  - silence mail.E001 with a comment.

  Add tests; `check --deploy` must come back clean → `feat(config): harden settings for HTTPS deployments`
- [ ] 6. `vercel.json`:
  - `regions: ["fra1"]`;
  - `maxDuration: 300` on `config/wsgi.py`;
  - `git.deploymentEnabled: false`;
  - a build command that runs `migrate` over `DATABASE_URL_UNPOOLED`;
  - `excludeFiles` for the tests and the static folder.

  Add `.vercelignore`. Add `.vercel/` to `.gitignore` → `build(vercel): add Vercel project configuration`
- [ ] 7. Update `.env.example` with `DB_CONN_MAX_AGE`, `REPLY_MAX_SECONDS`, `REPLY_CHUNK_TIMEOUT_SECONDS`, `HTTPS_ONLY` and the Neon variables → `docs(env): document deployment variables`

### B. Preview (needs the Gardener's logins and clicks)
- [ ] 8. Create and link the Vercel project with `npx vercel@latest link`. No deploy yet, no Git auto-deploys
- [ ] 9. ⏸ **Gardener:** add Neon (Free, Frankfurt, Production and Preview, Preview branching on) and turn on the automation bypass secret
- [ ] 10. Set the env vars for Production and Preview:
  - `SECRET_KEY`: random, different per environment;
  - the three proxy keys, piped from `.env`;
  - `REPLY_MAX_SECONDS=270`;
  - `REPLY_CHUNK_TIMEOUT_SECONDS=25`;
  - `DB_CONN_MAX_AGE=0`.

  No commit; nothing in Git
- [ ] 11. `vercel deploy` (**preview only**). Check the build log: migrations applied, `collectstatic` ran, Python 3.14
- [ ] 12. Run the scripted preview smoke test (a local script in the scratchpad, not committed; it calls the metered proxy). It checks:
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
- [ ] 13. Check the mobile layout at 360 px and 390 px with a headless browser (Playwright through npx, local, free), plus the drawer
- [ ] 14. Set plan `Status: awaiting-rendezvous`. ⏸ **Rendezvous 1:** preview URL, results and open issues
### C. Production (only after acceptance)
- [ ] 15. `vercel deploy --prod` from the accepted commit. The production build migrates the production Neon database
- [ ] 16. ⏸ **Gardener:** `createsuperuser` against production (I give you the exact command)
- [ ] 17. Production smoke test: health, sign-up, one short reply (1 paid call), persistence
- [ ] 18. Set plan `Status: awaiting-rendezvous`. ⏸ **Rendezvous 2:** the live URL
- [ ] 19. Sync:
  - add `doc/wiki/deployment.md` (setup, env vars, deploying, migrations, rollback, reconciliation, limits);
  - update setup, architecture, external-dependencies and README.

  → `docs(wiki): sync after vercel-deployment`

**Paid proxy calls in total:** about 6 on the preview and 1 in production, plus retries if something fails. Each is short except the one long reply.

## Blocked On
- Approval of the Study and this Plan, and your answers on **plan (Hobby)** and **region (Frankfurt)**.
- Task 8: your `npx vercel@latest login`.
- Task 9: Neon setup and the bypass secret (dashboard).
- Task 16: your `createsuperuser` run.
