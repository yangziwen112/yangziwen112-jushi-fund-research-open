"""Machine-readable audit summaries for data and research results."""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any

from .data_policy import DataStatus
from .nav_chain import NavChainResult
from .strategy import BacktestResult


def _iso(value: date | datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def summarize_nav_chain(result: NavChainResult) -> dict[str, Any]:
    """Return a safe, serializable summary without exposing raw adapter errors."""

    points = result.points
    attempts = [
        {
            "source": attempt.source,
            "accepted_rows": attempt.accepted_rows,
            "status": attempt.status,
            "observed_at": _iso(attempt.observed_at),
            "duration_ms": attempt.duration_ms,
            "error_present": bool(attempt.error),
        }
        for attempt in result.attempts
    ]
    return {
        "status": result.status.value if isinstance(result.status, DataStatus) else str(result.status),
        "selected_source": result.selected_source,
        "point_count": len(points),
        "coverage_start": _iso(points[0].trading_date) if points else None,
        "coverage_end": _iso(points[-1].trading_date) if points else None,
        "attempt_count": len(attempts),
        "failed_attempt_count": sum(item["status"] == "failed" for item in attempts),
        "attempts": attempts,
        "message": result.message,
    }


def build_research_audit(
    nav_result: NavChainResult,
    backtest_result: BacktestResult,
) -> dict[str, Any]:
    """Combine source evidence and OOS output into a research decision.

    The decision deliberately stays below an investment recommendation. A
    successful backtest is reported as ``research_only``; insufficient inputs
    are reported as ``insufficient_data`` with no return conclusion.
    """

    nav = summarize_nav_chain(nav_result)
    enough_data = nav_result.status != DataStatus.INSUFFICIENT and bool(nav_result.points)
    enough_sample = backtest_result.status == "ok"
    decision = "research_only" if enough_data and enough_sample else "insufficient_data"
    limitations = [
        "历史研究结果不构成投资建议",
        "正式净值、盘中估值和公开披露信息的时间语义不同",
    ]
    if not enough_data:
        limitations.append("没有足够的已验证净值数据支持策略结论")
    if not enough_sample:
        limitations.append(backtest_result.warning or "样本不足，未输出回测收益结论")

    return {
        "decision": decision,
        "data": nav,
        "backtest": {
            "status": backtest_result.status,
            "train_rows": backtest_result.train_rows,
            "test_rows": backtest_result.test_rows,
            "window": backtest_result.window,
            "strategy_return": backtest_result.strategy_return,
            "benchmark_return": backtest_result.benchmark_return,
            "strategy_max_drawdown": backtest_result.strategy_max_drawdown,
            "benchmark_max_drawdown": backtest_result.benchmark_max_drawdown,
        },
        "limitations": limitations,
        "disclaimer": "Research only; not investment advice.",
    }


def audit_json(nav_result: NavChainResult, backtest_result: BacktestResult) -> str:
    """Serialize an audit report for an API, Agent, or artifact file."""

    return json.dumps(
        build_research_audit(nav_result, backtest_result),
        ensure_ascii=False,
        sort_keys=True,
    )
