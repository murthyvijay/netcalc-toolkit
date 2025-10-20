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

    def test_jitter_buffer(self):
        self.assertEqual(mos.effective_delay_ms(80, 10), 100)


class TestScores(unittest.TestCase):
    def test_best_case(self):
        self.assertAlmostEqual(mos.r_factor(0), 93.2)
        self.assertAlmostEqual(mos.r_to_mos(93.2), 4.41, places=2)

    def test_typical_call(self):
        r = mos.r_factor(80, 10, 0.5)
        self.assertAlmostEqual(r, 88.94, places=2)
        self.assertGreater(mos.r_to_mos(r), 4.3)

    def test_mos_bounds(self):
        self.assertEqual(mos.r_to_mos(-5), 1.0)
        self.assertEqual(mos.r_to_mos(120), 4.5)


class TestBudget(unittest.TestCase):
    def test_delay_budget(self):
        d = mos.max_delay_for_mos(4.0)
        self.assertAlmostEqual(mos.r_to_mos(mos.r_factor(d)), 4.0, places=3)

    def test_unreachable_target(self):
        self.assertEqual(mos.max_delay_for_mos(4.4, loss_pct=5, codec="g729"), 0.0)


if __name__ == "__main__":
    unittest.main()
