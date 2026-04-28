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
