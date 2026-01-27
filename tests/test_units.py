import unittest

from netcalc import units


class TestParseRate(unittest.TestCase):
    def test_prefixes(self):
        self.assertEqual(units.parse_rate("100G"), 100e9)
        self.assertEqual(units.parse_rate("25Gbps"), 25e9)
        self.assertEqual(units.parse_rate("1.5 Mb/s"), 1.5e6)
        self.assertEqual(units.parse_rate("9600"), 9600)

    def test_rejects_garbage(self):
        with self.assertRaises(ValueError):
            units.parse_rate("fast")
