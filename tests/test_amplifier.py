import unittest

from netcalc.optics import amplifier


class TestChannelPower(unittest.TestCase):
    def test_sharing_total_power(self):
        self.assertAlmostEqual(amplifier.per_channel_power(20, 40), 3.98, places=2)
        self.assertAlmostEqual(amplifier.per_channel_power(20, 1), 20.0)

    def test_round_trip(self):
        self.assertAlmostEqual(amplifier.total_power(amplifier.per_channel_power(17, 96), 96), 17)


class TestSpans(unittest.TestCase):
    def test_spans_and_inline_amplifiers(self):
        self.assertEqual(amplifier.spans_needed(600, 80), 8)
        self.assertEqual(amplifier.spans_needed(160, 80), 2)
        self.assertEqual(amplifier.inline_amplifiers(160, 80), 1)
        self.assertEqual(amplifier.spans_needed(10, 80), 1)

    def test_gain(self):
        self.assertEqual(amplifier.gain_needed(20, 2.5), 22.5)
