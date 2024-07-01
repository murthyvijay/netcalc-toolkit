import unittest

from netcalc.queueing import littles


class TestLittlesLaw(unittest.TestCase):
    def test_solves_each_unknown(self):
        self.assertEqual(littles.littles_law(rate=2000, time=0.05), 100.0)
        self.assertEqual(littles.littles_law(count=100, time=0.05), 2000.0)
        self.assertEqual(littles.littles_law(count=40, rate=2000), 0.02)

    def test_needs_exactly_two(self):
        with self.assertRaises(ValueError):
            littles.littles_law(rate=10)
        with self.assertRaises(ValueError):
            littles.littles_law(count=1, rate=2, time=3)


class TestOperationalLaws(unittest.TestCase):
    def test_utilization(self):
        self.assertAlmostEqual(littles.utilization(800, 0.001), 0.8)
        self.assertEqual(littles.max_throughput(0.002, servers=4), 2000)
