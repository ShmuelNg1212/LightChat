# Plan: Assessment submission package

- **Date:** 2026-09-29 14:56
- **Study:** [../study/2026-09-29-1456-assessment-package.md](../study/2026-09-29-1456-assessment-package.md)
- **Status:** in-progress

> **Approved 2026-09-29, with changes from the Gardener:**
> - Transcripts go in as **raw JSONL**. The derived `readable/` renderings are dropped. Only the required minimal redactions (email, test passwords) are applied to the copies.
> - The **skills list** and the **assessor README** are written only inside the gitignored `submission/` folder, never committed (task 3 changes accordingly).
> - The two open decisions were left open, so the recommended defaults apply: readable git log only (no bundle), and home paths kept.

No application behavior changes: no edits to app code, templates, static files, migrations or tests. Output goes to `submission/`, which is gitignored and never uploaded.

## Package layout

```
submission/
├── lightchat-assessment-package/
│   ├── README.md                      assessor guide: what this is, how to run, journeys to check (new, labeled retrospective where it summarises)
│   ├── MANIFEST.md, manifest.json     every file: path, size, SHA-256, source, kind (original | redacted copy | generated), plus missing evidence and redactions
│   ├── 01-conversations/
│   │   ├── SESSION-INDEX.md           chronological index (generated from JSONL timestamps; the missing sessions named precisely)
│   │   └── jsonl/                     raw main-session + 2 subagent logs and their .meta.json (copies; only email and test passwords redacted)
│   ├── 02-project-rules/              AGENTS.md, CLAUDE.md, PRODUCT.md, DESIGN.md, .impeccable/ config, surface brief, design.json
│   ├── 03-skills/
│   │   ├── SKILLS-USED.md             confirmed vs uncertain usage, with evidence (transcript timestamps), source, version, licence
│   │   └── impeccable-4.4.0/          the plugin's text files (skills, agents, hooks, plugin.json) + upstream Apache-2.0 LICENSE; no binaries
│   ├── 04-journal/                    doc/study, doc/plan, doc/design, doc/wiki (copies)
│   ├── 05-source/
│   │   ├── repository-snapshot/       `git archive` of the submitted commit (tracked files only: app, tests, requirements.txt, .python-version, .env.example, fixtures, docs)
│   │   └── requirements-freeze.txt    `pip freeze` of the working .venv (generated; no lockfile exists in the repo)
│   ├── 06-evidence/
│   │   ├── test-results/              full test run at packaging time (verbose output, date, Python/Django versions, commit)
│   │   ├── screenshots/               core-app rendezvous (pre-rebrand UI), rebrand inspection rounds, finish-review captures, logo drafts, favicon checks
│   │   ├── verification-scripts/      the scratchpad scripts whose creation appears in the transcript (e2e, screenshots, axe audit, keyboard, live, icons, logo, contrast); test passwords redacted
│   │   └── api-samples/               doc/fixtures/proxy (already redacted captures)
│   └── 07-git/                        REPOSITORY.md (no remote configured, submitted commit, branch), git-log.txt (readable history, email redacted), git-status.txt
└── lightchat-assessment-package-2026-09-29.zip
```

## Redaction rules (copies only; originals untouched)

| What | Replacement | Where |
|---|---|---|
| Your email address | `[REDACTED_EMAIL]` | Transcripts, git log |
| Local test passwords (`[REDACTED_TEST_PASSWORD]`, `[REDACTED_TEST_PASSWORD]`, `[REDACTED_TEST_PASSWORD]`, `[REDACTED_TEST_PASSWORD]`) | `[REDACTED_TEST_PASSWORD]` | Transcripts, verification scripts |
| `.env` values | Never copied. A scan fails the build if any value appears anywhere. | Everywhere |
| `/Users/shm` home paths | **Decision below** | Transcripts |

Excluded entirely: `.env`, all `*.sqlite3` databases, `.venv/`, `node_modules/`, `__pycache__/`, `~/.impeccable/bin` (binary), WhatsUp and other projects' sessions, the unrelated 2026-09-28 workspace marker, and the scratchpad file `sidecar.py` (its creation isn't in the transcript).

## Tasks

- [ ] 1. Add `submission/` to `.gitignore`. → `chore: ignore the local submission package`
- [ ] 2. Add `tools/package_submission.py`, a stdlib-only script that builds the layout above. It copies originals, writes the redacted copies and the labeled generated files, and computes the manifest. It then **scans the finished folder** for every `.env` value, the email, the test passwords, `*.sqlite3`, `.env` files and dependency folders, and aborts if anything is found. Last, it zips the folder. → `chore(tools): add the submission packaging script`
- [ ] 3. Write the assessor README and SKILLS-USED.md in `submission/inputs/` (gitignored, **not committed**; the script copies them in). Summaries are marked *retrospective (written 2026-09-29 at packaging time)*. No commit.
- [ ] 4. Fetch Impeccable's upstream `LICENSE` (Apache-2.0) for inclusion. Run the full test suite verbosely and capture it. Run the packaging script. It makes no commit, because its output is gitignored.
- [ ] 5. Verify:
  - unzip into the scratchpad and re-run the secret scan on the extracted files;
  - check that every manifest SHA-256 matches;
  - open the README, the session index and one readable transcript to confirm they read correctly;
  - confirm the repo's `git status` is clean and the tests still pass;
  - report the ZIP's path and size.

  Set Status to `awaiting-rendezvous`. → `docs(plan): mark assessment-package ready for rendezvous`
- [ ] **After acceptance (Sync):** add the packaging command to `doc/wiki/setup.md`, and mark the plan done. → `docs(wiki): sync after assessment-package`

## Decisions for you

1. **Git history:** a readable log only, or also a full `git bundle`? The bundle contains your email in every commit's author field, and that can't be redacted. Recommendation: log only.
2. **Home paths in transcripts:** keep `/Users/shm/…` as is (readable; reveals only your macOS username), or replace it with `~`? Recommendation: keep.

## Blocked On

Nothing, apart from your approval and the two decisions.
