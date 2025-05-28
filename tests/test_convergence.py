import unittest

from netcalc.routing import convergence


class TestComponents(unittest.TestCase):
    def test_flooding(self):
        self.assertAlmostEqual(convergence.flooding_delay(4, 0.01, 0.05), 0.09)

    def test_fib(self):
        self.assertAlmostEqual(convergence.fib_update_time(20000, 20e-6), 0.4)
        self.assertAlmostEqual(convergence.fib_update_time(20000, 20e-6, pic=True), 20e-6)


class TestBudget(unittest.TestCase):
    def test_total_is_sum(self):
        parts = convergence.convergence_budget(0.15, hops=4, prefixes=20000)
        self.assertAlmostEqual(parts["fib"], 0.4)
        self.assertAlmostEqual(parts["total"], 0.70)

    def test_pic_removes_fib_term(self):
        parts = convergence.convergence_budget(0.15, hops=4, prefixes=20000, pic=True)
        self.assertLess(parts["total"], 0.31)
