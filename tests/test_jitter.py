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
