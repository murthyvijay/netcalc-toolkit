import unittest

from netcalc.perf import availability


class TestCombinations(unittest.TestCase):
    def test_series(self):
        self.assertAlmostEqual(availability.series(0.999, 0.999), 0.998001)
