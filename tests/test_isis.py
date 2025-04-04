import unittest

from netcalc.routing import isis


class TestNet(unittest.TestCase):
    def test_parse(self):
        parts = isis.parse_net("49.0001.1921.6800.1001.00")
        self.assertEqual(parts["area"], "49.0001")
        self.assertEqual(parts["system_id"], "1921.6800.1001")

    def test_long_area(self):
        self.assertEqual(isis.parse_net("39.0840.8000.0000.0000.0001.00")["area"], "39.0840.8000")

    def test_invalid(self):
        with self.assertRaises(ValueError):
            isis.parse_net("49.0001.00")
