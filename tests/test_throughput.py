import unittest

from netcalc.perf import throughput


class TestBdp(unittest.TestCase):
    def test_bdp(self):
        self.assertEqual(throughput.bdp_bytes(10e9, 0.08), 100e6)

    def test_window_scale(self):
        self.assertEqual(throughput.window_scale_shift(65535), 0)
        self.assertEqual(throughput.window_scale_shift(100e6), 11)
        with self.assertRaises(ValueError):
            throughput.window_scale_shift(2 ** 31)
