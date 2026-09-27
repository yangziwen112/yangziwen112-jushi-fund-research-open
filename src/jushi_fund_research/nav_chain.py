"""A small, auditable multi-source historical NAV chain."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Callable, Iterable, Mapping, Sequence

from .data_policy import (
    DataStatus,
    NormalizedNav,
    SourceAttempt,
    now_utc,
    validate_nav_rows,
)

Fetcher = Callable[[], Iterable[Mapping[str, Any]]]


@dataclass(frozen=True)
class NavChainResult:
    points: tuple[NormalizedNav, ...]
    status: DataStatus
    selected_source: str | None
    attempts: tuple[SourceAttempt, ...]
    message: str


def fetch_with_fallback(
    sources: Sequence[tuple[str, Fetcher]],
    *,
    cache: Iterable[Mapping[str, Any]] | None = None,
    min_rows: int = 1,
) -> NavChainResult:
    """Fetch the first source that passes validation.

    Source order is intentional: primary endpoint, declared fallback(s), then
    local cache. No synthetic or stale value is generated when all branches
    fail; the caller receives ``INSUFFICIENT`` and the audit trail.
    """

    attempts: list[SourceAttempt] = []
    for index, (name, fetcher) in enumerate(sources):
        observed_at = now_utc()
        started = perf_counter()
        try:
            points = validate_nav_rows(fetcher(), source=name)
            duration_ms = round((perf_counter() - started) * 1000, 3)
            if len(points) >= min_rows:
                status = DataStatus.PRIMARY if index == 0 else DataStatus.FALLBACK
                attempts.append(
                    SourceAttempt(
                        name, len(points), status.value,
                        observed_at=observed_at, duration_ms=duration_ms,
                    )
                )
                return NavChainResult(
                    tuple(points), status, name, tuple(attempts),
                    f"accepted {len(points)} rows from {name}",
                )
            attempts.append(
                SourceAttempt(
                    name, len(points), "rejected", "not enough valid rows",
                    observed_at, duration_ms,
                )
            )
        except Exception as exc:  # adapters must not break the next branch
            attempts.append(
                SourceAttempt(
                    name, 0, "failed", str(exc), observed_at,
                    round((perf_counter() - started) * 1000, 3),
                )
            )

    if cache is not None:
        observed_at = now_utc()
        started = perf_counter()
        points = validate_nav_rows(cache, source="cache")
        duration_ms = round((perf_counter() - started) * 1000, 3)
        if len(points) >= min_rows:
            attempts.append(
                SourceAttempt(
                    "cache", len(points), DataStatus.CACHE.value,
                    observed_at=observed_at, duration_ms=duration_ms,
                )
            )
            return NavChainResult(
                tuple(points), DataStatus.CACHE, "cache", tuple(attempts),
                "live sources unavailable; using validated local cache",
            )
        attempts.append(
            SourceAttempt(
                "cache", len(points), "rejected", "not enough valid rows",
                observed_at, duration_ms,
            )
        )

    return NavChainResult(
        tuple(), DataStatus.INSUFFICIENT, None, tuple(attempts),
        "no source produced enough validated historical NAV rows",
    )
