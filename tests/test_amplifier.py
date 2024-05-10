import unittest

from netcalc.optics import amplifier


class TestChannelPower(unittest.TestCase):
    def test_sharing_total_power(self):
        self.assertAlmostEqual(amplifier.per_channel_power(20, 40), 3.98, places=2)
        self.assertAlmostEqual(amplifier.per_channel_power(20, 1), 20.0)

    def test_round_trip(self):
        self.assertAlmostEqual(amplifier.total_power(amplifier.per_channel_power(17, 96), 96), 17)
