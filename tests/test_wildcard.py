import unittest

from netcalc.ccna import wildcard


class TestConversions(unittest.TestCase):
    def test_mask_wildcard(self):
        self.assertEqual(wildcard.mask_to_wildcard("255.255.255.224"), "0.0.0.31")
        self.assertEqual(wildcard.wildcard_to_mask("0.0.0.31"), "255.255.255.224")
        self.assertEqual(wildcard.prefix_to_wildcard(20), "0.0.15.255")

    def test_non_contiguous(self):
        self.assertFalse(wildcard.is_contiguous("0.0.254.255"))
        with self.assertRaises(ValueError):
            wildcard.wildcard_to_mask("0.0.254.255")
