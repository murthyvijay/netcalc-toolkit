import unittest

from netcalc.optics import budget


class TestSpanLoss(unittest.TestCase):
    def test_typical_span(self):
        self.assertAlmostEqual(budget.span_loss(40, 0.25, connectors=4, splices=8), 12.8)

    def test_defaults_include_two_connectors(self):
        self.assertAlmostEqual(budget.span_loss(10, 0.35), 4.5)


class TestMargin(unittest.TestCase):
    def test_budget_and_margin(self):
        self.assertEqual(budget.power_budget(-1, -18), 17)
        self.assertAlmostEqual(budget.link_margin(-1, -18, 11.0), 3.0)
        self.assertLess(budget.link_margin(-1, -18, 16.0), 0)

    def test_overload(self):
        ok, atten = budget.overload_check(4, 1.0, 0.0)
        self.assertFalse(ok)
        self.assertAlmostEqual(atten, 3.0)
        self.assertEqual(budget.overload_check(0, 5.0, 0.0), (True, 0.0))


class TestReach(unittest.TestCase):
    def test_reach_without_splices(self):
        self.assertAlmostEqual(budget.max_reach_km(2, -20), 72.0)

    def test_splices_shorten_reach(self):
        self.assertAlmostEqual(budget.max_reach_km(2, -20, splice_every_km=2), 60.0)

    def test_no_budget_means_no_reach(self):
        self.assertEqual(budget.max_reach_km(-10, -12), 0.0)


if __name__ == "__main__":
    unittest.main()
