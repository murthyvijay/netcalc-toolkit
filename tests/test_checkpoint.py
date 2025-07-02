import math
import unittest

from netcalc.aifabric import checkpoint


class TestSize(unittest.TestCase):
    def test_bytes(self):
        self.assertEqual(checkpoint.checkpoint_bytes(70e9), 980e9)
        self.assertEqual(checkpoint.checkpoint_bytes(1e9, 2), 2e9)

    def test_write_time(self):
        self.assertAlmostEqual(checkpoint.write_time(1e12, 200e9), 40.0)


class TestFailures(unittest.TestCase):
    def test_job_mtbf(self):
        self.assertAlmostEqual(checkpoint.job_mtbf_hours(50000, 10000), 5.0)

    def test_interruption(self):
        self.assertAlmostEqual(checkpoint.interruption_probability(1, 100, 100), 1 - math.exp(-1))
        self.assertEqual(checkpoint.interruption_probability(0, 100, 100), 0.0)
