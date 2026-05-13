import unittest

from netcalc.ccna import qos


class TestMM1(unittest.TestCase):
    def test_80_percent(self):
        s = qos.mm1(1e9, 0.8, 1000)
        self.assertAlmostEqual(s["service_time"], 8e-6)
        self.assertAlmostEqual(s["queue_wait"], 32e-6)
        self.assertAlmostEqual(s["avg_queue_len"], 3.2)

    def test_saturated(self):
        with self.assertRaises(ValueError):
            qos.mm1(1e9, 1.0, 1000)
