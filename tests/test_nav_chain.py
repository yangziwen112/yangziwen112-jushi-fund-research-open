import unittest

from jushi_fund_research.data_policy import DataStatus, validate_nav_rows
from jushi_fund_research.nav_chain import fetch_with_fallback


class NavChainTests(unittest.TestCase):
    def test_validation_deduplicates_and_discards_invalid_rows(self):
        rows = validate_nav_rows(
            [
                {"date": "2024-01-02", "nav": "1.10"},
                {"date": "2024-01-02", "nav": "1.20"},
                {"date": "bad", "nav": 2},
                {"date": "2024-01-03", "nav": -1},
            ],
            source="primary",
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].nav, 1.2)

    def test_fallback_is_used_after_primary_failure(self):
        result = fetch_with_fallback(
            [("primary", lambda: (_ for _ in ()).throw(RuntimeError("timeout"))),
             ("fallback", lambda: [{"date": "2024-01-02", "nav": 1.1}])]
        )
        self.assertEqual(result.status, DataStatus.FALLBACK)
        self.assertEqual(result.selected_source, "fallback")
        self.assertEqual(len(result.attempts), 2)

    def test_cache_is_not_called_a_live_source(self):
        result = fetch_with_fallback(
            [("primary", lambda: [])],
            cache=[{"date": "2024-01-02", "nav": 1.1}],
        )
        self.assertEqual(result.status, DataStatus.CACHE)
        self.assertEqual(result.selected_source, "cache")

    def test_all_sources_failed_without_cache_returns_insufficient(self):
        result = fetch_with_fallback(
            [("primary", lambda: []), ("fallback", lambda: [])]
        )
        self.assertEqual(result.status, DataStatus.INSUFFICIENT)
        self.assertIsNone(result.selected_source)
        self.assertEqual(len(result.points), 0)

    def test_common_date_separators_are_normalized(self):
        rows = validate_nav_rows(
            [
                {"date": "2024/01/02", "nav": "1.10"},
                {"date": "2024.01.03", "nav": "1.20"},
            ],
            source="primary",
        )
        self.assertEqual([row.trading_date.isoformat() for row in rows], ["2024-01-02", "2024-01-03"])


if __name__ == "__main__":
    unittest.main()
