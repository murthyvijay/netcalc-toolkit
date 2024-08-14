import unittest

from netcalc.queueing import mm1k


class TestDistribution(unittest.TestCase):
    def test_probabilities_sum_to_one(self):
        for rho in (0.5, 1.0, 1.7):
            total = sum(mm1k.state_probability(rho, 10, n) for n in range(11))
            self.assertAlmostEqual(total, 1.0)

    def test_out_of_range_state(self):
        self.assertEqual(mm1k.state_probability(0.5, 5, 6), 0.0)


class TestLoss(unittest.TestCase):
    def test_uniform_at_full_load(self):
        self.assertAlmostEqual(mm1k.loss_probability(1.0, 9), 0.1)

    def test_known_value(self):
        self.assertAlmostEqual(mm1k.loss_probability(0.9, 20), 0.01365, places=5)

    def test_overload_drops_the_excess(self):
        self.assertAlmostEqual(mm1k.carried_load(2.0, 50), 1.0, places=6)


class TestSizing(unittest.TestCase):
    def test_buffer_for_loss(self):
        k = mm1k.buffer_for_loss(0.9, 1e-6)
        self.assertEqual(k, 110)
        self.assertLessEqual(mm1k.loss_probability(0.9, k), 1e-6)
        self.assertGreater(mm1k.loss_probability(0.9, k - 1), 1e-6)

    def test_delay_by_littles_law(self):
        self.assertAlmostEqual(mm1k.mean_delay(0.5, 1000, 1.0), 2.0, places=6)


if __name__ == "__main__":
    unittest.main()
