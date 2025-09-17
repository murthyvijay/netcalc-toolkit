import ipaddress
import unittest

from netcalc.protocols import nat


class TestPortBlocks(unittest.TestCase):
    def test_subscribers_per_address(self):
        self.assertEqual(nat.subscribers_per_address(1024), 63)
        self.assertEqual(nat.subscribers_per_address(64512), 1)

    def test_addresses_needed(self):
        self.assertEqual(nat.addresses_needed(100000, 1024), 1588)

    def test_block_size(self):
        self.assertEqual(nat.block_size(900), 1408)
        self.assertEqual(nat.block_size(100, headroom=1.0), 128)


class TestDeterministic(unittest.TestCase):
    def test_first_subscriber(self):
        addr, first, last = nat.deterministic_mapping(0, 2048, "203.0.113.0/24")
        self.assertEqual(addr, ipaddress.ip_address("203.0.113.0"))
        self.assertEqual((first, last), (1024, 3071))
