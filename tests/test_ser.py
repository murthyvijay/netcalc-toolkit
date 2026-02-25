import math
import unittest

from netcalc.layer1 import ser


class TestPam(unittest.TestCase):
    def test_pam2_matches_binary(self):
        snr_db = 10 * math.log10(49)  # Q = 7 for PAM2
        self.assertAlmostEqual(ser.pam_ser(2, snr_db) / ser.q_function(7), 1, places=9)

    def test_pam4_worse_than_pam2(self):
        self.assertGreater(ser.pam_ser(4, 15), ser.pam_ser(2, 15))

    def test_snr_for_ser(self):
        snr = ser.snr_for_ser(4, 1e-6)
        self.assertAlmostEqual(ser.pam_ser(4, snr) / 1e-6, 1, places=3)
