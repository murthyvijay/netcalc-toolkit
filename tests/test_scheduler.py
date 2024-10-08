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
