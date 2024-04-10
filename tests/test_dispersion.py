import unittest

from netcalc.optics import dispersion


class TestChromaticDispersion(unittest.TestCase):
    def test_accumulated(self):
        self.assertEqual(dispersion.accumulated_cd(80), 1360)

    def test_signal_width(self):
        self.assertAlmostEqual(dispersion.signal_width_nm(10e9), 0.0801, places=4)

    def test_reach_scales_with_inverse_square_of_rate(self):
        r10 = dispersion.cd_limited_reach_km(10e9)
        self.assertAlmostEqual(r10, 73.4, places=1)
        self.assertAlmostEqual(dispersion.cd_limited_reach_km(100e9), r10 / 100)

    def test_spread_at_reach_is_one_bit(self):
        km = dispersion.cd_limited_reach_km(25e9)
        self.assertAlmostEqual(dispersion.pulse_spread_ps(km, 25e9), 40.0)

    def test_compensation(self):
        self.assertEqual(dispersion.compensation_needed(80, tolerance_ps_nm=800), -560)
        self.assertEqual(dispersion.compensation_needed(20, tolerance_ps_nm=800), 0)
