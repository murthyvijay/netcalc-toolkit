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


class TestWire(unittest.TestCase):
    def test_min_frame_padding(self):
        self.assertEqual(overhead.frame_bytes(1, "udp"), 64)
        self.assertEqual(overhead.wire_bytes(1, "udp"), 84)

    def test_full_size_tcp_efficiency(self):
        self.assertAlmostEqual(overhead.efficiency(1460, "tcp"), 1460 / 1538)
        self.assertAlmostEqual(overhead.goodput(1460, "tcp", 10e9) / 1e9, 9.4928, places=3)

    def test_line_rate_pps(self):
        self.assertAlmostEqual(overhead.packets_per_second(64, 10e9) / 1e6, 14.881, places=3)
        self.assertAlmostEqual(overhead.packets_per_second(1518, 10e9) / 1e3, 812.743, places=2)


if __name__ == "__main__":
    unittest.main()
