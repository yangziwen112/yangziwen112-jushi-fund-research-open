"""Simple strategy research with an explicit out-of-sample boundary."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

from .data_policy import NormalizedNav


@dataclass(frozen=True)
class BacktestResult:
    status: str
    train_rows: int
    test_rows: int
    window: int
    strategy_return: float | None
    benchmark_return: float | None
    strategy_max_drawdown: float | None
    benchmark_max_drawdown: float | None
    warning: str | None = None


def _max_drawdown(equity: Sequence[float]) -> float:
    peak = equity[0]
    worst = 0.0
    for value in equity:
        peak = max(peak, value)
        worst = min(worst, value / peak - 1.0)
    return worst


def _validate_parameters(
    train_ratio: float,
    window: int,
    min_train_rows: int,
    min_test_rows: int,
) -> None:
    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio must be between 0 and 1")
    if window < 1:
        raise ValueError("window must be a positive integer")
    if min_train_rows < 1 or min_test_rows < 1:
        raise ValueError("minimum sample sizes must be positive")


def _prepare_ordered(points: Sequence[NormalizedNav]) -> list[NormalizedNav]:
    """Validate the strategy boundary and collapse duplicate trading dates.

    ``validate_nav_rows`` already applies this policy to adapter input, but
    callers can also construct ``NormalizedNav`` objects directly. Keeping
    the same last-observation-wins rule here prevents duplicate dates or
    non-positive values from silently distorting daily returns.
    """

    unique: dict[object, NormalizedNav] = {}
    for point in points:
        if not isinstance(point, NormalizedNav):
            raise TypeError("points must contain NormalizedNav values")
        if not isfinite(point.nav) or point.nav <= 0:
            raise ValueError("NAV must be a finite positive number")
        unique[point.trading_date] = point
    return sorted(unique.values(), key=lambda point: point.trading_date)


def _simulate_test_equity(
    ordered: Sequence[NormalizedNav],
    split: int,
    window: int,
) -> tuple[list[float], list[float]]:
    """Build test-only equity curves with one rolling-sum pass.

    The signal at index ``i`` only sees observations before ``i``. Prefix sums
    make the moving-average lookup O(1), so a long history no longer repeats a
    window-sized sum for every test point.
    """

    prefix = [0.0]
    for point in ordered:
        prefix.append(prefix[-1] + point.nav)

    strategy_curve = [1.0]
    benchmark_curve = [1.0]
    for index in range(split, len(ordered)):
        previous_nav = ordered[index - 1].nav
        start = max(0, index - window)
        moving_average = (prefix[index] - prefix[start]) / (index - start)
        position = 1.0 if previous_nav >= moving_average else 0.0
        daily_return = ordered[index].nav / previous_nav
        strategy_curve.append(strategy_curve[-1] * (1.0 + position * (daily_return - 1.0)))
        benchmark_curve.append(benchmark_curve[-1] * daily_return)
    return strategy_curve, benchmark_curve


def backtest_ma20_oos(
    points: Sequence[NormalizedNav],
    *,
    train_ratio: float = 0.6,
    window: int = 20,
    min_train_rows: int = 60,
    min_test_rows: int = 20,
) -> BacktestResult:
    """Evaluate MA20 on the test segment only.

    The first 60% is reserved for research/training context. The function does
    not tune parameters automatically, so its output cannot be mistaken for a
    claim of optimality. Small samples are explicitly rejected.
    """

    _validate_parameters(train_ratio, window, min_train_rows, min_test_rows)
    ordered = _prepare_ordered(points)
    split = int(len(ordered) * train_ratio)
    train = ordered[:split]
    test = ordered[split:]
    if len(train) < min_train_rows or len(test) < min_test_rows:
        return BacktestResult(
            "insufficient_sample", len(train), len(test), window,
            None, None, None, None,
            "sample is too small for an out-of-sample conclusion",
        )

    strat_curve, bench_curve = _simulate_test_equity(ordered, split, window)
    return BacktestResult(
        "ok", len(train), len(test), window,
        strat_curve[-1] - 1.0, bench_curve[-1] - 1.0,
        _max_drawdown(strat_curve), _max_drawdown(bench_curve),
        "research result only; not investment advice",
    )
