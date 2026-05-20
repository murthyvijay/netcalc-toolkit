import unittest

from netcalc.protocols import mtu


class TestMss(unittest.TestCase):
    def test_mss(self):
        self.assertEqual(mtu.mss(1500), 1460)
        self.assertEqual(mtu.mss(1500, ipv6=True), 1440)
        self.assertEqual(mtu.mss(1500, timestamps=True), 1448)
        self.assertEqual(mtu.mss(9000), 8960)


class TestEncapsulation(unittest.TestCase):
    def test_vxlan(self):
        self.assertEqual(mtu.required_underlay_mtu(1500, "vxlan"), 1550)
        self.assertEqual(mtu.effective_mtu(1500, "vxlan"), 1450)

    def test_stacked(self):
        self.assertEqual(mtu.encap_overhead("mpls", "mpls", "dot1q"), 12)
        with self.assertRaises(ValueError):
            mtu.encap_overhead("tunnel_of_love")
