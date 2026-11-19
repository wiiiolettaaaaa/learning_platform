import unittest

from ml.simulate import FEATURES, generate


class SimulationTests(unittest.TestCase):
    def test_dataset_shape_and_labels(self):
        X, y, groups = generate(n_students=200, seed=1)
        self.assertTrue(len(X) == len(y) == len(groups) > 0)
        self.assertTrue(all(len(row) == len(FEATURES) for row in X))
        self.assertEqual(set(y), {0, 1})

    def test_reproducible_with_seed(self):
        self.assertEqual(generate(50, seed=7), generate(50, seed=7))

    def test_feature_ranges(self):
        X, _, _ = generate(100, seed=3)
        for days, streak, attempts, mastery in X:
            self.assertGreaterEqual(days, 0)
            self.assertGreaterEqual(streak, 0)
            self.assertGreaterEqual(attempts, 0)
            self.assertTrue(0.0 <= mastery <= 1.0)


if __name__ == "__main__":
    unittest.main()
