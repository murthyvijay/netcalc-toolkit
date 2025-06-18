import unittest

from netcalc.aifabric import algorithms, collectives


class TestFlatAlgorithms(unittest.TestCase):
    def test_ring_matches_collectives_model(self):
        self.assertAlmostEqual(algorithms.ring_time(1e9, 64, 400e9, 5e-6),
                               collectives.ring_allreduce_time(1e9, 64, 400e9, 5e-6))

    def test_tree_latency_grows_with_log(self):
        t = algorithms.tree_time(0, 1024, 400e9, 1e-6)
        self.assertAlmostEqual(t, 20e-6)
