import unittest

from netcalc.layer1 import osnr


class TestReferenceBandwidth(unittest.TestCase):
    def test_0p1nm_is_12p5ghz(self):
        self.assertAlmostEqual(osnr.ref_bandwidth_hz() / 1e9, 12.48, places=2)


class TestSnrConversion(unittest.TestCase):
    def test_round_trip(self):
        snr = osnr.osnr_to_snr_db(22.0, 64)
        self.assertAlmostEqual(osnr.snr_to_osnr_db(snr, 64), 22.0)

    def test_higher_baud_lowers_snr(self):
        self.assertLess(osnr.osnr_to_snr_db(20, 128), osnr.osnr_to_snr_db(20, 64))


class TestLineOsnr(unittest.TestCase):
    def test_cascade_of_equal_terms(self):
        self.assertAlmostEqual(osnr.cascade_osnr_db(20, 20), 20 - 3.0103, places=3)

    def test_amplifier_chain(self):
        self.assertAlmostEqual(osnr.amplifier_chain_osnr_db(1, 22, 5.5, 10), 21.5)

    def test_powers(self):
        self.assertAlmostEqual(osnr.osnr_from_powers(0, -30, 0.1), 30.0)
        self.assertAlmostEqual(osnr.osnr_from_powers(0, -27, 0.2), 30.0103, places=3)


if __name__ == "__main__":
    unittest.main()
