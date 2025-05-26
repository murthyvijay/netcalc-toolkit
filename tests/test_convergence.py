import unittest

from netcalc.routing import convergence


class TestComponents(unittest.TestCase):
    def test_flooding(self):
        self.assertAlmostEqual(convergence.flooding_delay(4, 0.01, 0.05), 0.09)

    def test_fib(self):
        self.assertAlmostEqual(convergence.fib_update_time(20000, 20e-6), 0.4)
        self.assertAlmostEqual(convergence.fib_update_time(20000, 20e-6, pic=True), 20e-6)
