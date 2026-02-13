import unittest

from netcalc.layer1 import ber


class TestMeasuredBer(unittest.TestCase):
    def test_ratio(self):
        self.assertEqual(ber.ber(5, 1e12), 5e-12)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            ber.ber(1, 0)
        with self.assertRaises(ValueError):
            ber.ber(-1, 10)
