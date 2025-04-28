import unittest

from netcalc.routing import fhrp


class TestVrrpTimers(unittest.TestCase):
    def test_skew(self):
        self.assertAlmostEqual(fhrp.vrrp_skew_time(100), 0.609375)
        self.assertAlmostEqual(fhrp.vrrp_skew_time(254, 0.1), 2 * 0.1 / 256)

    def test_master_down_interval(self):
        self.assertAlmostEqual(fhrp.vrrp_master_down_interval(100), 3.609375)
        self.assertLess(fhrp.vrrp_master_down_interval(200), fhrp.vrrp_master_down_interval(100))

    def test_priority_range(self):
        with self.assertRaises(ValueError):
            fhrp.vrrp_skew_time(0)


class TestHsrp(unittest.TestCase):
    def test_hold_rule(self):
        self.assertTrue(fhrp.hsrp_hold_ok(3, 10))
        self.assertFalse(fhrp.hsrp_hold_ok(1, 2))
