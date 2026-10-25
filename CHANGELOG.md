# Changelog

## 2.1.0 — Deep-audit hardening release (2026-10-25)

- Enforced all four operation modes in the deterministic planner; `PREVIEW_ONLY` remains free of calendar reads and writes, `CREATE_ONLY` cannot update, and `UPDATE_EXISTING` cannot create unmatched events.
- Removed hardcoded reference-year behavior; unresolved yearless and ambiguous numeric dates are flagged rather than guessed.
- Added source field-presence semantics: blank/unspecified description and location do not clear existing user data; updates return an explicit `patch_fields` list.
- Required confirmation before replacing a description supplied by a schedule or changing recurrence; an existing recurring event paired with a source that omits recurrence is flagged for confirmation.
- Fixed logical source-ID namespacing and verified-state CLI handling.
- Emits Google Calendar API resource shape for all-day events (`start.date`, exclusive `end.date`) and timed events (timezone nested in `start`/`end`, not a nonstandard top-level field).
- Tightened recurrence validation, including `COUNT`/`UNTIL` mutual exclusion, supported field/value checks, DTSTART/UNTIL type checks, and end-boundary validation.
- Hardened state persistence: atomic writes, restrictive state/lock/temp file modes, no unnecessary parent-directory chmod, malformed-state preservation, and safe lock cleanup.
- Added bounded input handling, image-pixel limits, source provenance, and prompt-injection warnings that preserve source text instead of silently deleting it.
- Added safe retry guidance for uncertain remote creates, source-slot markers, mapping-based recovery, connector pagination rules, and read-after-write verification requirements.
- Expanded the local regression suite to **61 tests**, including mapped-field preservation, description replacement confirmation, recurrence mismatch handling, and exact patch-field selection.

### Validation boundary

The deterministic Python engine does not call Google Calendar. Local tests use synthetic files and mocked calendar data. Actual connector OAuth, pagination, update/patch semantics, recurrence representation, permissions, and live read-after-write must be validated by the host agent against a dedicated test calendar before production writes.
