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
