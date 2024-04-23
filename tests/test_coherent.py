import unittest

from netcalc.optics import coherent


class TestModulation(unittest.TestCase):
    def test_names_and_numbers(self):
        self.assertEqual(coherent.bits_per_symbol("DP-16QAM"), 4)
        self.assertEqual(coherent.bits_per_symbol("qpsk"), 2)
        self.assertEqual(coherent.bits_per_symbol("3.7"), 3.7)
        self.assertEqual(coherent.bits_per_symbol(6), 6)
