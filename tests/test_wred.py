import unittest

from netcalc.traffic import wred


class TestDropProbability(unittest.TestCase):
    def test_regions(self):
        self.assertEqual(wred.drop_probability(10, 20, 40), 0.0)
        self.assertAlmostEqual(wred.drop_probability(30, 20, 40, mpd=10), 0.05)
        self.assertEqual(wred.drop_probability(40, 20, 40), 1.0)

    def test_spaced_probability(self):
        self.assertAlmostEqual(wred.spaced_probability(0.05, 0), 0.05)
        self.assertAlmostEqual(wred.spaced_probability(0.05, 10), 0.1)
        self.assertEqual(wred.spaced_probability(0.05, 20), 1.0)


class TestAverage(unittest.TestCase):
    def test_weight(self):
        self.assertEqual(wred.ewma_weight(9), 1 / 512)

    def test_series_moves_slowly(self):
        avg = wred.ewma_series([100] * 10, n=1)
        self.assertAlmostEqual(avg[0], 50)
        self.assertAlmostEqual(avg[1], 75)
        self.assertLess(avg[-1], 100)

    def test_samples_to_reach(self):
        self.assertEqual(wred.samples_to_reach(0.5, 1), 1)
        self.assertEqual(wred.samples_to_reach(0.63, 9), 509)
