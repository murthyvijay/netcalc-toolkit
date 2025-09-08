import unittest

from netcalc.protocols import ipsec


class TestPadding(unittest.TestCase):
    def test_block_alignment(self):
        self.assertEqual(ipsec.padding(14, 16), 0)
        self.assertEqual(ipsec.padding(1400, 16), 6)
        self.assertEqual(ipsec.padding(1400, 4), 2)
