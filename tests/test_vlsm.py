import unittest

from netcalc.ccna import vlsm


class TestAllocate(unittest.TestCase):
    def test_classic_lab(self):
        plan = vlsm.allocate("192.168.1.0/24",
                             {"SALES": 100, "ENG": 50, "HR": 20, "WAN1": 2, "WAN2": 2})
        subnets = {row["name"]: row["subnet"] for row in plan}
        self.assertEqual(subnets["SALES"], "192.168.1.0/25")
        self.assertEqual(subnets["ENG"], "192.168.1.128/26")
        self.assertEqual(subnets["HR"], "192.168.1.192/27")
        self.assertEqual(subnets["WAN1"], "192.168.1.224/30")
        self.assertEqual(subnets["WAN2"], "192.168.1.228/30")

    def test_exhausted(self):
        with self.assertRaises(ValueError):
            vlsm.allocate("192.168.1.0/26", {"A": 60, "B": 10})


class TestHelpers(unittest.TestCase):
    def test_parse_and_utilization(self):
        reqs = vlsm.parse_requirements(["A=100", "B=20"])
        self.assertEqual(reqs, {"A": 100, "B": 20})
        plan = vlsm.allocate("10.0.0.0/24", reqs)
        self.assertAlmostEqual(vlsm.utilization("10.0.0.0/24", plan), (128 + 32) / 256)


if __name__ == "__main__":
    unittest.main()
