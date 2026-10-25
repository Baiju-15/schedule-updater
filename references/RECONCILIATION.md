# Reconciliation Contract

## Modes and hard invariants

| Mode | Create | Update | Delete | Calendar reads |
|---|---|---|---|---|
| `PREVIEW_ONLY` | Never | Never | Never | Never |
| `CREATE_ONLY` | Validated new event only | Never | Never | Yes, to prevent duplicates |
| `UPDATE_EXISTING` | Never | Confidently matched event only | Never by default | Yes |
| `RECONCILE` | Validated new event | Confidently matched event | Never by default | Yes |

The mode must be passed unchanged to the engine and checked again at execution time. A preview plan cannot be executed.

## Plan operation classes

- `CREATE`: no confident existing event or duplicate found.
- `UPDATE`: confidently mapped event; the host must still verify connector semantics and mode permission.
- `UNCHANGED`: core fields already match.
- `DUPLICATE_SKIPPED`: an existing identical event is found.
- `AMBIGUOUS_MATCH`: multiple or insufficiently reliable candidates; user confirmation required.
- `FETCH_EXISTING_BY_ID`: persistent mapping exists but event was not included in the list response; fetch it by ID before deciding.
- `NO_MATCH`: no match; `UPDATE_EXISTING` must skip rather than create.
- `PREVIEW`: proposed event in no-write preview mode.

## Matching hierarchy

1. Exact stored mapping for `(calendar_id, slot_key)` whose event ID was retrieved from the calendar.
2. Exact source-slot metadata/marker in an event description/extended properties.
3. Unique exact normalized title, date, start/end, all-day status, timezone where present, recurrence, and location.
4. Unique same-title, same-date time-shift candidate may be proposed as an update for `RECONCILE` or `UPDATE_EXISTING`, but requires user confirmation unless a stable mapping proves source identity.
5. Anything weaker remains ambiguous or unmatched. Do not use title similarity alone to overwrite events.

A moved event may lie outside the revised schedule's date window. Fetch all state-mapped event IDs associated with the source before planning updates. Use a bounded lookback/lookahead for unmapped fallback matching; do not issue unbounded calendar reads.

## Idempotency and state

State path: `~/.schedule_updater_state.json` by default (host may configure a different per-user location). State contains source-to-event mappings, not credentials. Mappings are scoped by `(calendar_id, source_id)` so another schedule in the same calendar is not mistaken for a removed source. The host must use a stable logical source ID across revisions; filename alone is only the fallback. Files use atomic replacement and restrictive permissions. Lock contention means stop instead of overwriting state.

Every event created by the skill should carry a source-slot marker, for example:

`[schedule-updater-key:0123456789abcdef0123456789abcdef]`
`[schedule-updater-anchor:abcdef0123456789abcdef0123456789]`

Store slot and anchor keys in supported private event metadata when the connector permits it. The description markers are a portable fallback for wrappers that do not return private metadata. Do not overwrite user-authored descriptions; append or merge markers deterministically and preserve existing content during updates. Exclude both machine markers when comparing human-authored description text.

Strict exactly-once creation cannot be guaranteed solely by a local file because the process can crash after the remote service accepts a create request. If the response is lost or state has not been committed, search by marker and relevant event fields before retrying. If the outcome remains uncertain, stop and report it.

## Changed source rows and removals

An anchor key uses the stable source ID and provenance anchor; the slot key also incorporates the normalized title. If the title or date changes at an otherwise mapped anchor, require user confirmation because this may be a real change or a row reorder. If the source document is renamed or rows are rearranged, old mappings might not match. Fall back to conservative matching; do not invent a match. A mapping absent from a revised source becomes `POTENTIALLY_REMOVED`; never delete automatically.

## Connector pagination and concurrency

Retrieve every page of relevant existing events and all state-mapped IDs relevant to the source. Deduplicate listing results by event ID. Use actual connector pagination semantics. Avoid simultaneous mutation runs against the same calendar/source; serialize state commits and reconcile again if the calendar changed during planning.

## Event updates

Before updating, inspect whether the connector implements PATCH semantics or full-resource replacement. For PATCH, supply intended changes only. For full replacement, fetch and merge the full resource while preserving all unrelated fields; use ETags or equivalent concurrency control if available. If the adapter cannot guarantee preservation, do not update automatically.
