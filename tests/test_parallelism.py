import unittest

from netcalc.aifabric import parallelism


class TestDataParallel(unittest.TestCase):
    def test_allreduce_volume(self):
        self.assertAlmostEqual(parallelism.allreduce_bytes_per_rank(1000, 4), 1500)

    def test_gradient_bytes(self):
        self.assertAlmostEqual(parallelism.dp_bytes_per_step(1e9, 2, 2), 2e9)
        self.assertAlmostEqual(parallelism.dp_bytes_per_step(70e9, 2, 64), 2 * 63 / 64 * 140e9)


class TestModelParallel(unittest.TestCase):
    def test_tensor_parallel(self):
        self.assertEqual(parallelism.tp_bytes_per_step(1024, 4096, 2, 1), 0.0)
        expected = 4 * 2 * (2 * 7 / 8) * 1024 * 4096 * 2
        self.assertAlmostEqual(parallelism.tp_bytes_per_step(1024, 4096, 2, 8), expected)

    def test_pipeline_boundary(self):
        self.assertEqual(parallelism.pp_bytes_per_microbatch(4096, 8192), 2 * 4096 * 8192 * 2)

    def test_bubble(self):
        self.assertAlmostEqual(parallelism.pipeline_bubble(8, 32), 7 / 39)
        self.assertEqual(parallelism.pipeline_bubble(1, 4), 0.0)


class TestTiming(unittest.TestCase):
    def test_comm_time(self):
        self.assertAlmostEqual(parallelism.comm_time(50e9, 400e9), 1.0)
        self.assertAlmostEqual(parallelism.comm_time(50e9, 400e9, efficiency=0.8), 1.25)

    def test_overlap(self):
        self.assertAlmostEqual(parallelism.step_time(1.0, 0.5), 1.5)
        self.assertAlmostEqual(parallelism.step_time(1.0, 0.5, overlap=0.8), 1.1)


if __name__ == "__main__":
    unittest.main()
