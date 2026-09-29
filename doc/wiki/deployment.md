# Deployment (Vercel)

LightChat is live at **https://lightchat-five.vercel.app**. It runs on Vercel's free Hobby plan, with a free Neon Postgres database, in Frankfurt.

## What runs where

| Piece | Where | Notes |
|---|---|---|
| Django app | One Vercel Function (Python 3.14, WSGI, `config/wsgi.py`), region **`fra1`** (Frankfurt) | Close to the proxy in Roubaix, France. `maxDuration: 300` s, the Hobby maximum |
| Static files | Vercel CDN at `/static/` | Vercel runs `collectstatic` automatically because `STATIC_ROOT` is set |
| Database | Neon Postgres (Free), `aws-eu-central-1` (Frankfurt) | The app uses the pooled `DATABASE_URL` (PgBouncer). Migrations use `DATABASE_URL_UNPOOLED` |
| Build gate | Every Vercel build (`vercel.json` → `buildCommand`) | 1. The **full test suite** runs on a throwaway SQLite file (no Neon, no paid proxy calls). 2. Only if all tests pass, **migrations** run over `DATABASE_URL_UNPOOLED`. A failing test fails the build, and the live site keeps its current version |

- **Vercel project:** `lightchat` in `shmuelng8310-5097s-projects`. The local link is in `.vercel/` (gitignored).
- **Configuration files:** [`vercel.json`](../../vercel.json) and [`.vercelignore`](../../.vercelignore).
- **Git:** the project is connected to GitHub [`ShmuelNg1212/LightChat`](https://github.com/ShmuelNg1212/LightChat) (production branch `main`). **Every push deploys** (Vercel's default Git workflow): `main` goes to production, and any other branch or pull request gets a private preview. Deployments show their commit on GitHub and in the Vercel dashboard.

## Environment variables (Vercel → Settings → Environment Variables)

The same names are set for **Production** and **Preview**. None of them are in Git; names and purposes are also in [`.env.example`](../../.env.example).

| Variable | Set by | Value / purpose |
|---|---|---|
| `SECRET_KEY` | us, sensitive | A random 86-character value, different for Production and Preview |
| `BUILD_OPENAI_KEY`, `BUILD_ANTHROPIC_KEY`, `BUILD_GOOGLE_KEY` | us, sensitive | Proxy keys (copied from the local `.env`) |
| `REPLY_MAX_SECONDS` | us | `260`. The app ends a reply before Vercel's 300 s limit |
| `REPLY_CHUNK_TIMEOUT_SECONDS` | us | `25`. The longest wait between chunks (260 + 25 < 300) |
| `DB_CONN_MAX_AGE` | us | `0`. Don't hold database connections between requests (PgBouncer does the pooling) |
| `DATABASE_URL`, `DATABASE_URL_UNPOOLED` (+ `PG*`, `POSTGRES_*`, `NEON_*`) | Neon integration, sensitive | Connection strings. Only the first two are used |
| `VERCEL`, `VERCEL_URL`, `VERCEL_BRANCH_URL`, `VERCEL_PROJECT_PRODUCTION_URL` | Vercel (system) | Turn on the HTTPS settings and add the deployment's host names to `ALLOWED_HOSTS` |

Sensitive values can't be read back through the CLI or `vercel env pull`. To change one, remove it and add it again:

```sh
npx vercel@latest env rm SECRET_KEY production
python3 -c "import secrets;print(secrets.token_urlsafe(64),end='')" | npx vercel@latest env add SECRET_KEY production --sensitive
```

A variable change only takes effect on the **next deployment**.

## Production settings (automatic on Vercel)

When `VERCEL` is set (or `HTTPS_ONLY=True`), `config/settings.py` turns on:
- trust of `X-Forwarded-Proto`;
- a redirect to HTTPS;
- `Secure` session and CSRF cookies;
- HSTS for one year. It covers this host only, because `*.vercel.app` isn't ours to preload.

`manage.py check --deploy` is clean with these settings, and `config/tests.py` enforces that. On Vercel, the app **refuses to start without `DATABASE_URL`**, so it can never quietly run on a throwaway SQLite file.

## Deploying a change

1. Work on a branch: `git switch -c my-change`. Commit, and run `.venv/bin/python manage.py test` locally.
2. `git push -u origin my-change`. Vercel builds a **preview** (the tests run in the build) and posts its URL on the GitHub commit or pull request. Preview URLs need a Vercel login.
3. Test the preview in a browser where you're signed in to Vercel.
4. Merge into `main` (a pull request on GitHub, or `git switch main && git merge my-change && git push`). Vercel builds **production**: tests, then migrations, then `lightchat-five.vercel.app` switches to the new version, but only if the build succeeds.

The CLI still works for one-off deploys: `npx vercel@latest deploy` (preview) and `npx vercel@latest deploy --prod`. **CLI previews share the production database** (see below).

### Database changes: additive only

Migrations run on the production database **before** the new version goes live, and a rollback **doesn't undo them**. So every release must keep the database usable by the previous version:
- ✅ Adding tables, adding nullable columns or columns with defaults, adding indexes, data migrations that only add rows.
- ❌ Removing or renaming a column or table in the same release as the code change. Do it in two releases instead: first deploy code that no longer uses the field, then (one release later) the migration that removes it.

### Preview databases

- **Git previews (a branch push or a pull request) get their own Neon database branch**, a copy-on-write copy of production made when the preview is built. Anything done on such a preview never reaches production. Verified 2026-09-29: an account created on a Git preview could not sign in to production.
- **CLI previews (`npx vercel@latest deploy`) share the production database** (no Neon branch is made), and their build migrates it. Prefer Git branches for previews.
- **Housekeeping:** Neon Free allows 10 branches per project. Preview branches are deleted when Vercel deletes the preview deployments (after 6 months by default). If Neon reports the limit, delete old `preview/…` branches in the Neon console → Branches. Never delete `main`.

## Rollback runbook (a bug in production)

1. **Roll back:** Vercel → project **lightchat** → Production tile → **Instant Rollback** → **Confirm**, or `npx vercel@latest rollback`. The previous production version serves again within seconds, with no rebuild.
   - On Hobby, you can only go back **one** release. For something older, revert the bad commit on GitHub (`git revert <sha> && git push`). The revert deploys itself, after the rollback is undone (step 3).
2. **While rolled back, pushes to `main` don't go live.** Vercel pauses auto-assignment of the production domain, so a follow-up push can't undo the rollback by accident. Builds still run, so fixes can be checked on their deployment URL.
3. **Resume normal releases:** push the fix, then Vercel → Production tile → **Undo Rollback** → pick the fixed deployment → **Confirm**, or `npx vercel@latest promote <deployment-url>`.
4. **Database:** rollback restores code only. If a migration caused the bug, deploy a forward fix (a new migration), or restore the database from the Neon console (point-in-time restore, within the restore window your Neon plan includes).

## Security-incident runbook (a leaked key, abuse, a vulnerability)

Rollback is **not** the tool here: a rolled-back deployment keeps the environment variables it was built with.

1. **Close the site (seconds, free):** Vercel → Settings → Deployment Protection → **All Deployments** → Save. Every URL now needs a Vercel login, and the public is locked out.
2. **Rotate what leaked:**
   - A **proxy key:** ask the BUILD proxy administrator for a new key, then `npx vercel@latest env rm BUILD_OPENAI_KEY production` and add the new one (see *Environment variables* above). Do the same for Preview.
   - **`SECRET_KEY`:** replace it as shown above. This signs everyone out.
   - **The database password:** Neon console → Roles → reset the password. The Vercel integration updates `DATABASE_URL*`.
3. **Redeploy** so the new values take effect: push a commit, or `npx vercel@latest deploy --prod`.
4. **Check,** then reopen: Deployment Protection → **Standard Protection** → Save.
5. **Review the damage:** `/admin/` → Generations and Ledger entries (unusual sign-ups or spending), and Vercel → Logs.

## Operations against production

Admin commands run locally against the production database. Copy the **direct** connection string from Vercel → Storage → your Neon database → **.env.local** tab → **Show secret** (`DATABASE_URL_UNPOOLED`), or from the Neon console → **Connect** (with pooling turned off). Don't save it to a file in the repo.

```sh
# Create an admin account (you choose the password when prompted)
DATABASE_URL='postgresql://…' .venv/bin/python manage.py createsuperuser

# Flag replies whose function died mid-stream, then settle them at /admin/ → Generations
DATABASE_URL='postgresql://…' .venv/bin/python manage.py reconcile_stale_generations
```

## Limits to know

| Limit | Value | Effect |
|---|---|---|
| Function duration (Hobby) | 300 s | A reply is cut off at 260 s (partial text kept, hold left for admin review). At the measured ~135 tokens/s, a full 25,000-token reply takes about 3 minutes |
| Request body | 4.5 MB | Far above any prompt |
| Neon Free | 0.5 GB storage, 100 CU-hours a month; sleeps after 5 min idle | The first request after idle waits about 0.5 s for the database to wake. If the limits are hit, writes stop until the next month. Never billed |
| Vercel Hobby | Non-commercial use only | Fits the assessment |

## Verified on 2026-09-29

- **Preview:** 36/36 scripted checks (three models, streaming, holds and charges, the double-send check, Stop, saved chats, secure cookies, HSTS, static files, no secrets served) and 17/17 phone checks at 360 and 390 px.
- **Production:** 28/28 checks.
- Streaming reaches the browser incrementally. The first token arrives in about 1 s.
