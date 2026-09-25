import unittest
from datetime import date, timedelta

from jushi_fund_research.data_policy import NormalizedNav
from jushi_fund_research.strategy import backtest_ma20_oos


def points(count):
    return [
        NormalizedNav(date(2023, 1, 1) + timedelta(days=i), 1 + i * 0.001, "test")
        for i in range(count)
    ]


class StrategyTests(unittest.TestCase):
    def test_small_sample_is_rejected(self):
        result = backtest_ma20_oos(points(30))
        self.assertEqual(result.status, "insufficient_sample")
        self.assertIsNone(result.strategy_return)

    def test_oos_result_contains_train_test_boundary(self):
        result = backtest_ma20_oos(points(100), min_train_rows=20, min_test_rows=10)
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.train_rows, 60)
        self.assertEqual(result.test_rows, 40)
        self.assertIsNotNone(result.strategy_max_drawdown)


if __name__ == "__main__":
    unittest.main()
