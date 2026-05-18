import unittest

from netcalc.protocols import overhead


class TestStacks(unittest.TestCase):
    def test_resolve(self):
        self.assertEqual(overhead.resolve_stack("tcp"), ["eth", "ipv4", "tcp"])
        self.assertEqual(overhead.resolve_stack("eth,ipv6,udp"), ["eth", "ipv6", "udp"])
        with self.assertRaises(ValueError):
            overhead.resolve_stack("eth,carrier_pigeon")

    def test_header_bytes(self):
        self.assertEqual(overhead.header_bytes("tcp"), 58)
        self.assertEqual(overhead.header_bytes("roce"), 62)
        self.assertEqual(overhead.header_bytes("vxlan"), 18 + 20 + 8 + 8 + 14 + 20 + 20)
