import unittest

from netcalc.routing import fhrp


class TestVrrpTimers(unittest.TestCase):
    def test_skew(self):
        self.assertAlmostEqual(fhrp.vrrp_skew_time(100), 0.609375)
        self.assertAlmostEqual(fhrp.vrrp_skew_time(254, 0.1), 2 * 0.1 / 256)

    def test_master_down_interval(self):
        self.assertAlmostEqual(fhrp.vrrp_master_down_interval(100), 3.609375)
        self.assertLess(fhrp.vrrp_master_down_interval(200), fhrp.vrrp_master_down_interval(100))
