import unittest

from netcalc.aifabric import parallelism


class TestDataParallel(unittest.TestCase):
    def test_allreduce_volume(self):
        self.assertAlmostEqual(parallelism.allreduce_bytes_per_rank(1000, 4), 1500)

    def test_gradient_bytes(self):
        self.assertAlmostEqual(parallelism.dp_bytes_per_step(1e9, 2, 2), 2e9)
        self.assertAlmostEqual(parallelism.dp_bytes_per_step(70e9, 2, 64), 2 * 63 / 64 * 140e9)
