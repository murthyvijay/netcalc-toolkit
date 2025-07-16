import unittest

from netcalc.aifabric import topology


class TestMaxSize(unittest.TestCase):
    def test_two_tier(self):
        self.assertEqual(topology.two_tier_max_hosts(64), 2048)

    def test_three_tier(self):
        self.assertEqual(topology.three_tier_max_hosts(64), 65536)
        self.assertEqual(topology.three_tier_switches(4), 20)


class TestPlan(unittest.TestCase):
    def test_full_two_tier(self):
        plan = topology.leaf_spine_plan(2048, 64)
        self.assertEqual(plan["leaves"], 64)
        self.assertEqual(plan["spines"], 32)
        self.assertEqual(plan["leaf_spine_links"], 2048)

    def test_oversubscribed_leaf(self):
        plan = topology.leaf_spine_plan(480, 64, oversub=3)
        self.assertEqual(plan["host_ports_per_leaf"], 48)
        self.assertEqual(plan["uplinks_per_leaf"], 16)
        self.assertEqual(plan["leaves"], 10)

    def test_too_big_for_two_tiers(self):
        with self.assertRaises(ValueError):
            topology.leaf_spine_plan(4096, 64)

    def test_ratio_and_optics(self):
        self.assertEqual(topology.oversubscription(48, 8, 100, 400), 1.5)
        self.assertEqual(topology.optics_count(2048), 4096)
