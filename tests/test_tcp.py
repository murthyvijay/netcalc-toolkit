import math
import unittest

from netcalc.perf import tcp


class TestMathis(unittest.TestCase):
    def test_formula(self):
        expected = 1460 * 8 / 0.05 * math.sqrt(1.5) / math.sqrt(1e-4)
        self.assertAlmostEqual(tcp.mathis_throughput(1460, 0.05, 1e-4), expected)

    def test_max_loss_inverse(self):
        p = tcp.mathis_max_loss(1460, 0.05, 1e9)
        self.assertAlmostEqual(tcp.mathis_throughput(1460, 0.05, p) / 1e9, 1.0)

    def test_zero_loss_rejected(self):
        with self.assertRaises(ValueError):
            tcp.mathis_throughput(1460, 0.05, 0)
