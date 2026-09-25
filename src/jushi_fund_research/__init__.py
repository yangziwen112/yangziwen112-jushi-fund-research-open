"""Auditable building blocks for fund data and strategy research."""

from .data_policy import DataStatus, SourceAttempt, validate_nav_rows
from .nav_chain import NavChainResult, fetch_with_fallback
from .strategy import BacktestResult, backtest_ma20_oos

__all__ = [
    "BacktestResult",
    "DataStatus",
    "NavChainResult",
    "SourceAttempt",
    "backtest_ma20_oos",
    "fetch_with_fallback",
    "validate_nav_rows",
]
