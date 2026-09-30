import unittest
from datetime import datetime, timezone

from jushi_fund_research.data_policy import validate_nav_rows
from jushi_fund_research.nav_chain import fetch_with_fallback


class DataContractTests(unittest.TestCase):
    def test_adapter_accepts_datetime_dates_and_preserves_source(self):
        rows = validate_nav_rows(
            [{"date": datetime(2024, 1, 2, 15, 30, tzinfo=timezone.utc), "nav": "1.234"}],
            source="primary-api",
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].trading_date.isoformat(), "2024-01-02")
        self.assertEqual(rows[0].nav, 1.234)
        self.assertEqual(rows[0].source, "primary-api")

    def test_source_attempt_records_timezone_aware_observation_time(self):
        result = fetch_with_fallback(
            [("primary-api", lambda: [{"date": "2024-01-02", "nav": 1.1}])]
        )

        attempt = result.attempts[0]
        self.assertIsNotNone(attempt.observed_at)
        self.assertIsNotNone(attempt.observed_at.tzinfo)
        self.assertEqual(attempt.observed_at.utcoffset(), timezone.utc.utcoffset(None))


if __name__ == "__main__":
    unittest.main()
