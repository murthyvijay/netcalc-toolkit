import unittest

from netcalc.ccna import ospf


class TestCost(unittest.TestCase):
    def test_default_reference(self):
        self.assertEqual(ospf.interface_cost(10e6), 10)
        self.assertEqual(ospf.interface_cost(100e6), 1)
        self.assertEqual(ospf.interface_cost(400e9), 1)

    def test_raised_reference(self):
        self.assertEqual(ospf.interface_cost(10e9, 100e9), 10)
        self.assertEqual(ospf.interface_cost(25e9, 100e9), 4)
        self.assertEqual(ospf.interface_cost(1e3, 100e9), 65535)


class TestPaths(unittest.TestCase):
    def test_path_cost(self):
        self.assertEqual(ospf.path_cost([10e9, 10e9, 1e9], 100e9), 120)

    def test_table_and_recommendation(self):
        table = dict(ospf.cost_table(400e9))
        self.assertEqual(table["100G"], 4)
        self.assertEqual(ospf.recommended_reference(800e9), 8e12)


if __name__ == "__main__":
    unittest.main()
