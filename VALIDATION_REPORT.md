# Validation Report — Schedule Updater 2.1.0

**Validation date:** 2026-10-25  
**Scope:** deterministic local engine, synthetic fixtures, mocked calendar data, CLI, package metadata, clean-working-directory smoke run  
**Live Google Calendar writes:** not performed

## Results

| Check | Result | Evidence |
|---|---|---|
| Unit/regression suite | **PASS — 61 tests** | `python -m unittest discover -s tests -q`; 61 tests, zero failures. |
| Pytest run | **PASS — 61 tests** | `python -m pytest -q`; 61 passed. |
| Python compilation | **PASS** | `python -m py_compile scripts/schedule_engine.py tests/test_schedule_updater.py`. |
| CLI command discovery | **PASS** | `python scripts/schedule_engine.py --help` exposes `extract`, `reconcile`, `state-list`, and `record-verified`. |
| Clean-working-directory smoke test | **PASS** | Invoked the engine by absolute path from `/tmp`; the sample file was read successfully. |
| Sample extraction | **PASS** | 3 entries extracted, 3 valid, 0 ambiguous. |
| Preview-only plan | **PASS** | 3 `PREVIEW` operations; `calendar_writes_performed=false`; no Calendar connector was invoked. |
| Wheel metadata build | **PASS** | `python -m pip wheel . --no-deps --no-build-isolation` completed successfully. The wheel is metadata-only by design; install the complete Agent Skill folder for runtime use. |
| ZIP archive integrity | **PASS** | Final archive checked with `unzip -t`; all entries validated. |

## Regression coverage

The 61 tests cover:

- Markdown, TXT/pasted text, HTML, DOCX, image OCR, native PDF extraction, and scanned-PDF OCR fallback.
- Ambiguous/yearless dates, AM/PM ambiguity, invalid timezone, overnight handling, and all-day exclusive end dates.
- Supported recurrence subset, invalid fields, `COUNT`/`UNTIL` conflict, `UNTIL` type and ordering checks.
- All four operation modes and no-write preview enforcement.
- Duplicate detection, mapped events, source-ID isolation, moved-event confirmation, and no implicit deletion.
- Preservation of unspecified description/location fields; confirmation for replacing user-authored descriptions or changing recurrence; explicit `patch_fields` generation.
- Verified state mapping, read-back comparison, atomic state writes, lock collision/failure, malformed state preservation, and parent-directory permission preservation.
- Shell-like text remaining inert, prompt-injection warnings without silently altering raw source text, input and image size limits, CLI contracts, skill-document invariants, and no deletion operations in plans.

## External validation still required

The engine deliberately does not call Google Calendar. These local tests **do not prove** live OAuth behavior, connector pagination schema, calendar permissions, write payload translation, PATCH versus full-resource replacement behavior, recurring-instance semantics, notifications, or live read-after-write verification. Run a controlled create/read/update/read test in a dedicated test calendar before enabling routine production mutations. Do not use destructive tests against the production calendar.
