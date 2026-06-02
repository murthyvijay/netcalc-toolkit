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


class TestMessages(unittest.TestCase):
    def test_probability(self):
        self.assertAlmostEqual(retransmit.message_retransmit_probability(1e-5, 16384),
                               1 - (1 - 1e-5) ** 16384)

    def test_expected_time(self):
        base = retransmit.expected_message_time(4096 * 100, 400e9, 4096, 0, 1e-3)
        self.assertAlmostEqual(base, 4096 * 100 * 8 / 400e9)
        lossy = retransmit.expected_message_time(4096 * 100, 400e9, 4096, 1e-3, 1e-3)
        self.assertGreater(lossy, base)


if __name__ == "__main__":
    unittest.main()
