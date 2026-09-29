"""Settings helpers that depend on where the app runs (local or Vercel).

Kept free of Django imports so settings.py can call them and tests can
exercise them with a plain dict for the environment.
"""

import dj_database_url


def database_config(url: str, *, conn_max_age: int) -> dict:
    """DATABASES["default"] for a DATABASE_URL (SQLite or PostgreSQL)."""
    db = dj_database_url.parse(url, conn_max_age=conn_max_age, conn_health_checks=True)
    if db["ENGINE"] == "django.db.backends.sqlite3":
        # Concurrent requests (streams, several tabs) must wait for the write lock
        # rather than fail: take it at transaction start and allow a busy timeout.
        db["OPTIONS"] = {
            "transaction_mode": "IMMEDIATE",
            "timeout": 20,
            "init_command": "PRAGMA journal_mode=WAL;",
        }
    elif db["ENGINE"] == "django.db.backends.postgresql":
        # Neon's pooled URL goes through PgBouncer in transaction mode, where a
        # named cursor could land on another server connection.
        db["DISABLE_SERVER_SIDE_CURSORS"] = True
    return db


def vercel_hosts(environ) -> list[str]:
    """Host names Vercel assigns to this deployment (empty when not on Vercel)."""
    names = ("VERCEL_URL", "VERCEL_BRANCH_URL", "VERCEL_PROJECT_PRODUCTION_URL")
    return [environ[n] for n in names if environ.get(n)]
