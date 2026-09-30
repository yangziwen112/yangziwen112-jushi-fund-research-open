# Daily maintenance log

This log records small, verifiable maintenance tasks. It is not intended to
manufacture activity; each entry should correspond to a code, test, document,
or reproducibility improvement that can be reviewed independently.

## 2026-09-29

- Area: source fallback and cache validation.
- Change: cache validation failures are now recorded as a failed audit attempt
  and return `insufficient` instead of escaping from `fetch_with_fallback`.
- Change: `min_rows` must be at least one, preventing empty results from being
  accepted as a successful source.
- Evidence: `tests/test_nav_chain.py` adds invalid-cache and parameter-boundary
  tests; the full unit test suite passes locally.
- Next candidate: add a small adapter contract test for source timestamps and
  duplicate-date handling.

## 2026-09-30

- Area: adapter contract and audit timestamps.
- Change: added regression coverage for timezone-aware adapter dates, source
  preservation, and timezone-aware `SourceAttempt.observed_at` values.
- Evidence: `tests/test_data_contract.py`; the test suite must pass before the
  change is committed or pushed.
- Multi-agent handoff: OpenClaw may review source and risk semantics, while
  Codex owns the local implementation, tests, commit SHA, and push evidence.

## Suggested daily rotation

1. Fix one reproducible edge case and add a regression test.
2. Improve one public API or README example and verify it from a clean Python
   environment.
3. Review one data-source or cache boundary and record the evidence.
4. Refactor one small module only when behavior is protected by tests.
5. Review an issue or open a narrowly scoped issue with reproduction steps.

Avoid empty commits, fabricated metrics, generated noise, and unreviewed bulk
rewrites. Push only after local tests and the intended diff have been checked.

## Automation

- GitHub Actions runs the verification workflow once per day and can also be
  started with `workflow_dispatch`.
- The workflow runs the test suite, compiles the package, checks the diff, and
  uploads the log as an artifact. It does not create commits or change code.
- Windows users can run the same check with:

```powershell
.\scripts\daily-maintenance.ps1 -Python "C:\Python314\python.exe"
```
