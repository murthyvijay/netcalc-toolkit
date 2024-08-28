import unittest

from netcalc.traffic import dscp


class TestCodePoints(unittest.TestCase):
    def test_named_values(self):
        self.assertEqual(dscp.parse_dscp("EF"), 46)
        self.assertEqual(dscp.parse_dscp("af41"), 34)
        self.assertEqual(dscp.parse_dscp("CS6"), 48)
        self.assertEqual(dscp.parse_dscp("0x2e"), 46)

    def test_range(self):
        with self.assertRaises(ValueError):
            dscp.parse_dscp(64)

    def test_names(self):
        self.assertEqual(dscp.phb_name(0), "DF")
        self.assertEqual(dscp.phb_name(10), "AF11")
        self.assertEqual(dscp.phb_name(3), "EXP/LU")
