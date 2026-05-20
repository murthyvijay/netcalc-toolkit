import unittest

from netcalc.protocols import mtu


class TestMss(unittest.TestCase):
    def test_mss(self):
        self.assertEqual(mtu.mss(1500), 1460)
        self.assertEqual(mtu.mss(1500, ipv6=True), 1440)
        self.assertEqual(mtu.mss(1500, timestamps=True), 1448)
        self.assertEqual(mtu.mss(9000), 8960)
