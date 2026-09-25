"""Simple strategy research with an explicit out-of-sample boundary."""

from __future__ import annotations

from dataclasses import dataclass
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

    ordered = sorted(points, key=lambda point: point.trading_date)
    split = int(len(ordered) * train_ratio)
    train = ordered[:split]
    test = ordered[split:]
    if len(train) < min_train_rows or len(test) < min_test_rows:
        return BacktestResult(
            "insufficient_sample", len(train), len(test), window,
            None, None, None, None,
            "sample is too small for an out-of-sample conclusion",
        )

    # Recalculate test-only returns with the train tail as signal context.
    strategy_value = 1.0
    benchmark_value = 1.0
    for index in range(split, len(ordered)):
        previous_nav = ordered[index - 1].nav
        start = max(0, index - window)
        moving_average = sum(p.nav for p in ordered[start:index]) / (index - start)
        position = 1.0 if previous_nav >= moving_average else 0.0
        daily_return = ordered[index].nav / previous_nav
        strategy_value *= 1.0 + position * (daily_return - 1.0)
        benchmark_value *= daily_return
    test_context = ordered[split - 1:]
    # Use a small independent pass to calculate drawdown over test equity.
    strat_curve = [1.0]
    bench_curve = [1.0]
    for index in range(1, len(test_context)):
        global_index = split - 1 + index
        previous_nav = ordered[global_index - 1].nav
        start = max(0, global_index - window)
        moving_average = sum(p.nav for p in ordered[start:global_index]) / (global_index - start)
        position = 1.0 if previous_nav >= moving_average else 0.0
        daily_return = ordered[global_index].nav / previous_nav
        strat_curve.append(strat_curve[-1] * (1.0 + position * (daily_return - 1.0)))
        bench_curve.append(bench_curve[-1] * daily_return)
    return BacktestResult(
        "ok", len(train), len(test), window,
        strategy_value - 1.0, benchmark_value - 1.0,
        _max_drawdown(strat_curve), _max_drawdown(bench_curve),
        "research result only; not investment advice",
    )
