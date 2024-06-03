import unittest

from netcalc.wireless import capacity


class TestNoise(unittest.TestCase):
    def test_noise_floor(self):
        self.assertAlmostEqual(capacity.noise_floor_dbm(1), -174.0)
        self.assertAlmostEqual(capacity.noise_floor_dbm(20e6), -100.99, places=2)
        self.assertAlmostEqual(capacity.noise_floor_dbm(20e6, 7), -93.99, places=2)


class TestShannon(unittest.TestCase):
    def test_capacity(self):
        self.assertAlmostEqual(capacity.shannon_capacity(1e6, 0), 1e6)
        self.assertAlmostEqual(capacity.shannon_capacity(20e6, 30) / 1e6, 199.34, places=2)

    def test_snr_for_rate_inverts_capacity(self):
        snr = capacity.snr_for_rate_db(100e6, 20e6)
        self.assertAlmostEqual(snr, 14.91, places=2)
        self.assertAlmostEqual(capacity.shannon_capacity(20e6, snr), 100e6)

    def test_ebn0(self):
        self.assertAlmostEqual(capacity.ebn0_db(10, 2e6, 1e6), 6.99, places=2)


class TestSinr(unittest.TestCase):
    def test_noise_only(self):
        self.assertAlmostEqual(capacity.sinr_db(-60, -95), 35.0)

    def test_interference_dominates(self):
        self.assertAlmostEqual(capacity.sinr_db(-60, -95, [-80, -85]), 18.70, places=2)


if __name__ == "__main__":
    unittest.main()
