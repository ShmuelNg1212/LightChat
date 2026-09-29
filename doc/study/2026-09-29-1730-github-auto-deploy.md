# Study: Automatic deploys from GitHub
- **Date:** 2026-09-29 17:30
- **Request:** "yes automate deploys from github, but this means i still can rollback in case of bugs or urgent security breaches right?"
- **Status:** awaiting-approval

## Intended Outcome
- A push to `main` on GitHub deploys to production (https://lightchat-five.vercel.app) with no manual command.
- A push to any other branch (or a pull request) creates a **private preview**, ideally with its **own Neon database branch**, so previews stop sharing production data.
- **A commit that fails the test suite never goes live.** Its build fails and the current version keeps serving.
- The Gardener can still **roll back** in one click and **take the site offline** within seconds. Both are documented in the wiki.

## Current State
- Sources: [deployment.md](../wiki/deployment.md) and `vercel.json`.
- The project is connected to `ShmuelNg1212/LightChat`, with `main` as the production branch.
- `git.deploymentEnabled: false`, so pushes deploy nothing. All deploys are manual CLI commands.
- The build runs only `migrate`. Tests run only locally.
- `.vercelignore` excludes `doc/`, which also removes the proxy fixtures that `proxy/tests/test_captured.py` replays.

## Rollback: yes, with caveats
Source: [Instant Rollback](https://vercel.com/docs/instant-rollback), read 2026-09-29.

| Question | Answer on Hobby |
|---|---|
| Can I undo a bad release? | **Yes, instantly.** Project page → Production tile → **Instant Rollback**, or `npx vercel@latest rollback`. Domains move back in seconds, with no rebuild |
| How far back? | **Only to the immediately previous production deployment** (Pro can go further). For older versions, revert the commit on GitHub (the revert then auto-deploys), or promote an older deployment with `vercel promote <url>` |
| What happens to new pushes after a rollback? | Vercel **pauses auto-deploys to the live domain** until you **Undo Rollback** (dashboard) or run `vercel promote`, so a follow-up push can't undo your rollback by accident |
| Does rollback undo database changes? | **No.** Migrations stay applied. This is why releases must keep database changes backward-compatible (see Risks) |
| Security breach? | Rollback **keeps the old build's environment variables**, so it doesn't rotate leaked secrets. Fastest response: switch Deployment Protection to **All Deployments** (the whole site is private within seconds, free), rotate the keys, then deploy again |

## Options & Tradeoffs
| Option | Pros | Cons | Effort | Risk |
|---|---|---|---|---|
| **A. Turn on Git deploys, and run the test suite in the Vercel build before migrations** | A failing commit never goes live. No extra service, and it's free (tests use mocks, with no paid calls). About 15 s more build time | The tests need the proxy fixtures uploaded (they're redacted captures, no secrets) | Low | Low |
| B. Turn on Git deploys only | Simplest | A broken commit on `main` goes straight to production | Trivial | Medium |
| C. GitHub Actions CI plus Vercel deployment checks | Standard CI with a separate status on GitHub | Another service to configure. Whether Hobby supports blocking checks is unverified | Medium | Low |

## Recommendation
Option A:
1. `vercel.json`: remove `git.deploymentEnabled: false`, so every branch deploys (Vercel's default).
2. Build command: run the tests first, then `migrate`. The tests run on an in-build SQLite file, so they never touch Neon or the proxy.
3. `.vercelignore`: keep uploading `doc/fixtures/` (the tests need it) and keep excluding the rest of `doc/`.
4. Check that a pushed test branch gets its **own Neon branch**. If it does, previews are isolated from production data. If not, report it.
5. Wiki: a runbook for rollback and security incidents.

This follows Vercel's default Git workflow. The only addition is the test gate in the build command.

## Exogenous Inputs
| Input | Why needed | Status | Owner |
|---|---|---|---|
| Vercel GitHub App access to `ShmuelNg1212/LightChat` | Git-triggered deploys | **verified** (`vercel git connect` succeeded) | — |
| Neon preview branching for Git branches | Isolated previews | **assumed**. It will be checked with one test branch push | Vine |

## Risks & Open Questions
- **Pushing to `main` = releasing.** The push of this change itself will trigger a production deploy. That's the intended first automatic release; the code is unchanged apart from the build step.
- **Migrations run automatically on production** before the new version goes live. A migration that removes or renames something could break the version still serving (and the rollback target). Rule: make database changes additive, and remove old fields one release later. This will be in the wiki.
- **Neon Free allows 10 branches per project.** Each preview branch uses one until the preview expires, so old ones may need deleting in the Neon console.
- **Cost:** $0. Tests make no paid calls. Verification makes about 2 short paid replies (one preview, one production).
