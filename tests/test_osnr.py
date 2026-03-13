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
