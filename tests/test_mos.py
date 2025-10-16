import unittest

from netcalc.perf import mos


class TestImpairments(unittest.TestCase):
    def test_delay(self):
        self.assertAlmostEqual(mos.delay_impairment(100), 2.4)
        self.assertAlmostEqual(mos.delay_impairment(277.3), 0.024 * 277.3 + 11.0)
