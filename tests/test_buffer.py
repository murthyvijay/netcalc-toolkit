import math
import unittest

from netcalc.aifabric import buffer


class TestIncast(unittest.TestCase):
    def test_peak_queue(self):
        self.assertAlmostEqual(buffer.incast_buffer(16, 256e3, 400e9), 15 * 256e3)
        self.assertEqual(buffer.incast_buffer(1, 256e3, 400e9), 0.0)

    def test_absorb_time(self):
        self.assertAlmostEqual(buffer.absorb_time(16e6, 4, 400e9), 16e6 * 8 / 1200e9)
        self.assertTrue(math.isinf(buffer.absorb_time(1e6, 1, 400e9)))


class TestDynamicThreshold(unittest.TestCase):
    def test_single_queue(self):
        self.assertAlmostEqual(buffer.dt_queue_limit(64e6, 1, 1), 32e6)
        self.assertAlmostEqual(buffer.dt_free_buffer(64e6, 1, 1), 32e6)

    def test_many_queues_share(self):
        self.assertAlmostEqual(buffer.dt_queue_limit(64e6, 1, 7), 8e6)
        self.assertAlmostEqual(7 * buffer.dt_queue_limit(64e6, 1, 7) +
                               buffer.dt_free_buffer(64e6, 1, 7), 64e6)


if __name__ == "__main__":
    unittest.main()
