import unittest

from netcalc.aifabric import algorithms, collectives


class TestFlatAlgorithms(unittest.TestCase):
    def test_ring_matches_collectives_model(self):
        self.assertAlmostEqual(algorithms.ring_time(1e9, 64, 400e9, 5e-6),
                               collectives.ring_allreduce_time(1e9, 64, 400e9, 5e-6))

    def test_tree_latency_grows_with_log(self):
        t = algorithms.tree_time(0, 1024, 400e9, 1e-6)
        self.assertAlmostEqual(t, 20e-6)

    def test_halving_doubling(self):
        self.assertAlmostEqual(algorithms.halving_doubling_time(1e6, 2, 8e6), 1.0)
        self.assertAlmostEqual(algorithms.halving_doubling_time(0, 8, 1e9, 1e-6), 6e-6)

    def test_tree_efficiency(self):
        self.assertAlmostEqual(algorithms.tree_time(1e6, 2, 8e6, efficiency=0.5), 4.0)


class TestChoice(unittest.TestCase):
    def test_small_messages_avoid_ring(self):
        name, _ = algorithms.best_algorithm(1e3, 512, 400e9, 5e-6)
        self.assertNotEqual(name, "ring")

    def test_crossover_is_where_times_meet(self):
        s = algorithms.ring_tree_crossover(64, 400e9, 5e-6, tree_efficiency=0.7)
        self.assertAlmostEqual(algorithms.ring_time(s, 64, 400e9, 5e-6),
                               algorithms.tree_time(s, 64, 400e9, 5e-6, 0.7))


class TestHierarchical(unittest.TestCase):
    def test_beats_flat_ring_at_scale(self):
        h = algorithms.hierarchical_time(1e9, 64, 8, 400e9, 3.6e12, 5e-6)
        flat = algorithms.ring_time(1e9, 512, 400e9, 5e-6)
        self.assertLess(h, flat)

    def test_single_server_is_intra_only(self):
        t = algorithms.hierarchical_time(8e9, 1, 8, 400e9, 8e9 * 8)
        self.assertAlmostEqual(t, 2 * 7 / 8)


if __name__ == "__main__":
    unittest.main()
