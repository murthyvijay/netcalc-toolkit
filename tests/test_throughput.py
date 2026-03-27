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


class TestWindowLimits(unittest.TestCase):
    def test_classic_64k_window(self):
        rate = throughput.window_limited_throughput(65535, 0.03)
        self.assertAlmostEqual(rate / 1e6, 17.476, places=2)

    def test_flows_to_fill(self):
        self.assertEqual(throughput.flows_to_fill(10e9, 0.03, 65535), 573)


class TestTransferTime(unittest.TestCase):
    def test_transfer(self):
        self.assertAlmostEqual(throughput.transfer_time(1.25e9, 1e9, 0.0), 10.0)
        self.assertAlmostEqual(throughput.transfer_time(1.25e9, 1e9, 0.1), 10.15)


if __name__ == "__main__":
    unittest.main()
