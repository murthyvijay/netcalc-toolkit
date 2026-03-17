import unittest

from netcalc.perf import latency


class TestComponents(unittest.TestCase):
    def test_serialization(self):
        self.assertAlmostEqual(latency.serialization_delay(1500, 10e9), 1.2e-6)
        self.assertAlmostEqual(latency.serialization_delay(64, 400e9), 1.28e-9)

    def test_propagation_fibre(self):
        self.assertAlmostEqual(latency.propagation_delay(1) * 1e6, 4.897, places=3)
        self.assertAlmostEqual(latency.km_per_ms(), 204.2, places=1)

    def test_rtt(self):
        self.assertEqual(latency.rtt(2.0), 4.0)
        self.assertEqual(latency.rtt(2.0, 3.0), 5.0)


class TestPathLatency(unittest.TestCase):
    def test_store_and_forward_vs_cut_through(self):
        sf = latency.path_latency(9000, 100e9, hops=4)
        ct = latency.path_latency(9000, 100e9, hops=4, cut_through=True)
        self.assertAlmostEqual(sf["serialization"], 4 * ct["serialization"])

    def test_total(self):
        parts = latency.path_latency(1500, 10e9, hops=3, distance_km=10, processing_s=1e-6)
        expected = 3 * 1.2e-6 + latency.propagation_delay(10) + 2e-6
        self.assertAlmostEqual(parts["total"], expected)


if __name__ == "__main__":
    unittest.main()
