import unittest
from datetime import datetime, timedelta, timezone

from app.teacher import student_summary, topic_summary

NOW = datetime(2026, 11, 18, 12, 0, tzinfo=timezone.utc)


def user(mastery=None, attempts=None, fails=0, results=None):
    return {"mastery": mastery or {}, "attempts": attempts or [], "fails": fails,
            "last": {}, "results": results or {}}


class TeacherTests(unittest.TestCase):
    def test_student_summary_average_and_activity(self):
        u = user({"a": 0.9, "b": 0.5}, [NOW - timedelta(days=2)])
        s = student_summary("ann", u, NOW)
        self.assertEqual(s["avg_mastery"], 0.7)
        self.assertEqual(s["topics_started"], 2)
        self.assertEqual(s["attempts_last_week"], 1)
        self.assertEqual(s["days_inactive"], 2)

    def test_student_without_activity(self):
        s = student_summary("new", user(), NOW)
        self.assertEqual(s["avg_mastery"], 0.0)
        self.assertEqual(s["attempts_last_week"], 0)

    def test_topic_summary_accuracy(self):
        db = {
            "a": user({"t": 0.8}, results={"t": {"correct": 3, "total": 4}}),
            "b": user({"t": 0.4}, results={"t": {"correct": 1, "total": 4}}),
        }
        rows = {r["topic_id"]: r for r in topic_summary(db, ["t", "empty"])}
        self.assertEqual(rows["t"]["attempts"], 8)
        self.assertEqual(rows["t"]["accuracy"], 0.5)
        self.assertEqual(rows["t"]["avg_mastery"], 0.6)
        self.assertIsNone(rows["empty"]["accuracy"])


if __name__ == "__main__":
    unittest.main()
