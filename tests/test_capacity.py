import unittest

from netcalc.wireless import capacity


class TestNoise(unittest.TestCase):
    def test_noise_floor(self):
        self.assertAlmostEqual(capacity.noise_floor_dbm(1), -174.0)
        self.assertAlmostEqual(capacity.noise_floor_dbm(20e6), -100.99, places=2)
        self.assertAlmostEqual(capacity.noise_floor_dbm(20e6, 7), -93.99, places=2)
