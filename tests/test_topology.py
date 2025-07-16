import unittest

from netcalc.aifabric import topology


class TestMaxSize(unittest.TestCase):
    def test_two_tier(self):
        self.assertEqual(topology.two_tier_max_hosts(64), 2048)

    def test_three_tier(self):
        self.assertEqual(topology.three_tier_max_hosts(64), 65536)
        self.assertEqual(topology.three_tier_switches(4), 20)
