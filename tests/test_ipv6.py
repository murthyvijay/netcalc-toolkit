import ipaddress
import unittest

from netcalc.protocols import ipv6


class TestEui64(unittest.TestCase):
    def test_interface_id(self):
        self.assertEqual(ipv6.eui64_interface_id("00:1b:44:11:3a:b7"), 0x021B44FFFE113AB7)

    def test_slaac_and_link_local(self):
        self.assertEqual(str(ipv6.eui64_address("2001:db8:1:1::/64", "00-1B-44-11-3A-B7")),
                         "2001:db8:1:1:21b:44ff:fe11:3ab7")
        self.assertEqual(str(ipv6.link_local("001b.4411.3ab7")), "fe80::21b:44ff:fe11:3ab7")

    def test_requires_slash_64(self):
        with self.assertRaises(ValueError):
            ipv6.eui64_address("2001:db8::/48", "00:1b:44:11:3a:b7")
        with self.assertRaises(ValueError):
            ipv6.eui64_interface_id("00:1b:44")
