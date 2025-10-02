import unittest

from netcalc.perf import availability


class TestCombinations(unittest.TestCase):
    def test_series(self):
        self.assertAlmostEqual(availability.series(0.999, 0.999), 0.998001)

    def test_parallel(self):
        self.assertAlmostEqual(availability.parallel(0.99, 0.99), 0.9999)
