import ipaddress
import unittest

from netcalc.protocols import nat


class TestPortBlocks(unittest.TestCase):
    def test_subscribers_per_address(self):
        self.assertEqual(nat.subscribers_per_address(1024), 63)
        self.assertEqual(nat.subscribers_per_address(64512), 1)

    def test_addresses_needed(self):
        self.assertEqual(nat.addresses_needed(100000, 1024), 1588)
