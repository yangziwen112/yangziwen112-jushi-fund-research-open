import json
import unittest
from datetime import date, timedelta

from jushi_fund_research.audit import audit_json, build_research_audit, summarize_nav_chain
from jushi_fund_research.data_policy import DataStatus, NormalizedNav
from jushi_fund_research.nav_chain import fetch_with_fallback
from jushi_fund_research.strategy import backtest_ma20_oos


def points(count):
    return [
        NormalizedNav(date(2023, 1, 1) + timedelta(days=i), 1 + i * 0.001, "primary")
        for i in range(count)
    ]


class AuditTests(unittest.TestCase):
    def test_primary_result_contains_coverage_and_attempt_summary(self):
        nav = fetch_with_fallback([("primary", lambda: [
            {"date": "2024-01-02", "nav": 1.1},
            {"date": "2024-01-03", "nav": 1.2},
        ])])
        summary = summarize_nav_chain(nav)
        self.assertEqual(summary["status"], "primary")
        self.assertEqual(summary["coverage_start"], "2024-01-02")
        self.assertEqual(summary["coverage_end"], "2024-01-03")
        self.assertEqual(summary["attempts"][0]["error_present"], False)

    def test_fallback_and_insufficient_are_distinguishable(self):
        fallback = fetch_with_fallback([
            ("primary", lambda: (_ for _ in ()).throw(RuntimeError("timeout"))),
            ("fallback", lambda: [{"date": "2024-01-02", "nav": 1.1}]),
        ])
        insufficient = fetch_with_fallback([("primary", lambda: [])])
        self.assertEqual(summarize_nav_chain(fallback)["status"], "fallback")
        self.assertEqual(summarize_nav_chain(insufficient)["status"], "insufficient")
        self.assertTrue(summarize_nav_chain(fallback)["attempts"][0]["error_present"])

    def test_small_sample_refuses_research_decision(self):
        nav = fetch_with_fallback([("primary", lambda: [
            {"date": point.trading_date.isoformat(), "nav": point.nav}
            for point in points(30)
        ])])
        report = build_research_audit(nav, backtest_ma20_oos(points(30)))
        self.assertEqual(report["decision"], "insufficient_data")
        self.assertIsNone(report["backtest"]["strategy_return"])

    def test_report_is_json_serializable_and_not_a_trading_signal(self):
        nav = fetch_with_fallback([("primary", lambda: [
            {"date": point.trading_date.isoformat(), "nav": point.nav}
            for point in points(100)
        ])])
        result = backtest_ma20_oos(points(100), min_train_rows=20, min_test_rows=10)
        payload = json.loads(audit_json(nav, result))
        self.assertEqual(payload["decision"], "research_only")
        self.assertIn("not investment advice", payload["disclaimer"].lower())
        self.assertNotIn("password", audit_json(nav, result).lower())


if __name__ == "__main__":
    unittest.main()
