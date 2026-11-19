import unittest

from app.activity import ActivityStats, dropout_risk
from app.risk_model import MODEL, mean_mastery, risk, risk_factors

TOY = {
    "features": ["days_inactive", "fail_streak", "attempts_last_week", "avg_mastery"],
    "mean": [2.0, 1.0, 5.0, 0.5],
    "scale": [2.0, 1.0, 3.0, 0.2],
    "coef": [1.5, 0.3, -1.0, -0.1],
    "intercept": -0.5,
}


class RiskModelTests(unittest.TestCase):
    def test_probability_in_range(self):
        for days in (0, 3, 30):
            p = risk(ActivityStats(days, 2, 4), 0.6, TOY)
            self.assertTrue(0.0 <= p <= 1.0)

    def test_inactivity_raises_risk(self):
        low = risk(ActivityStats(0, 0, 6), 0.5, TOY)
        high = risk(ActivityStats(10, 0, 0), 0.5, TOY)
        self.assertGreater(high, low)

    def test_more_attempts_lower_risk(self):
        self.assertLess(risk(ActivityStats(1, 0, 10), 0.5, TOY),
                        risk(ActivityStats(1, 0, 1), 0.5, TOY))

    def test_fallback_to_rules_without_model(self):
        s = ActivityStats(4, 2, 0)
        self.assertEqual(risk(s, 0.5, None), dropout_risk(s))
        self.assertEqual(risk_factors(s, 0.5, None), [])

    def test_factors_sorted_by_contribution(self):
        factors = risk_factors(ActivityStats(10, 0, 5), 0.5, TOY)
        self.assertEqual(factors[0][0], "days_inactive")
        self.assertEqual(len(factors), 4)

    def test_mean_mastery(self):
        self.assertEqual(mean_mastery({}), 0.0)
        self.assertEqual(mean_mastery({"a": 0.2, "b": 0.6}), 0.4)

    def test_shipped_model_is_sane(self):
        self.assertIsNotNone(MODEL, "models/dropout_logreg.json не знайдено")
        active = risk(ActivityStats(0, 0, 8), 0.7)
        gone = risk(ActivityStats(12, 0, 0), 0.7)
        self.assertLess(active, 0.3)
        self.assertGreater(gone, 0.7)


if __name__ == "__main__":
    unittest.main()
