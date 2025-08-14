import ipaddress
import unittest

from netcalc.protocols import ipv6


class TestEui64(unittest.TestCase):
    def test_interface_id(self):
        self.assertEqual(ipv6.eui64_interface_id("00:1b:44:11:3a:b7"), 0x021B44FFFE113AB7)
