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


class TestCbwfq(unittest.TestCase):
    def test_shares(self):
        alloc = qos.cbwfq_allocation(10e9, {"VOICE": 10, "DATA": 40})
        self.assertEqual(alloc["VOICE"], 1e9)
        self.assertEqual(alloc["unallocated"], 5e9)

    def test_oversubscribed(self):
        with self.assertRaises(ValueError):
            qos.cbwfq_allocation(1e9, {"A": 60, "B": 50})
