import unittest

from netcalc.perf import availability


class TestCombinations(unittest.TestCase):
    def test_series(self):
        self.assertAlmostEqual(availability.series(0.999, 0.999), 0.998001)

    def test_parallel(self):
        self.assertAlmostEqual(availability.parallel(0.99, 0.99), 0.9999)

    def test_k_of_n(self):
        self.assertAlmostEqual(availability.k_of_n(1, 2, 0.99), availability.parallel(0.99, 0.99))
        self.assertAlmostEqual(availability.k_of_n(2, 2, 0.99), availability.series(0.99, 0.99))
        self.assertAlmostEqual(availability.k_of_n(2, 3, 0.9), 0.972)


class TestMtbf(unittest.TestCase):
    def test_from_mtbf(self):
        self.assertAlmostEqual(availability.from_mtbf(9999, 1), 0.9999)
