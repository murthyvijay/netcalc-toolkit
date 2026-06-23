import unittest

from netcalc.aifabric import collectives


class TestBandwidth(unittest.TestCase):
    def test_algbw(self):
        self.assertEqual(collectives.algbw(1e9, 0.1), 80e9)

    def test_busbw_factors(self):
        self.assertAlmostEqual(collectives.busbw("all_reduce", 1e9, 0.1, 8), 80e9 * 14 / 8)
        self.assertAlmostEqual(collectives.busbw("all_gather", 1e9, 0.1, 8), 80e9 * 7 / 8)
        self.assertEqual(collectives.busbw("broadcast", 1e9, 0.1, 8), 80e9)


class TestRing(unittest.TestCase):
    def test_bandwidth_term(self):
        t = collectives.ring_allreduce_time(1e9, 64, 400e9)
        self.assertAlmostEqual(t, 2 * 63 / 64 * 8e9 / 400e9)

    def test_latency_term(self):
        t0 = collectives.ring_allreduce_time(1e9, 64, 400e9)
        t1 = collectives.ring_allreduce_time(1e9, 64, 400e9, 5e-6)
        self.assertAlmostEqual(t1 - t0, 126 * 5e-6)

    def test_bytes_per_rank(self):
        self.assertAlmostEqual(collectives.bytes_per_rank("all_reduce", 1e9, 4), 1.5e9)


if __name__ == "__main__":
    unittest.main()
