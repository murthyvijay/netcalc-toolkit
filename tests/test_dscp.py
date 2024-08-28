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


class TestTosByte(unittest.TestCase):
    def test_ef_is_0xb8(self):
        self.assertEqual(dscp.dscp_to_tos("EF"), 0xB8)
        self.assertEqual(dscp.dscp_to_tos(46, ecn=0b11), 0xBB)

    def test_decode(self):
        self.assertEqual(dscp.tos_to_dscp(0xB9), (46, 1))


class TestMappings(unittest.TestCase):
    def test_precedence_and_cos(self):
        self.assertEqual(dscp.ip_precedence("EF"), 5)
        self.assertEqual(dscp.default_cos("AF41"), 4)

    def test_drop_precedence(self):
        self.assertEqual(dscp.af_drop_precedence("AF23"), 3)
        self.assertIsNone(dscp.af_drop_precedence("EF"))

    def test_rfc4594_names_resolve(self):
        for name in dscp.RFC4594_CLASSES.values():
            self.assertIn(name, dscp.NAMED)


if __name__ == "__main__":
    unittest.main()
