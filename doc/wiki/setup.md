# Setup

How to install, configure and run LightChat locally. For the live Vercel deployment, see [deployment.md](deployment.md).

## Requirements

- Python **3.14** (pinned in `.python-version`; on this machine at `/opt/homebrew/bin/python3.14`)
- The BUILD LLM Proxy keys (see [external-dependencies.md](external-dependencies.md))
- No database server: SQLite is used locally by default

## Install

```sh
cd /Users/shm/LightChat
/opt/homebrew/bin/python3.14 -m venv --clear .venv
.venv/bin/python -m pip install -r requirements.txt   # survives a renamed folder, unlike .venv/bin/pip
cp .env.example .env        # then fill in the keys
.venv/bin/python manage.py migrate
```

## Configure (`.env`)

`.env` is gitignored. `.env.example` lists every variable with its purpose.

| Variable | Required | Purpose |
|---|---|---|
| `BUILD_OPENAI_KEY` | for the GPT model | OpenAI-interface proxy key |
| `BUILD_ANTHROPIC_KEY` | for the Claude model | Anthropic-interface proxy key |
| `BUILD_GOOGLE_KEY` | for the Gemini model | Google-interface proxy key |
| `DEBUG` | locally | `True` enables debug pages and a fixed development `SECRET_KEY` |
| `SECRET_KEY` | when `DEBUG` is off | Django secret key; the app refuses to start without one |
| `ALLOWED_HOSTS` | when deployed | Comma-separated host names (default `localhost,127.0.0.1`) |
| `DATABASE_URL` | no (required on Vercel) | e.g. `postgres://user:pass@host:5432/db`; defaults to `db.sqlite3` |
| `DB_CONN_MAX_AGE` | no | Seconds to keep a database connection (default 60; `0` on Vercel) |
| `REPLY_MAX_SECONDS` | no | Longest a reply may stream (default 1200; `260` on Vercel) |
| `REPLY_CHUNK_TIMEOUT_SECONDS` | no | Longest wait between streamed chunks (default 90; `25` on Vercel) |
| `HTTPS_ONLY` | no | Secure cookies, HSTS, HTTPS redirect. Defaults to on when `VERCEL` is set |
| `PROXY_BASE_URL` | no | Defaults to `https://proxy.litechat.ai` |
| `LOG_LEVEL` | no | Level for `litechat.*` loggers (default `INFO`) |

A model whose key is blank is hidden from users.

## Run

```sh
.venv/bin/python manage.py runserver          # http://127.0.0.1:8000
```

Create an admin account (needed to review held credit at `/admin/`):

```sh
.venv/bin/python manage.py createsuperuser
```

## Test

```sh
.venv/bin/python manage.py test
```

140 tests. They never call the real proxy: an `httpx.MockTransport` replaces the network, and real captured responses in `doc/fixtures/proxy/` are replayed. SQLite tests use a file-backed test database (`test_db.sqlite3`, gitignored) so locking behaves as in development.

To run the suite on PostgreSQL (as deployed), point `DATABASE_URL` at a local server, for example Homebrew `postgresql@17`: `DATABASE_URL=postgres://user@127.0.0.1:5432/lightchat .venv/bin/python manage.py test`. It passed on 2026-09-29.

## Design checks

| Command | What it checks |
|---|---|
| `python3 doc/design/check_contrast.py` | Every color token pair in `static/css/app.css` meets WCAG 2.2 AA in light and dark (exit 1 on failure) |
| `…/impeccable detect --json <files>` | Impeccable's anti-pattern detector (runs automatically as a hook when editing UI through Claude Code) |
| `python doc/design/brand/generate_logo.py <BarlowSemiCondensed-SemiBold.ttf> static/brand` | Rebuilds the logo SVGs (needs `fonttools`) |

Fonts are self-hosted from `static/fonts/` (sources and licences in its README). No third-party requests are made for fonts or icons.

## Operational commands

| Command | What it does | Cost |
|---|---|---|
| `manage.py probe_proxy [--provider P] [--bad-key] [--max-tokens N] [--no-save]` | Makes one tiny streamed request per configured interface. Rewrites the redacted fixtures in `doc/fixtures/proxy/` unless `--no-save` is given (use that to check a setting such as a new output limit) | **Paid**: about 190 tokens per interface |
| `manage.py reconcile_stale_generations [--minutes 10]` | Flags replies stuck "in progress" (e.g. after a server restart) for admin review | Free |

## Assessment submission package

`python tools/package_submission.py --scratch <session scratchpad> --impeccable-license submission/inputs/impeccable-LICENSE` builds the local assessment package in `submission/` (gitignored; never committed or uploaded). It:
- copies the raw session transcripts, rules, skills, journal, a source snapshot of HEAD, evidence and git history;
- redacts the author email and the throwaway test passwords (listed in the gitignored `submission/inputs/redact-test-passwords.txt`);
- writes a manifest with SHA-256 checksums;
- runs the test suite;
- scans the result for `.env` values, the email, passwords, databases and dependency folders, aborting on any hit;
- zips the package.

The assessor README and `SKILLS-USED.md` are inputs kept only in `submission/inputs/`. The script uses only the standard library.

## Not yet set up

- Password-reset email and Google sign-in.
