import unittest

from netcalc.routing import mpls


class TestOverhead(unittest.TestCase):
    def test_stack(self):
        self.assertEqual(mpls.stack_overhead(3), 12)

    def test_mtu(self):
        self.assertEqual(mpls.required_mtu(1500, 3), 1512)
        self.assertEqual(mpls.required_mtu(1500, 2, l2_overhead=14), 1522)
