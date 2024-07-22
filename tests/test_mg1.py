import unittest

from netcalc.queueing import mg1


class TestPollaczekKhinchine(unittest.TestCase):
    def test_mm1_special_case(self):
        self.assertAlmostEqual(mg1.pk_wait(0.8, 1.0), 4.0)

    def test_md1_is_half_of_mm1(self):
        self.assertAlmostEqual(mg1.md1_wait(0.8, 1.0), 2.0)

    def test_rejects_saturation(self):
        with self.assertRaises(ValueError):
            mg1.pk_wait(1.0, 1.0)
