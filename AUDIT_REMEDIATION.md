# Audit Remediation Record

**Package:** `schedule-updater`  
**Rebuild version:** 2.1.0  
**Scope:** Rebuild of the uploaded `SKILL.md` workflow and creation of a self-contained local engine, references, fixtures, and tests.

## Important source limitation

Only the previous `SKILL.md` was supplied for this audit. The prior helper script, reference documents, and original test suite were not supplied as source files. This package is therefore a clean, independently testable reconstruction based on the skill's stated contract and the identified audit findings; it is not a claim that unseen original source code was patched in place.

## Findings addressed

| Prior finding | Remediation in this package | Verification |
|---|---|---|
| Operation mode hardcoded to `RECONCILE` | CLI requires one of four modes; reconciliation enforces mode-specific action limits. | Regression tests for each mode and no-write preview. |
| Unsafe interpolation of raw text into shell commands | Engine accepts a file path or stdin; skill forbids shell interpolation of source text and recommends argv execution or proper shell quoting. | Shell-like source content remains data; no subprocess is called by the engine. |
| Skill root and relative paths could diverge | `SKILL.md` requires resolving the actual installed root; README explicitly covers hosts that only snapshot the skill file. | Documentation assertions and clean-root CLI smoke test. |
| Hardcoded reference year | No `--reference-year` is used; incomplete dates stay ambiguous. | Yearless-date tests. |
| Incomplete pagination and moved-event misses | Host workflow requires all pages and fetches mappings by event ID even outside the new date window; engine explicitly expects a complete normalized snapshot. | Workflow docs and reconciliation tests. |
| Uncertain connector update semantics | Host must inspect the actual tool contract; PATCH only intended fields or merge the full resource with concurrency control; stop if preservation is not safe. | Explicit acceptance boundary documented. Actual connector behavior remains untested here. |
| Invalid all-day payload shape | Google API-style resource uses date-only start and exclusive date-only end; timezone lives on timed start/end only. | All-day and payload-shape tests. |
| Prompt-injection phrase stripping could corrupt data | Suspicious instructions are warnings only; source text is preserved and never executed. | Prompt-injection preservation test. |
| Fixed temporary filenames could collide | Per-run private temporary directories are required by skill instructions and used in documented examples. | Workflow docs. Host runtime compliance must be verified in deployment. |
| Duplicate retry after uncertain create | Stable source IDs, slot/anchor keys, private marker support, state mappings, and a stop-and-reconcile rule for uncertain outcomes. Exactly-once is not claimed. | State, source-ID, and retry-model regression tests. |
| Write response alone treated as proof | `record-verified` verifies expected core fields before committing mapping; skill mandates live read-back. | CLI test validates mapping only after expected/actual match; live connector read-back is a host responsibility. |
| Generic 403 misclassified as expired auth | Skill distinguishes auth expiry, access scope, read-only target, rate limit and transient failures. | Workflow contract documented. Actual connector error taxonomy remains host-specific. |
| State permission and lock edge cases | Existing parent directory permissions are not changed; state writes are atomic and mode-restricted; lock-write failure cleanup and malformed-state protection are tested. | Unit tests. |
| Resource exhaustion via large inputs | Enforce a 100 MiB input limit and a 100-million-pixel image limit before OCR. | Input-size and image-pixel regression tests. |
| Unspecified optional fields could clear user-authored data | Source-field presence is tracked; omitted/blank descriptions and locations are excluded from change comparisons, and update plans include only explicit changed fields. Description/recurrence changes require confirmation; an existing recurrence omitted by the source becomes ambiguous. | Regression tests for preservation, confirmation, and patch field selection. |
| Source mappings could leak across same-named schedules | Mappings are scoped by calendar ID and stable logical source ID; legacy mapping fallback only applies when the source ID equals the filename. | Source-ID isolation regression tests. |
| Recurrence values were under-validated | Stricter supported RRULE subset; `COUNT` and `UNTIL` mutually exclusive; BYDAY and numeric fields validated; DTSTART/UNTIL type and ordering checks. | Recurrence regression tests. |

## Non-goals and remaining external checks

- This package does not implement OAuth or call Google Calendar APIs directly.
- The host agent must prove that its registered calendar connector's create/update payloads, pagination, all-day semantics, recurrence representation, read-back and concurrency semantics match this workflow.
- Do not enable production writes solely on the basis of local tests. Perform a controlled test in a dedicated calendar first.
