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
