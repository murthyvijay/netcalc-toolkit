import unittest

from netcalc.perf import loss


class TestLossRatio(unittest.TestCase):
    def test_ratio(self):
        self.assertAlmostEqual(loss.loss_ratio(100000, 99950), 0.0005)

    def test_path_loss(self):
        self.assertAlmostEqual(loss.path_loss(0.01, 0.01), 0.0199)
        self.assertEqual(loss.path_loss(), 0.0)

    def test_any_loss_and_retransmissions(self):
        self.assertAlmostEqual(loss.prob_any_loss(0.5, 2), 0.75)
        self.assertAlmostEqual(loss.expected_transmissions(0.5), 2.0)
