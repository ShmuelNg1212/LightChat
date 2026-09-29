"""Build the local assessment submission package (documentation only).

Usage:
    python tools/package_submission.py --scratch <session scratchpad dir> --impeccable-license <LICENSE file>

Writes submission/lightchat-assessment-package/ and a ZIP beside it. submission/ is
gitignored; nothing is uploaded. Originals are only read. Copies of conversation logs
and scripts have the Gardener's email and local test passwords redacted. The finished
folder is scanned for .env values, the email, test passwords, databases, .env files
and dependency folders; any hit aborts before zipping.

Stdlib only. Plan: doc/plan/2026-09-29-1456-assessment-package.md
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = ROOT / "submission"
PKG_NAME = "lightchat-assessment-package"
OUT = SUBMISSION / PKG_NAME
INPUTS = SUBMISSION / "inputs"
TRANSCRIPTS = Path.home() / ".claude/projects/-Users-shm-litechat-midterm"
MAIN_SESSION = "41aceb7c-abfa-464c-b227-5a085f4011ca"
PLUGIN = Path.home() / ".claude/plugins/cache/impeccable/impeccable/4.4.0"
TEST_PASSWORDS = ["[REDACTED_TEST_PASSWORD]", "[REDACTED_TEST_PASSWORD]", "[REDACTED_TEST_PASSWORD]", "[REDACTED_TEST_PASSWORD]", "[REDACTED_TEST_PASSWORD]"]
EMAIL_TOKEN, PASSWORD_TOKEN = "[REDACTED_EMAIL]", "[REDACTED_TEST_PASSWORD]"

# Scratchpad verification scripts whose creation is recorded in the session transcript.
SCRIPTS = [
    "shoot.js", "shoot2.js", "shoot3.js", "e2e.js", "long.js", "cmp.js", "shootlogo.js",
    "icons.js", "iconsheet.js", "iconsheet.html", "logo.py", "small.py", "pngmeta.py", "contrast.py",
    "states/seed.py", "states/shots.js", "states/audit.js", "states/keys.js", "states/live.js",
    "states/review-shots.js", "states/dock.js",
]

kinds: dict[str, str] = {}   # package-relative path -> original | redacted copy | generated
sources: dict[str, str] = {}
redactions: list[str] = []
missing: list[str] = []


def run(*cmd, **kw) -> str:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True, **kw).stdout


def rel(p: Path) -> str:
    return p.relative_to(OUT).as_posix()


def note(dest: Path, kind: str, source: str = ""):
    kinds[rel(dest)] = kind
    if source:
        sources[rel(dest)] = source


def copy(src: Path, dest: Path, kind="original"):
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    note(dest, kind, str(src).replace(str(Path.home()), "~"))


def copy_tree(src: Path, dest: Path, skip=lambda p: False):
    for f in sorted(src.rglob("*")):
        if f.is_file() and not skip(f):
            copy(f, dest / f.relative_to(src))


def redact_bytes(data: bytes, email: str) -> tuple[bytes, dict]:
    counts = {}
    if email:
        counts["email"] = data.count(email.encode())
        data = data.replace(email.encode(), EMAIL_TOKEN.encode())
    for pw in TEST_PASSWORDS:
        n = data.count(pw.encode())
        if n:
            counts[pw] = n
            data = data.replace(pw.encode(), PASSWORD_TOKEN.encode())
    return data, counts


def copy_redacted(src: Path, dest: Path, email: str):
    dest.parent.mkdir(parents=True, exist_ok=True)
    data, counts = redact_bytes(src.read_bytes(), email)
    dest.write_bytes(data)
    changed = {k: v for k, v in counts.items() if v}
    note(dest, "redacted copy" if changed else "original", str(src).replace(str(Path.home()), "~"))
    if changed:
        what = ", ".join(f"{'email' if k == 'email' else 'test password'} ×{v}" for k, v in changed.items())
        redactions.append(f"`{rel(dest)}`: {what}")


def write(dest: Path, text: str, kind="generated"):
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    note(dest, kind)


def env_values() -> list[str]:
    values = []
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                v = line.split("=", 1)[1].strip().strip('"').strip("'")
                if len(v) >= 8:  # ignore short flags such as DEBUG=True
                    values.append(v)
    return values


# ---------------------------------------------------------------- sections

def conversations(email: str, now: str):
    base = OUT / "01-conversations" / "jsonl"
    main = TRANSCRIPTS / f"{MAIN_SESSION}.jsonl"
    copy_redacted(main, base / main.name, email)
    for f in sorted((TRANSCRIPTS / MAIN_SESSION / "subagents").glob("*")):
        copy_redacted(f, base / "subagents" / f.name, email)

    rows = []
    main_last = None
    for f in [main, *sorted((TRANSCRIPTS / MAIN_SESSION / "subagents").glob("*.jsonl"))]:
        first = last = title = None
        users = assistants = 0
        for line in f.open(encoding="utf-8"):
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = d.get("timestamp")
            if ts:
                first, last = first or ts, ts
            users += d.get("type") == "user"
            assistants += d.get("type") == "assistant"
            if d.get("type") == "ai-title" and not title:
                title = d.get("aiTitle") or d.get("title")
        meta = f.with_suffix(".meta.json")
        role = json.loads(meta.read_text()).get("agentType", "") if meta.exists() else "main Claude Code session"
        rows.append((first, f.name, role, first, last, users, assistants, title))
        if f == main:
            main_last = last
    rows.sort()
    table = "\n".join(
        f"| {i} | `{name}` | {role or '—'} | {a} | {b} | {u} | {asst} |"
        for i, (_, name, role, a, b, u, asst, _t) in enumerate(rows, 1)
    )
    write(OUT / "01-conversations" / "SESSION-INDEX.md", f"""# Session index (chronological)

*Generated {now} by `tools/package_submission.py` from the JSONL timestamps. Times are UTC (Asia/Manila = UTC+8).*

| # | File (in `jsonl/`) | Kind | First entry | Last entry in snapshot | User entries | Assistant entries |
|---|---|---|---|---|---|---|
| 0 | *(missing, see below)* | Session that wrote `doc/study/2026-09-29-1243-litechat-core.md` | ~2026-09-29 04:43 (12:43 Manila, per the study's own date) | — | — | — |
{table}

The main session was still running when this snapshot was taken. Turns after "{main_last}" (including the rest of the packaging conversation) are not included.

## Missing session exports

1. **Original study session.** It produced `doc/study/2026-09-29-1243-litechat-core.md`, which was pasted into the main session as its first message. By its own account it ran in a different workspace (`work/` and `outputs/` folders, `outputs/litechat/`, browser access to GitHub and litechat.ai, failing shell DNS). Its transcript is not in this machine's Claude Code project store, so it is **not included**.
2. **Claude Code `/export` text exports:** none were made for any session. The files here are the raw JSONL session logs Claude Code keeps, copied with only the redactions listed in `MANIFEST.md`.

Excluded as unrelated: sessions of the separate WhatsUp project, and an empty 2026-09-28 desktop workspace marker.
""")
    missing.extend([
        "Transcript of the original-study session (doc/study/2026-09-29-1243-litechat-core.md, 12:43 Manila): not on this machine.",
        "Claude Code `/export` text exports: none were made; raw JSONL logs are included instead.",
        "Final turns of the main session after the snapshot time shown in 01-conversations/SESSION-INDEX.md.",
    ])


def rules():
    base = OUT / "02-project-rules"
    for name in ("AGENTS.md", "CLAUDE.md", "PRODUCT.md", "DESIGN.md"):
        copy(ROOT / name, base / name)
    for f in (".impeccable/config.json", ".impeccable/live/config.json", ".impeccable/design.json"):
        copy(ROOT / f, base / f)
    copy_tree(ROOT / ".impeccable/surfaces", base / ".impeccable/surfaces")


def skills(license_file: Path):
    base = OUT / "03-skills"
    copy(INPUTS / "SKILLS-USED.md", base / "SKILLS-USED.md", kind="generated")
    is_binary = lambda p: b"\0" in p.read_bytes()[:8192]
    copy_tree(PLUGIN, base / "impeccable-4.4.0", skip=is_binary)
    copy(license_file, base / "impeccable-4.4.0" / "LICENSE")
    sources[rel(base / "impeccable-4.4.0" / "LICENSE")] = "https://github.com/pbakaus/impeccable/blob/main/LICENSE (fetched at packaging time)"


def journal():
    for part in ("study", "plan", "design", "wiki"):
        copy_tree(ROOT / "doc" / part, OUT / "04-journal" / part)


def source(head: str, now: str):
    snap = OUT / "05-source" / "repository-snapshot"
    snap.mkdir(parents=True)
    archive = subprocess.run(["git", "archive", "--format=tar", head], cwd=ROOT, capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(snap)], input=archive, check=True)
    for f in snap.rglob("*"):
        if f.is_file():
            note(f, "original", f"git archive {head[:12]}")
    freeze = run(str(ROOT / ".venv/bin/pip"), "freeze")
    write(OUT / "05-source" / "requirements-freeze.txt",
          f"# Generated {now} by `pip freeze` from the working .venv (Python {run(str(ROOT / '.venv/bin/python'), '--version').strip()}).\n"
          "# The repository pins direct dependencies in requirements.txt; it has no lockfile.\n" + freeze)


def evidence(scratch: Path | None, head: str, now: str, email: str):
    base = OUT / "06-evidence"
    # Test results: a fresh verbose run at packaging time.
    proc = subprocess.run([str(ROOT / ".venv/bin/python"), "manage.py", "test", "-v", "2"], cwd=ROOT, capture_output=True, text=True)
    versions = run(str(ROOT / ".venv/bin/python"), "-c", "import django,sys;print(sys.version.split()[0], django.get_version())").split()
    write(base / "test-results" / "test-run.txt",
          f"# Test run generated {now} at commit {head} (Python {versions[0]}, Django {versions[1]}).\n"
          f"# Command: python manage.py test -v 2   Exit code: {proc.returncode}\n\n" + proc.stdout + proc.stderr)
    if proc.returncode != 0:
        sys.exit("Tests failed; package not built. See the test run output above.")

    shots = base / "screenshots"
    copy_tree(ROOT / ".impeccable/review", shots / "rebrand-finish-review")
    copy_tree(ROOT / "doc/design/drafts", shots / "logo-drafts", skip=lambda p: p.suffix != ".png")
    if scratch and scratch.exists():
        groups = {
            "core-app-rendezvous-pre-rebrand": ["shot-*.png", "light-*.png", "errors-*.png"],
            "reply-limit-live-check": ["long-reply.png"],
            "logo-and-icon-checks": ["out-logo/*.png", "iconsheet.png", "states/favicon-16-actual.png", "states/header-1x.png"],
            "rebrand-inspection-rounds": ["states/r1-*.png", "states/r2-*.png", "states/live-*.png", "states/final-*.png"],
        }
        for folder, patterns in groups.items():
            for pattern in patterns:
                for f in sorted(scratch.glob(pattern)):
                    copy(f, shots / folder / f.name)
        for name in SCRIPTS:
            f = scratch / name
            if f.exists():
                copy_redacted(f, base / "verification-scripts" / name, email)
            else:
                missing.append(f"Verification script `{name}` was no longer in the scratchpad.")
    else:
        missing.append("Session scratchpad (screenshots from the core-app and rebrand checks, verification scripts) was not available.")
    copy_tree(ROOT / "doc/fixtures/proxy", base / "api-samples")


def git_section(head: str, email: str, now: str):
    base = OUT / "07-git"
    log = run("git", "log", "--date=iso-strict", "--format=commit %H%nAuthor: %an <%ae>%nDate:   %ad%n%n%w(0,4,4)%B")
    data, counts = redact_bytes(log.encode(), email)
    write(base / "git-log.txt", f"# Readable commit history, generated {now} (`git log`). Author email redacted.\n\n" + data.decode(), kind="redacted copy")
    if counts.get("email"):
        redactions.append(f"`07-git/git-log.txt`: email ×{counts['email']}")
    status = run("git", "status", "--porcelain=v1", "--branch")
    write(base / "git-status.txt", f"# `git status --porcelain=v1 --branch` at packaging time ({now})\n" + status)
    branch = run("git", "rev-parse", "--abbrev-ref", "HEAD").strip()
    count = run("git", "rev-list", "--count", "HEAD").strip()
    remote = run("git", "remote", "-v").strip() or "none"
    dirty = [line for line in status.splitlines()[1:] if line.strip()]
    write(base / "REPOSITORY.md", f"""# Repository

*Generated {now}.*

- **Repository URL:** none. No remote is configured (`git remote -v`: {remote}). The Gardener has not linked a GitHub repository yet.
- **Submitted commit:** `{head}` on branch `{branch}` ({count} commits).
- **Working tree at packaging time:** {"clean" if not dirty else "has uncommitted changes, see git-status.txt"} (the `submission/` output folder is gitignored).
- **Source snapshot:** `05-source/repository-snapshot/` is `git archive {head[:12]}`: exactly the tracked files at the submitted commit.
- **History:** `git-log.txt` (every commit, message and body; author email redacted). A full `git bundle` is deliberately not included, because it would carry the author email in every commit.
""")


def manifest(now: str, head: str):
    files = sorted(p for p in OUT.rglob("*") if p.is_file())
    entries = []
    for f in files:
        r = rel(f)
        entries.append({
            "path": r, "bytes": f.stat().st_size, "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
            "kind": kinds.get(r, "generated"), "source": sources.get(r, ""),
        })
    (OUT / "manifest.json").write_text(json.dumps({
        "generated": now, "commit": head, "files": entries, "missing": missing, "redactions": redactions,
    }, indent=1), encoding="utf-8")
    by_section: dict[str, list] = {}
    for e in entries:
        by_section.setdefault(e["path"].split("/")[0] if "/" in e["path"] else "(root)", []).append(e)
    lines = [f"# Manifest\n\n*Generated {now} for commit `{head}`. Every file with its size, SHA-256, kind and source. `manifest.json` has the same data. MANIFEST.md and manifest.json are not listed in themselves.*\n",
             "## Kinds\n\n- **original:** byte-for-byte copy.\n- **redacted copy:** copy with the redactions listed below.\n- **generated:** written at packaging time. Summaries in it are retrospective.\n",
             "## Redactions\n\n- The Gardener's email → `[REDACTED_EMAIL]`; local test-account passwords → `[REDACTED_TEST_PASSWORD]`.\n- Not copied at all: `.env` (credentials), `*.sqlite3` databases, `.venv/`, `node_modules/`, caches, Impeccable's downloaded runtime binary, other projects' conversations.\n- Home paths (`/Users/shm/…`) are kept, as decided by the Gardener's defaults.\n"]
    lines += [f"- {r}" for r in redactions]
    lines.append("\n## Missing evidence\n")
    lines += [f"- {m}" for m in missing]
    for section, items in by_section.items():
        lines.append(f"\n## {section} ({len(items)} files)\n\n| Path | Bytes | Kind | Source | SHA-256 |\n|---|---:|---|---|---|")
        lines += [f"| `{e['path']}` | {e['bytes']:,} | {e['kind']} | {e['source'] or '—'} | `{e['sha256'][:16]}…` |" for e in items]
    (OUT / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(entries)


def scan(email: str) -> list[str]:
    needles = [(v, ".env value") for v in env_values()] + [(email, "email")] + [(p, "test password") for p in TEST_PASSWORDS]
    problems = []
    for f in OUT.rglob("*"):
        r = f.relative_to(OUT).as_posix()
        if f.is_dir() and f.name in {".venv", "node_modules", "__pycache__"}:
            problems.append(f"forbidden folder: {r}")
        if not f.is_file():
            continue
        if f.suffix == ".sqlite3" or f.name == ".env" or (f.name.startswith(".env.") and f.name != ".env.example"):
            problems.append(f"forbidden file: {r}")
        data = f.read_bytes()
        for needle, label in needles:
            if needle and needle.encode() in data:
                problems.append(f"{label} found in {r}")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", type=Path)
    ap.add_argument("--impeccable-license", type=Path, required=True)
    args = ap.parse_args()
    for needed in (INPUTS / "README.md", INPUTS / "SKILLS-USED.md", args.impeccable_license):
        if not needed.exists():
            sys.exit(f"Missing input: {needed}")

    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    head = run("git", "rev-parse", "HEAD").strip()
    email = run("git", "config", "user.email").strip()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    copy(INPUTS / "README.md", OUT / "README.md", kind="generated")
    conversations(email, now)
    rules()
    skills(args.impeccable_license)
    journal()
    source(head, now)
    evidence(args.scratch, head, now, email)
    git_section(head, email, now)
    count = manifest(now, head)

    problems = scan(email)
    if problems:
        sys.exit("Secret scan FAILED; no ZIP written:\n  " + "\n  ".join(problems[:50]))

    zip_path = SUBMISSION / f"{PKG_NAME}-{now[:10]}.zip"
    zip_path.unlink(missing_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted(OUT.rglob("*")):
            if f.is_file():
                z.write(f, f"{PKG_NAME}/{f.relative_to(OUT).as_posix()}")
    print(f"Package: {OUT}\nFiles: {count} (+ MANIFEST.md, manifest.json)\nRedacted files: {len(redactions)}\nMissing evidence items: {len(missing)}\nSecret scan: clean\nZIP: {zip_path} ({zip_path.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
