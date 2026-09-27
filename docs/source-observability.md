# Source observability

`fetch_with_fallback` records the elapsed time of every source attempt in
`SourceAttempt.duration_ms`. The value is measured locally with a monotonic
clock and is intended for operational diagnosis, not for benchmarking a
provider across machines.

The audit serializer exposes the field under `data.attempts[*].duration_ms`.
Together with `status`, `accepted_rows`, `observed_at`, and
`error_present`, an API or Agent can distinguish:

- a fast source that returned unusable rows;
- a slow source that eventually succeeded;
- a source that failed before the fallback was used; and
- a local cache read after all live sources were unavailable.

Raw exception messages are still omitted from the serialized audit summary.
This keeps the public contract useful for troubleshooting without exposing
provider credentials or request details.
