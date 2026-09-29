# Study: Deploy LightChat to Vercel
- **Date:** 2026-09-29 16:41
- **Request:** "Prepare and deploy LightChat to Vercel." Check Vercel's current docs for streaming, authentication, database persistence, static assets and runtime limits, and don't assume the existing architecture works unchanged. Keep secrets server-side and out of Git. Deploy a preview and test it, then pause for acceptance before production. No purchases, domain changes or replacing existing production deployments without approval.
- **Status:** approved

## Intended Outcome
LightChat runs on Vercel with the same behavior it has locally, for example `https://lightchat-<hash>.vercel.app`.

Acceptance criteria (all testable in a browser):
- Sign up, sign in and sign out work over HTTPS. Session and CSRF cookies are `Secure`.
- Chats, messages and credit history survive a redeploy and a cold start.
- Each of the three models replies, and the text **streams in** instead of arriving all at once.
- The credit readout, reading line and Credits page show a hold, then a charge, and the ledger balances.
- **Stop** works. A duplicate send is charged once.
- Pages work at 360 px wide, including the chat drawer on a phone.
- The admin at `/admin/` works (it's used to reconcile held replies).
- Proxy keys and `SECRET_KEY` never appear in Git, in pages or in the deployed file listing.
- Nothing reaches production until the preview has been accepted.

## Current State
Sources: [architecture.md](../wiki/architecture.md), [setup.md](../wiki/setup.md) and `config/settings.py`.
- The app is Django 6.1 on **WSGI** and Python 3.14.
- Replies stream as NDJSON through `StreamingHttpResponse` from a sync view. One reply can run up to **20 minutes** (`proxy/client.py`: `MAX_DURATION`, with a 90 s read timeout between chunks).
- The database is **SQLite** by default. Postgres is already supported through `DATABASE_URL` (`dj-database-url`), but no Postgres driver is installed and the tests have only run on SQLite.
- Concurrency safety relies on conditional `UPDATE`s and a unique request ID. Both work the same way on Postgres.
- **Stop** works by polling a database flag every 0.5 s during a stream. It works across servers, but each poll waits on a round trip to the database.
- Static files are in `static/` and `STATIC_ROOT` is set. The fonts are self-hosted.
- Sign-in uses Django usernames and passwords. There is **no OAuth**, so no callback URLs are needed.
- `check --deploy` currently reports:
  - mail.E001 (console email backend; no email is ever sent);
  - no HSTS;
  - no SSL redirect;
  - session and CSRF cookies not marked `Secure`.
- There's no Vercel CLI, no linked project and no Vercel login on this machine.

## What Vercel supports today
Read 2026-09-29 from [Django on Vercel](https://vercel.com/docs/frameworks/full-stack/django), [Python runtime](https://vercel.com/docs/functions/runtimes/python), [Function limits](https://vercel.com/docs/functions/limitations), [Fluid compute](https://vercel.com/docs/fluid-compute), [System env vars](https://vercel.com/docs/environment-variables/system-environment-variables) and [Neon on Vercel](https://neon.com/docs/guides/vercel-native-integration).

| Area | Vercel today | Fits LightChat? |
|---|---|---|
| Django / WSGI | Zero-config. It detects `manage.py` and loads `WSGI_APPLICATION`, and the whole app runs as **one function** | ✅ as is |
| Python 3.14 | Supported (3.12 is the default). It's read from `.python-version` | ✅ as is |
| Static files | Runs `collectstatic` automatically when `STATIC_ROOT` is set and serves the files from the CDN at `/static/` | ✅ as is |
| Streaming | Python functions stream by default | ✅ to be confirmed on the preview (the NDJSON must not be buffered) |
| **Duration** | **Hobby: 300 s max. Pro: 800 s** (1800 s in beta). When the limit is reached, the function is killed with a 504 | ❌ **A 20-minute reply can't run.** Needs an adjustment |
| **Filesystem** | Every instance starts fresh, and local files don't persist | ❌ **SQLite would lose all data.** Needs Postgres |
| Database | Vercel Postgres has been retired, so Postgres comes from the Marketplace (Neon). Neon injects `DATABASE_URL` (pooled through PgBouncer) and `DATABASE_URL_UNPOOLED`, and can give each Preview deployment its own copy-on-write branch | ✅ with a driver and pooler-safe settings |
| HTTPS | Vercel terminates TLS and forwards `X-Forwarded-Proto` | ✅ Django must trust that header |
| Hosts | `VERCEL_URL`, `VERCEL_BRANCH_URL` and `VERCEL_PROJECT_PRODUCTION_URL` are set at build time and at runtime | ✅ `ALLOWED_HOSTS` can use them |
| Request body | 4.5 MB | ✅ prompts are small |
| Preview access | Previews sit behind Vercel Authentication (Standard Protection) by default | ✅ keeps previews private. My automated tests need a bypass token (see Exogenous Inputs) |

## Options & Tradeoffs

**Database**
| Option | Pros | Cons | Effort | Risk |
|---|---|---|---|---|
| **A. Neon Free through the Vercel Marketplace** | $0 and no card. Env vars are injected. Previews get isolated branches. Postgres is already supported in code | 0.5 GB and 100 CU-hours per month. It suspends after 5 min idle (about 0.5 s cold start) | Low | Low |
| B. Another Marketplace Postgres (Supabase, Prisma…) | Similar | No automatic preview branching. Another account to manage | Low | Low |
| C. Keep SQLite | None | Data is lost on every cold start | — | Not viable |

**Reply length vs. the 300 s limit**
| Option | Pros | Cons | Effort | Risk |
|---|---|---|---|---|
| **A. Cap each reply at ~270 s on Vercel and shorten the gap allowed between chunks to 25 s, so the app always finishes the reply itself before Vercel would kill it** | Free. The 25,000-token limit stays: at the measured ~135 tokens/s a full reply takes ~185 s. Timeouts follow the existing path (partial text kept, hold under review) | A reply slower than ~93 tokens/s would be cut off at 270 s | Low | Low |
| B. Pro plan (800 s) | More headroom | $20 a month. That's a purchase | Low | Low |
| C. Move generation to a background worker (Workflows or Queues) | No time limit | Architecture change, more services and more cost | High | Medium |

**Region**
The proxy is in **Roubaix, France** (OVH). During a stream the function polls the database every 0.5 s, so **the function and the database must be in the same region**.

| Option | Pros | Cons |
|---|---|---|
| **A. `fra1` (Frankfurt) with Neon `aws-eu-central-1`** | About 10 ms to the proxy, so the fewest connection timeouts and the fastest first token | Pages take about 250 ms per round trip from Manila |
| B. `sin1` (Singapore) with Neon `aws-ap-southeast-1` | Faster page loads from Asia | About 250 ms to the proxy. The flaky connections seen from Manila may reappear |

## Recommendation
Use **Hobby (free), Neon Free, `fra1`**, and make these small changes:

1. **Postgres.** Add `psycopg[binary]`. When the database is Postgres:
   - disable server-side cursors (required behind PgBouncer's transaction pooling);
   - turn on connection health checks.

   Run migrations in the Vercel build over `DATABASE_URL_UNPOOLED`. Neon preview branching gives every preview its own database, so testing never touches production data.
2. **Duration.** Make the reply limits configurable. On Vercel, set `maxDuration: 300`, a 270 s cap per reply and 25 s between chunks. Locally, keep today's 20 min and 90 s.
3. **Production security.** On Vercel only:
   - trust `X-Forwarded-Proto`;
   - turn on SSL redirect and `Secure` session and CSRF cookies;
   - add HSTS for one year (without `includeSubDomains` or preload, because the domain isn't ours);
   - build `ALLOWED_HOSTS` from Vercel's system variables plus an optional override;
   - silence mail.E001 with a comment (the app never sends email).
4. **Explicit deploys only.**
   - `vercel.json` sets `git.deploymentEnabled: false`, so linking the GitHub repo can't auto-deploy anything to production.
   - Every deploy is a deliberate `vercel deploy` (preview) or `vercel deploy --prod` (after your acceptance).
   - A `.vercelignore` keeps `.env*`, databases, `submission/`, `doc/` and `.venv` out of the upload.
5. **Secrets** are set with `vercel env add`, piped from the local `.env` so they are never printed. They go to the Production and Preview environments. `SECRET_KEY` is freshly generated, with a different value per environment.
6. **Postgres is tested before deploying.** I install Homebrew PostgreSQL locally (free) and run the full suite, including the threaded no-overspend tests, against it.
7. **Held replies.** Replies whose function died keep their hold, as today. The operator still runs `reconcile_stale_generations`, now against production through `vercel env pull`. A scheduled cron job would be a separate request.

This follows Vercel's zero-config Django path: no custom entrypoint, and no ASGI or WebSocket rewrite.

## Exogenous Inputs
| Input | Why needed | Status | Owner |
|---|---|---|---|
| Vercel account and CLI login | To create the project, set env vars and deploy | **needed**: you run `npx vercel@latest login` once in your terminal | Gardener |
| Neon database added through the Vercel Marketplace (Free plan, region **Frankfurt `aws-eu-central-1`**, Production and Preview environments, **Preview branching on**) | Persistent storage | **needed**: dashboard clicks and accepting Neon's terms, after I create the project | Gardener |
| Protection Bypass for Automation secret | Lets my scripted tests reach the protected preview | **needed**: one click in Project → Settings → Deployment Protection. Vercel exposes it to the CLI, and it never goes into chat or Git | Gardener |
| BUILD proxy keys | Model calls | verified (already in local `.env`) | — |
| Whether the proxy accepts calls from Vercel's IPs | Model responses | **assumed**: the docs mention no IP allowlist. The first preview reply will confirm it | Vine |
| Admin account on production | Reconciliation | **needed at production time**: you run `createsuperuser` yourself, so you choose the password | Gardener |

## Costs
- **Vercel Hobby:** $0. Its terms limit it to non-commercial use, which fits an assessment project. Upgrading to Pro would be $20 a month and is not planned.
- **Neon Free:** $0 and no card. If the 0.5 GB or 100 CU-hour limits are exceeded, the database stops accepting writes (or suspends) until the next month. It is never billed.
- **BUILD proxy (paid, metered):** about **12 short test replies** of 100 output tokens or fewer, across three interfaces, preview and production. That's roughly 12 × ~400 tokens, or about 5,000 tokens in total. One more *long* reply (~3,000 tokens) confirms streaming holds past 20 s.

## Risks & Open Questions
- **Buffered streaming.** If Vercel buffers WSGI streams, replies would appear all at once. They would still be correct and charged correctly. The fallback is to switch the one streaming view to ASGI, which I'd bring back to you as a finding rather than do silently.
- **Disconnect detection.** WSGI on Vercel may not tell the app when the browser closes. If so, a reply keeps running to its end and is charged normally. That is safe, and the same as or better than today.
- **Migrations run in the production build before the switch-over.** Today's migrations only add things, so that's fine. Future destructive migrations would need a two-step release, which will be noted in the wiki.
- **Proxy connectivity from Frankfurt** is unknown. It will be measured on the preview.
- **Rollback:** `vercel rollback` or promoting a previous deployment restores the code instantly, but it doesn't undo database migrations. This will be documented.
- **Questions for you:** (1) Is the **Hobby plan with a ~270 s reply cap** OK, or do you want Pro? (2) Is the **Frankfurt region** OK, or are your users mostly in Asia (Singapore)?

## Review
- **2026-09-29:** Approved by the Gardener with the Plan. Decisions: stay on the **Vercel Hobby (free)** plan with the ~270 s reply cap; use the **Frankfurt** region (`fra1`, Neon `aws-eu-central-1`). The Gardener asked to be guided through the Neon setup once the Vercel project exists.
