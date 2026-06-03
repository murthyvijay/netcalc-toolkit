import unittest

from netcalc.aifabric import mrc


class TestEntropy(unittest.TestCase):
    def test_coupon_collector(self):
        self.assertAlmostEqual(mrc.harmonic(4), 25 / 12)
        self.assertAlmostEqual(mrc.expected_entropies_to_cover(4), 25 / 3)

    def test_coverage(self):
        self.assertAlmostEqual(mrc.coverage_probability(2, 2), 0.5)
        self.assertEqual(mrc.coverage_probability(4, 3), 0.0)
        self.assertGreater(mrc.coverage_probability(64, 1024), 0.99)

    def test_expected_paths_used(self):
        self.assertAlmostEqual(mrc.expected_paths_used(2, 2), 1.5)
