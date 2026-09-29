# Plan: Automatic deploys from GitHub
- **Date:** 2026-09-29 17:30
- **Study:** [../study/2026-09-29-1730-github-auto-deploy.md](../study/2026-09-29-1730-github-auto-deploy.md)
- **Status:** in-progress

## Tasks
- [x] 1. `.vercelignore`: keep uploading `doc/fixtures/` and keep excluding the rest of `doc/` → `build(vercel): upload the proxy fixtures the tests replay`
- [x] 2. Build command: run the test suite on an in-build SQLite file, then `migrate` over `DATABASE_URL_UNPOOLED`. A test failure fails the build. Check it first with a local `vercel build`-style run of the same command → `build(vercel): gate every deployment on the test suite`
- [x] 3. Local check that a failing test would stop the build: run the build command with a deliberately broken test in a scratch copy, which is never committed
- [x] 4. Wiki: in `deployment.md`, the Git workflow, a **rollback runbook**, a **security-incident runbook**, the "additive migrations only" rule and Neon branch housekeeping → `docs(wiki): …`, committed in the same push
- [x] 5. Enable Git deploys: remove `git.deploymentEnabled: false` from `vercel.json` → `build(vercel): deploy automatically from GitHub`
- [x] 6. Push a throwaway branch `ci/preview-check` and confirm that:
  - Vercel builds a **preview**;
  - the build log shows the tests passing;
  - Neon created a **separate database branch** (a branch-specific `DATABASE_URL` for Preview).

  Run the smoke test against it (1 short paid reply, `--paid short`). Then delete the GitHub branch.
- [ ] 7. Push `main`. This is the first automatic production release. Watch the build, confirm that `lightchat-five.vercel.app` serves the new deployment, and run the production smoke test (1 short paid reply)
- [ ] 8. Verify: all tests pass locally, both builds were green, `git status` is clean. Set plan `Status: awaiting-rendezvous`

**Paid proxy calls:** 2 short replies.

## Blocked On
Nothing. The GitHub connection is verified.

## Notes
- Task 3: in a scratch copy with a deliberately failing test, the build command exited 1 and `migrate` never ran.
- Task 6, first push: the **gate caught a real problem**. With Vercel's `REPLY_MAX_SECONDS=260`, the test for the local 20-minute limit failed, so the build failed and nothing was deployed. Fixed in `babe280` (the test pins its own limit). The rerun passed 140/140 in the build.
- Task 6: **Git previews get an isolated Neon branch.** A sign-up made on the preview can't sign in on production. The preview smoke test passed 28/28 (1 paid reply). Branch `ci/preview-check` was deleted from GitHub; its Neon branch expires with the preview.
- Test data: `isocheck…` and `smoke950b04e2` exist only on the preview's Neon branch, not in production.
