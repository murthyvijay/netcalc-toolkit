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
