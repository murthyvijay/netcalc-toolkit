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


class TestTokenBucket(unittest.TestCase):
    def test_shaper_and_policer(self):
        self.assertAlmostEqual(qos.shaping_interval(50e6, 200000), 0.004)
        self.assertEqual(qos.recommended_policer_burst(8e6), 1.5e6)
        self.assertEqual(qos.parse_shares(["EF=10"]), {"EF": 10.0})


if __name__ == "__main__":
    unittest.main()
