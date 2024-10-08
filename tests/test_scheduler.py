import unittest

from netcalc.traffic import scheduler


class TestMaxMinFair(unittest.TestCase):
    def test_small_demand_is_fully_served(self):
        self.assertEqual(scheduler.max_min_fair(10, {"A": 2, "B": 6, "C": 6}),
                         {"A": 2.0, "B": 4.0, "C": 4.0})

    def test_weights(self):
        self.assertEqual(scheduler.max_min_fair(10, {"A": 8, "B": 8}, {"A": 3, "B": 1}),
                         {"A": 7.5, "B": 2.5})

    def test_undersubscribed(self):
        self.assertEqual(scheduler.max_min_fair(10, {"A": 1, "B": 2}), {"A": 1.0, "B": 2.0})


class TestDwrr(unittest.TestCase):
    def test_shares(self):
        shares = scheduler.weighted_shares({"g": 5, "s": 3, "b": 2})
        self.assertAlmostEqual(shares["g"], 0.5)

    def test_quanta_start_at_one_mtu(self):
        q = scheduler.dwrr_quanta({"g": 5, "s": 3, "b": 1}, 9216)
        self.assertEqual(q, {"g": 46080.0, "s": 27648.0, "b": 9216.0})

    def test_round_time(self):
        self.assertAlmostEqual(scheduler.round_time({"a": 1250, "b": 1250}, 10e6), 0.002)


class TestPriority(unittest.TestCase):
    def test_residual(self):
        self.assertEqual(scheduler.priority_residual(10, 3), 7)
        self.assertEqual(scheduler.priority_residual(10, 12), 0.0)

    def test_blocking(self):
        self.assertAlmostEqual(scheduler.priority_blocking_delay(9216, 10e9), 7.3728e-6)

    def test_parse_classes(self):
        demands, weights = scheduler.parse_classes(["A=2G", "B=8G:3"])
        self.assertEqual(demands, {"A": 2e9, "B": 8e9})
        self.assertEqual(weights, {"A": 1.0, "B": 3.0})


if __name__ == "__main__":
    unittest.main()
