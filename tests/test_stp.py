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


class TestBridgeId(unittest.TestCase):
    def test_priority(self):
        self.assertEqual(stp.bridge_priority(32768, 10), 32778)
        with self.assertRaises(ValueError):
            stp.bridge_priority(1000)

    def test_root_election(self):
        bridges = ["32768:0011.2233.4455", "4096:00aa.bbcc.ddee", "4096:0000.0000.0001"]
        self.assertEqual(stp.elect_root(bridges), "4096:0000.0000.0001")


if __name__ == "__main__":
    unittest.main()
