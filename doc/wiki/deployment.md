# Deployment (Vercel)

LightChat is live at **https://lightchat-five.vercel.app**. It runs on Vercel's free Hobby plan, with a free Neon Postgres database, in Frankfurt.

## What runs where

| Piece | Where | Notes |
|---|---|---|
| Django app | One Vercel Function (Python 3.14, WSGI, `config/wsgi.py`), region **`fra1`** (Frankfurt) | Close to the proxy in Roubaix, France. `maxDuration: 300` s, the Hobby maximum |
| Static files | Vercel CDN at `/static/` | Vercel runs `collectstatic` automatically because `STATIC_ROOT` is set |
| Database | Neon Postgres (Free), `aws-eu-central-1` (Frankfurt) | The app uses the pooled `DATABASE_URL` (PgBouncer). Migrations use `DATABASE_URL_UNPOOLED` |
| Migrations | In every Vercel build (`vercel.json` → `buildCommand`) | Run before the deployment serves traffic |

- **Vercel project:** `lightchat` in `shmuelng8310-5097s-projects`. The local link is in `.vercel/` (gitignored).
- **Configuration files:** [`vercel.json`](../../vercel.json) and [`.vercelignore`](../../.vercelignore).
- **Git:** pushes to GitHub **don't deploy** (`git.deploymentEnabled: false`), so every deploy is a deliberate CLI command.

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

1. Commit the change. Tests must pass locally: `.venv/bin/python manage.py test`.
2. **Preview:** `npx vercel@latest deploy`. Preview URLs need a Vercel login.
3. Test the preview URL in a browser where you're signed in to Vercel.
4. **Production:** `npx vercel@latest deploy --prod`. This builds again, runs migrations, and moves `lightchat-five.vercel.app` to the new deployment when the build succeeds.

> ⚠️ **Preview and production share one database.** Neon's automatic preview branching doesn't happen for CLI deployments, so the preview build **runs migrations against the production database**, and anything done on a preview is real data.
>
> - Additive migrations (new tables or columns) are safe.
> - A migration that removes or renames something needs two releases: first deploy code that no longer uses the old field, then deploy the migration that removes it.
> - To isolate previews, create a Neon branch (Neon console → Branches) and set a **Preview-only** `DATABASE_URL` / `DATABASE_URL_UNPOOLED` pointing to it.

## Rollback

| Situation | What to do |
|---|---|
| The new code is broken | `npx vercel@latest rollback`. This instantly points production back to the previous production deployment (on Hobby, only the one just before it). Or, in the dashboard: Deployments → pick an older production deployment → **Promote** |
| Back to an older version | Check out the old commit, then `npx vercel@latest deploy --prod` |
| A migration went wrong | Rolling back the code **does not undo migrations**. Deploy a fix forward (a new migration), or restore the database in the Neon console (point-in-time restore, within the restore window your Neon plan includes) |
| Take the site offline fast | Vercel → Settings → Deployment Protection → **All Deployments** (free). Everyone then needs a Vercel login. Switch back to **Standard Protection** to reopen |

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
