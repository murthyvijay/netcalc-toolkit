import unittest

from netcalc.perf import loss


class TestLossRatio(unittest.TestCase):
    def test_ratio(self):
        self.assertAlmostEqual(loss.loss_ratio(100000, 99950), 0.0005)

    def test_path_loss(self):
        self.assertAlmostEqual(loss.path_loss(0.01, 0.01), 0.0199)
        self.assertEqual(loss.path_loss(), 0.0)

    def test_any_loss_and_retransmissions(self):
        self.assertAlmostEqual(loss.prob_any_loss(0.5, 2), 0.75)
        self.assertAlmostEqual(loss.expected_transmissions(0.5), 2.0)


class TestSequenceAnalysis(unittest.TestCase):
    def test_bursts_dupes_reorder(self):
        r = loss.analyze_sequence([1, 2, 3, 6, 7, 7, 5, 8, 12])
        self.assertEqual(r["lost"], 4)          # 4, 9, 10, 11
        self.assertEqual(r["duplicates"], 1)
        self.assertEqual(r["reordered"], 1)
        self.assertEqual(r["max_burst"], 3)
        self.assertEqual(r["bursts"], 2)

    def test_clean(self):
        r = loss.analyze_sequence(list(range(100)))
        self.assertEqual(r["lost"], 0)
        self.assertEqual(r["max_burst"], 0)


if __name__ == "__main__":
    unittest.main()
