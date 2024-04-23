import unittest

from netcalc.optics import coherent


class TestModulation(unittest.TestCase):
    def test_names_and_numbers(self):
        self.assertEqual(coherent.bits_per_symbol("DP-16QAM"), 4)
        self.assertEqual(coherent.bits_per_symbol("qpsk"), 2)
        self.assertEqual(coherent.bits_per_symbol("3.7"), 3.7)
        self.assertEqual(coherent.bits_per_symbol(6), 6)


class TestRates(unittest.TestCase):
    def test_400zr_line_rate(self):
        self.assertAlmostEqual(coherent.line_rate_gbps(59.84375, "16qam"), 478.75)

    def test_net_rate_and_baud_round_trip(self):
        net = coherent.net_rate_gbps(64, "16qam", fec_overhead=0.15)
        self.assertAlmostEqual(coherent.required_baud(net, "16qam", fec_overhead=0.15), 64)

    def test_800g_needs_about_115gbd(self):
        self.assertAlmostEqual(coherent.required_baud(800, "16qam"), 115.0)
