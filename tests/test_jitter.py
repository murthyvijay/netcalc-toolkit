import os
import tempfile
import unittest

from netcalc.perf import jitter


class TestRfc3550(unittest.TestCase):
    def test_constant_delay_has_no_jitter(self):
        send = [0, 20, 40, 60]
        self.assertEqual(jitter.rfc3550_jitter(send, [s + 7 for s in send]), 0.0)

    def test_hand_computed(self):
        # D values: 1, -2, 3 -> J = 1/16, then + (2 - J)/16, then + (3 - J)/16
        j = 0.0
        for d in (1, 2, 3):
            j += (d - j) / 16
        self.assertAlmostEqual(jitter.rfc3550_jitter([0, 20, 40, 60], [5, 26, 44, 67]), j)

    def test_validation(self):
        with self.assertRaises(ValueError):
            jitter.rfc3550_jitter([0], [1])


class TestDelayStats(unittest.TestCase):
    def test_ipdv_and_pdv(self):
        self.assertEqual(jitter.ipdv([10, 12, 11]), [2, -1])
        self.assertEqual(jitter.pdv([10, 12, 11]), [0, 2, 1])

    def test_percentile(self):
        self.assertEqual(jitter.percentile([1, 2, 3, 4, 5], 50), 3)
        self.assertAlmostEqual(jitter.percentile([0, 10], 99), 9.9)

    def test_stats(self):
        s = jitter.delay_stats([10.0, 12.0, 11.0])
        self.assertEqual(s["min"], 10.0)
        self.assertAlmostEqual(s["mean"], 11.0)
        self.assertAlmostEqual(s["mean_abs_ipdv"], 1.5)
