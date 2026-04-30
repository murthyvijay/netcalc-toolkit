import unittest

from netcalc.ccna import stp


class TestTimers(unittest.TestCase):
    def test_defaults(self):
        t = stp.timers()
        self.assertEqual(t["max_age"], 20)
        self.assertEqual(t["forward_delay"], 15)
        self.assertEqual(t["stp_convergence"], 50)

    def test_smaller_diameter(self):
        t = stp.timers(diameter=2)
        self.assertEqual(t["max_age"], 10)
        self.assertEqual(t["forward_delay"], 7)


class TestCosts(unittest.TestCase):
    def test_short(self):
        self.assertEqual(stp.port_cost_short(1e9), 4)
        self.assertEqual(stp.port_cost_short(100e6), 19)
        self.assertEqual(stp.port_cost_short(100e9), 2)

    def test_long(self):
        self.assertEqual(stp.port_cost_long(1e9), 20000)
        self.assertEqual(stp.port_cost_long(10e9), 2000)
        self.assertEqual(stp.port_cost_long(100e6), 200000)
