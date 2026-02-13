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


class TestConfidence(unittest.TestCase):
    def test_zero_error_rule_of_three(self):
        bits = ber.bits_for_confidence(1e-12, 0.95)
        self.assertAlmostEqual(bits / 1e12, 2.9957, places=3)

    def test_round_trip(self):
        for errors in (0, 1, 3):
            bits = ber.bits_for_confidence(1e-12, 0.99, errors)
            self.assertAlmostEqual(ber.confidence_level(bits, 1e-12, errors), 0.99, places=6)

    def test_more_errors_need_more_bits(self):
        self.assertGreater(ber.bits_for_confidence(1e-12, 0.95, 2),
                           ber.bits_for_confidence(1e-12, 0.95, 1))
