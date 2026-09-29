# Study: Assessment submission package

- **Date:** 2026-09-29 14:56
- **Request:** Prepare an assessment submission package. Study the project files and exported transcripts, write a packaging plan, and pause for approval before assembling. Documentation and packaging only; no change to application behavior. Preserve originals, share redacted copies, exclude secrets, private databases, dependency folders and unrelated conversations. Don't invent transcripts, results, skill usage or decisions; label retrospective summaries; identify missing session exports precisely. After approval: assemble, verify, ZIP locally, report the location; don't upload. Gardener's addition: no GitHub repository is linked yet, so the package output must be gitignored.
- **Status:** approved 2026-09-29 with changes recorded in the plan (together with the [plan](../plan/2026-09-29-1456-assessment-package.md))

## Intended Outcome

An assessor receives one ZIP and can, without asking anyone:

- follow how the project was built, from the conversation records in chronological order;
- see the working agreement, studies, plans, design brief and wiki that governed each step;
- see which skills were used, with source, version and licence, and how certain each usage claim is;
- run the app and its tests from the included source and setup instructions;
- check the core user journeys with a README;
- trust the package, because a manifest lists every file, what is missing, and every redaction.

Acceptance criteria:
- The ZIP contains no `.env` values, no proxy keys, no email address, no database files, no `.venv`/`node_modules`, and no conversations from other projects. This is verified by an automated scan of the extracted ZIP.
- Originals are untouched; the repo's `git status` is clean afterwards apart from the ignored package folder.
- Every newly written summary is labeled *retrospective*, and every generated file says when and how it was generated.
- The manifest lists every file with its size and SHA-256, its source path, and whether it is original, redacted copy, or generated.

## Current State (evidence found)

### Conversation records

Claude Code keeps session transcripts as JSONL under `~/.claude/projects/-Users-shm-litechat-midterm/`.

| Record | Span (UTC) | Content | Status |
|---|---|---|---|
| **Main session** `41aceb7c-abfa-464c-b227-5a085f4011ca.jsonl` | 2026-09-29 04:47 → ongoing (12:47 Manila onward) | Everything from the first pasted study through this request: 363 user entries, 791 assistant entries, 266 Bash calls. The session is still running, so the packaged copy is a snapshot. | Available (12.5 MB) |
| Subagent `agent-a4b965dd354cc73ab.jsonl` + `.meta.json` | 06:31 → ~06:44 | Impeccable finish reviewer (review, recapture request, verdict) | Available |
| Subagent `agent-acad09e632ddc1bba.jsonl` + `.meta.json` | 06:46 → ~06:50 | Impeccable documenter (wrote DESIGN.md) | Available |
| Memory folder | n/a | Empty | Nothing to include |

**Missing session exports (precisely):**
1. **The session that produced the original study** `doc/study/2026-09-29-1243-litechat-core.md` (dated 2026-09-29 12:43 Asia/Manila). It was pasted into the main session at its start. Its own text says it ran in a workspace with `work/` and `outputs/` folders, created `outputs/litechat/`, read GitHub and litechat.ai through a browser, and had shell DNS failures. None of that matches this machine's Claude Code project store, so its transcript is **not available here**. Only you can export it, from wherever it ran.
2. **Claude Code `/export` text exports.** None exist for any session; only the raw JSONL logs. The package can include a *derived* readable rendering, labeled as generated from the JSONL, but it is not an export.
3. **The last turns of the main session** (after the snapshot is taken during assembly) will not be in the package.

**Unrelated, to be excluded:**
- `~/.claude/projects/-Users-shm-WhatsUp/` (two sessions of a different project);
- a Claude desktop scratch-workspace folder dated 2026-09-28, which holds only a 78-byte workspace-release marker and no conversation.

**Privacy scan of the transcripts** (patterns counted, values never printed):
- **Proxy keys:** the exact `.env` values appear **0 times**. No key-shaped `sk-…` strings.
- **Email:** your email address appears 4 times in the main session and 4 in the subagent logs (session context). → **redact**.
- **Test passwords:** throwaway passwords for local practice accounts (`[REDACTED_TEST_PASSWORD]`, `[REDACTED_TEST_PASSWORD]`, `[REDACTED_TEST_PASSWORD]`, `[REDACTED_TEST_PASSWORD]`) appear in scripts. → **redact** in copies.
- **Home paths:** `/Users/shm/...` appears about 4,200 times. It reveals the macOS username, which also matches the git author name. → decision below.

### Skills and tooling (from the transcript's tool calls, not memory)

| Item | Evidence | Certainty |
|---|---|---|
| **Impeccable** plugin 4.4.0 (`github.com/pbakaus/impeccable`, Apache-2.0; installed `plugin.json` says 4.4.0; the newest public tag found is `skill-v4.3.1`; scripts `VERSION` 0.1.6) | `Skill` tool called once (`impeccable:impeccable`, init, 05:58 UTC). Reference files opened: init, shape, new-work, craft-floor, clarify, document (documenter), live-setup. Script verbs run: `context`, `concept-seed` (seed `00ad6455` + choice telemetry), `surface-brief write/read`, `detect-csp`, `detect`, `hooks status`, `hooks ignore-value`. Agents run: `impeccable-finish-reviewer`, `impeccable-documenter`. The PostToolUse design hook ran on UI edits (hook messages in the transcript). | **Confirmed** |
| Impeccable references *not* opened (critique, audit, harden, polish playbooks, etc.) | Those passes were run from the skill's guidance and the plan, not by loading their reference files | **Confirmed not loaded.** Record the passes as "performed following the plan", not as "command X run" |
| Other listed skills (artifact-design, docs, frontend, deep-research, etc.) | Never invoked (Skill tool used once in total) | **Confirmed unused** |
| The skill set used by the original-study session | Unknown; that transcript is missing | **Uncertain** |
| Verification tools (not skills) | Installed in the scratchpad: `puppeteer-core` 25.12, `axe-core` 4.13, `fonttools` 4.60 (+ brotli). Headless Chrome was used for screenshots and icon rendering. | Confirmed (from install commands) |

**Redistribution:** Impeccable is Apache-2.0, so copying its text files is permitted, with the licence. The cached plugin has no `LICENSE` file, so the upstream `LICENSE` would be fetched and included alongside. The runtime binary it downloaded (`~/.impeccable/bin`) is excluded: it is an executable, isn't needed to read the skill, and sits outside the plugin.

### Project files

| Area | Where | Notes |
|---|---|---|
| Working agreement | `AGENTS.md`, `CLAUDE.md` (identical) | Plus `PRODUCT.md`, `DESIGN.md`, `.impeccable/config.json`, `.impeccable/live/config.json`, `.impeccable/surfaces/`, `.impeccable/design.json` |
| Journal | `doc/study/` (4), `doc/plan/` (3, plus this one), `doc/design/` (brief, brand, drafts, contrast script) | Historical, never rewritten |
| Wiki | `doc/wiki/` (5 pages) | Current state |
| App source and tests | `config/`, `accounts/`, `billing/`, `catalog/`, `chat/`, `proxy/`, `templates/`, `static/`, `manage.py` | 133 tests; no stored test-result file exists |
| Dependencies | `requirements.txt` (pinned direct deps), `.python-version` | **No lockfile exists.** A `pip freeze` of the working `.venv` (15 packages) can be generated, labeled as such. |
| Setup | `doc/wiki/setup.md`, `.env.example` (placeholders only) | |
| API samples | `doc/fixtures/proxy/` (4 redacted captures) | Already redacted at capture |
| Screenshots | Committed: logo drafts, app icons. Local only: `.impeccable/review/` (34 finish-review captures). Scratchpad (temporary, lost when the session ends): 16 from the core-app rendezvous (pre-rebrand Litechat UI), 63 rebrand inspection shots, 4 logo previews | Worth preserving now |
| Demo/verification scripts | Scratchpad: 20 scripts (e2e, screenshots, audit, keyboard, live, icons, logo, contrast); one unexplained file (`sidecar.py`) | Include only scripts whose creation appears in the transcript |
| Git | No remote; HEAD `f67a9fc` (79 commits); working tree clean; author name and email in commit metadata | |
| Excluded by rule | `.env`, `db.sqlite3` (dev DB with your account), practice DB, `.venv/`, `node_modules/`, caches | |

## Options & Tradeoffs

| Option | Pros | Cons | Effort | Risk |
|---|---|---|---|---|
| **Package folder + ZIP under `submission/` (gitignored)**, built by a script kept in the repo (recommended) | Repeatable; the manifest and scans are automatic; originals untouched | One more script to commit | Low | Low |
| Hand-assemble by copying | No new code | Easy to miss or leak something; not repeatable | Medium | Medium |

For git history:

| Option | Pros | Cons |
|---|---|---|
| **Readable `git log` text (email redacted) + `git archive` source snapshot of HEAD** (recommended) | Readable, no private metadata, source exactly equals the submitted commit | Assessors can't `git checkout` older commits |
| Also include a `git bundle` (full history) | Fully verifiable history | Carries your email in every commit's author field; it can't be redacted without rewriting history |

## Recommendation

Build the package with a small, committed, documentation-only script (`tools/package_submission.py`). It copies originals into `submission/lightchat-assessment-package/`, writes redacted copies of the transcripts, generates the labeled derived files (session index, readable transcript renderings, test results, `pip freeze`, git log, manifest), scans the result for secrets, and zips it. `submission/` is added to `.gitignore`. No application code, template, static file or test changes.

## Exogenous Inputs

| Input | Why | Status |
|---|---|---|
| Transcript of the original-study session | Chronological completeness | **Missing.** Listed in the manifest; you may add it later |
| Repository URL | Required field | **None**: record "no remote configured" |
| Your decision on the git bundle and home paths | Privacy vs. verifiability | Needed (see the plan's decisions) |

## Risks & Open Questions

- **The main session keeps growing.** The snapshot is taken during assembly; the packaging turn itself will be only partly included, and the manifest says so.
- **Scratchpad files vanish** when this session ends. Assembling soon preserves them.
- **Readable renderings** of the JSONL are derived and truncated (tool outputs shortened, images omitted). The redacted JSONL copies remain the complete record.
- **Large files:** the transcripts (about 18 MB with embedded screenshots) compress well. The ZIP is estimated at 15–25 MB.
