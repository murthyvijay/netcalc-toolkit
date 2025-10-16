import unittest

from netcalc.perf import mos


class TestImpairments(unittest.TestCase):
    def test_delay(self):
        self.assertAlmostEqual(mos.delay_impairment(100), 2.4)
        self.assertAlmostEqual(mos.delay_impairment(277.3), 0.024 * 277.3 + 11.0)

    def test_loss(self):
        self.assertEqual(mos.loss_impairment(0, "g711"), 0.0)
        self.assertEqual(mos.loss_impairment(0, "g729"), 11.0)
        self.assertAlmostEqual(mos.loss_impairment(1, "g711"), 95 / 26.1)
