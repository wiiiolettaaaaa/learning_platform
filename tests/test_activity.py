import unittest
from datetime import datetime, timedelta, timezone

from app.activity import build_stats, dropout_risk

NOW = datetime(2026, 11, 18, 12, 0, tzinfo=timezone.utc)


class ActivityStatsTests(unittest.TestCase):
    def test_no_attempts(self):
        s = build_stats([], 0, NOW)
        self.assertEqual((s.days_inactive, s.attempts_last_week), (0, 0))

    def test_counts_only_last_week(self):
        attempts = [NOW - timedelta(days=1), NOW - timedelta(days=3), NOW - timedelta(days=10)]
        s = build_stats(attempts, 0, NOW)
        self.assertEqual(s.attempts_last_week, 2)
        self.assertEqual(s.days_inactive, 1)

    def test_active_user_has_lower_risk_than_inactive(self):
        active = build_stats([NOW - timedelta(hours=1)], 0, NOW)
        inactive = build_stats([NOW - timedelta(days=9)], 0, NOW)
        self.assertLess(dropout_risk(active), dropout_risk(inactive))

    def test_fail_streak_raises_risk(self):
        base = build_stats([NOW], 0, NOW)
        failing = build_stats([NOW], 3, NOW)
        self.assertGreater(dropout_risk(failing), dropout_risk(base))


if __name__ == "__main__":
    unittest.main()
