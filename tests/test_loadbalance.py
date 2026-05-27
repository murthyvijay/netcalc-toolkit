import unittest

from netcalc.aifabric import loadbalance


class TestClosedForm(unittest.TestCase):
    def test_birthday(self):
        self.assertAlmostEqual(loadbalance.collision_probability(2, 2), 0.5)
        self.assertEqual(loadbalance.collision_probability(5, 4), 1.0)
        self.assertAlmostEqual(loadbalance.collision_probability(23, 365), 0.5073, places=3)

    def test_idle_paths(self):
        self.assertAlmostEqual(loadbalance.expected_idle_paths(1, 4), 3.0)
