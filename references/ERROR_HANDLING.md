# Connection, Execution, and Recovery

## Connection states

- `NO_CONNECTOR`: no calendar tool is registered.
- `DISCONNECTED`: integration exists but account connection is absent.
- `AUTH_EXPIRED`: structured provider result confirms invalid/expired authentication.
- `NO_CALENDAR_ACCESS`: target calendar cannot be accessed or required scopes are missing.
- `READ_ONLY_CALENDAR`: target calendar is readable but cannot be modified.
- `HEALTHY`: connection and requested operation appear authorized.

A generic 403 is not sufficient to classify expired authentication. Inspect provider error codes and tool schema. Connection check must be live for each non-preview run. Never request credentials in chat.

## Failure classes

- `INPUT_UNSUPPORTED`: unsupported format or missing parser dependency.
- `EXTRACTION_PARTIAL`: OCR/native parsing produced uncertain entries.
- `VALIDATION_BLOCKED`: missing or ambiguous title/date/time/timezone/recurrence.
- `CONNECTION_BLOCKED`: connector absent, disconnected, unauthorized, or read-only.
- `CALENDAR_READ_FAILED`: list/get failed; do not plan writes on incomplete data.
- `AMBIGUOUS_MATCH`: more than one plausible target or weak identity evidence.
- `WRITE_FAILED`: provider/connector returned a structured failure.
- `WRITE_UNVERIFIED`: write was accepted or returned an ID but read-back failed or disagreed.
- `STATE_COMMIT_FAILED`: calendar write verified but local mapping could not be committed; reconcile by marker before retrying.
- `RATE_LIMITED` / `TRANSIENT`: retry only when the connector gives a safe retry signal, using bounded backoff and idempotent recovery.

## Recovery rules

1. Never blindly retry a create when the previous result is unknown. Search the relevant calendar and source marker first.
2. Save verified event IDs after each operation, not only at the end of a batch.
3. If a batch partially succeeds, retain successful events and their mappings. Do not roll them back automatically.
4. If an update fails, re-read the existing event before retrying, especially if concurrency controls are available.
5. If persistent state is malformed, preserve it unchanged and report the path; do not replace it with an empty state file.
6. If a lock file exists, wait briefly. If it remains, stop and report possible concurrent operation or stale lock; never delete another process's lock automatically.
7. All intermediate files are per-run and permission-restricted. Avoid logging full source documents, credentials, or unnecessary calendar details.
8. In the final report, separate verified success, failure, unverified outcome, skipped duplicate, ambiguity, and pending recovery.
