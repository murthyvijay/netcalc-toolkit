import unittest

from netcalc.queueing import mm1k


class TestDistribution(unittest.TestCase):
    def test_probabilities_sum_to_one(self):
        for rho in (0.5, 1.0, 1.7):
            total = sum(mm1k.state_probability(rho, 10, n) for n in range(11))
            self.assertAlmostEqual(total, 1.0)

    def test_out_of_range_state(self):
        self.assertEqual(mm1k.state_probability(0.5, 5, 6), 0.0)
