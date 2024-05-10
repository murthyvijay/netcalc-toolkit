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


class TestFriis(unittest.TestCase):
    def test_single_stage(self):
        self.assertAlmostEqual(amplifier.friis_nf_db([(20, 5)]), 5.0)

    def test_first_stage_dominates(self):
        self.assertAlmostEqual(amplifier.friis_nf_db([(20, 5), (15, 6), (10, 8)]), 5.043, places=3)
        low_first = amplifier.friis_nf_db([(20, 4), (20, 8)])
        high_first = amplifier.friis_nf_db([(20, 8), (20, 4)])
        self.assertLess(low_first, high_first)

    def test_parse(self):
        self.assertEqual(amplifier.parse_stages(["20:5", "15:6.5"]), [(20.0, 5.0), (15.0, 6.5)])


if __name__ == "__main__":
    unittest.main()
