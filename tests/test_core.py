import unittest
from pathlib import Path
from app.knowledge import update_mastery
from app.graph import KnowledgeGraph
from app.recommender import recommend
from app.activity import ActivityStats, dropout_risk

G = KnowledgeGraph.from_json(Path(__file__).parent.parent / "data" / "sample_course.json")


class CoreTests(unittest.TestCase):
    def test_correct_raises_wrong_lowers(self):
        self.assertGreater(update_mastery(0.3, True), 0.3)
        self.assertLess(update_mastery(0.6, False), 0.6)

    def test_converges_with_correct_answers(self):
        p = 0.2
        for _ in range(10):
            p = update_mastery(p, True)
        self.assertGreater(p, 0.9)

    def test_start_with_root_topic(self):
        r = recommend(G, {}, {})
        self.assertEqual(r.topic_id, "variables")

    def test_prerequisites_unlock_next(self):
        r = recommend(G, {"variables": 0.95}, {"variables": 0})
        self.assertIn(r.topic_id, {"conditions", "functions"})

    def test_review_after_long_break(self):
        r = recommend(G, {"variables": 0.95}, {"variables": 20})
        self.assertEqual((r.topic_id, r.kind), ("variables", "review"))

    def test_risk_grows(self):
        self.assertGreater(dropout_risk(ActivityStats(8, 4, 0)), dropout_risk(ActivityStats(0, 0, 5)))


if __name__ == "__main__":
    unittest.main()
