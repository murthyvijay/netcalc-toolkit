import unittest

from netcalc.aifabric import loadbalance


class TestClosedForm(unittest.TestCase):
    def test_birthday(self):
        self.assertAlmostEqual(loadbalance.collision_probability(2, 2), 0.5)
        self.assertEqual(loadbalance.collision_probability(5, 4), 1.0)
        self.assertAlmostEqual(loadbalance.collision_probability(23, 365), 0.5073, places=3)

    def test_idle_paths(self):
        self.assertAlmostEqual(loadbalance.expected_idle_paths(1, 4), 3.0)


class TestSimulation(unittest.TestCase):
    def test_reproducible(self):
        a = loadbalance.simulate_max_load(16, 16, trials=200, seed=7)
        b = loadbalance.simulate_max_load(16, 16, trials=200, seed=7)
        self.assertEqual(a, b)

    def test_spraying_beats_flow_hashing(self):
        ecmp = loadbalance.simulate_max_load(32, 32, 1, trials=300)
        spray = loadbalance.simulate_max_load(32, 32, 256, trials=300)
        self.assertGreater(ecmp, 2.0)
        self.assertLess(spray, 1.3)
        self.assertGreater(loadbalance.effective_throughput_fraction(spray),
                           loadbalance.effective_throughput_fraction(ecmp))


if __name__ == "__main__":
    unittest.main()
