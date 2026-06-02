import unittest

from netcalc.aifabric import retransmit


class TestEfficiency(unittest.TestCase):
    def test_window(self):
        self.assertEqual(retransmit.window_packets(400e9, 10e-6, 4096), 123)
        self.assertEqual(retransmit.window_packets(1e6, 1e-6, 4096), 1)

    def test_gbn_worse_than_sr(self):
        self.assertAlmostEqual(retransmit.selective_efficiency(1e-3), 0.999)
        self.assertLess(retransmit.go_back_n_efficiency(1e-3, 100),
                        retransmit.selective_efficiency(1e-3))
        self.assertEqual(retransmit.go_back_n_efficiency(0, 100), 1.0)
