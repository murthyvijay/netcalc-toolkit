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


class TestCapacity(unittest.TestCase):
    def test_failover(self):
        self.assertEqual(mrc.failover_capacity(8, 400e9, 1), 7 * 400e9)
        with self.assertRaises(ValueError):
            mrc.failover_capacity(2, 1e9, 3)

    def test_reorder_buffer(self):
        self.assertAlmostEqual(mrc.reorder_buffer_bytes(800e9, 4e-6, 4096), 400000 + 4096)


if __name__ == "__main__":
    unittest.main()
