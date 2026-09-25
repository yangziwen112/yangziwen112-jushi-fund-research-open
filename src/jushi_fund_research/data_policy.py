"""Data quality rules shared by adapters and strategy code.

The module deliberately accepts plain mappings so an adapter can translate an
upstream API without coupling the research logic to a particular provider.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from enum import Enum
from math import isfinite
from typing import Any, Iterable, Mapping


class DataStatus(str, Enum):
    PRIMARY = "primary"
    FALLBACK = "fallback"
    CACHE = "cache"
    INSUFFICIENT = "insufficient"


@dataclass(frozen=True)
class NormalizedNav:
    """A validated historical NAV observation."""

    trading_date: date
    nav: float
    source: str


@dataclass(frozen=True)
class SourceAttempt:
    source: str
    accepted_rows: int
    status: str
    error: str | None = None
    observed_at: datetime | None = None


def _parse_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(text[:10], fmt).date()
        except ValueError:
            continue
    raise ValueError(f"invalid trading date: {value!r}")


def _parse_nav(value: Any) -> float:
    if isinstance(value, str):
        value = value.replace(",", "").strip()
    nav = float(value)
    if not isfinite(nav) or nav <= 0:
        raise ValueError(f"NAV must be a finite positive number: {value!r}")
    return nav


def validate_nav_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    source: str,
    date_key: str = "date",
    nav_key: str = "nav",
) -> list[NormalizedNav]:
    """Normalize and validate rows, rejecting malformed observations.

    Duplicate dates are collapsed deterministically. The last valid row wins,
    which is useful when an upstream endpoint returns a corrected NAV later in
    the same page. A source with no valid rows is considered unusable by the
    fallback chain.
    """

    normalized: dict[date, NormalizedNav] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        try:
            point = NormalizedNav(
                trading_date=_parse_date(row[date_key]),
                nav=_parse_nav(row[nav_key]),
                source=source,
            )
        except (KeyError, TypeError, ValueError):
            continue
        normalized[point.trading_date] = point
    return [normalized[key] for key in sorted(normalized)]


def now_utc() -> datetime:
    """Return a timezone-aware timestamp for audit records."""

    return datetime.now(timezone.utc)
