import math
import unittest

from netcalc.aifabric import checkpoint


class TestSize(unittest.TestCase):
    def test_bytes(self):
        self.assertEqual(checkpoint.checkpoint_bytes(70e9), 980e9)
        self.assertEqual(checkpoint.checkpoint_bytes(1e9, 2), 2e9)

    def test_write_time(self):
        self.assertAlmostEqual(checkpoint.write_time(1e12, 200e9), 40.0)
