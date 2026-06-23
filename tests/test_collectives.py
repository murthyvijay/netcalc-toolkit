import unittest

from netcalc.aifabric import collectives


class TestBandwidth(unittest.TestCase):
    def test_algbw(self):
        self.assertEqual(collectives.algbw(1e9, 0.1), 80e9)

    def test_busbw_factors(self):
        self.assertAlmostEqual(collectives.busbw("all_reduce", 1e9, 0.1, 8), 80e9 * 14 / 8)
        self.assertAlmostEqual(collectives.busbw("all_gather", 1e9, 0.1, 8), 80e9 * 7 / 8)
        self.assertEqual(collectives.busbw("broadcast", 1e9, 0.1, 8), 80e9)
