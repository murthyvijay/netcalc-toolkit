import unittest

from netcalc.aifabric import roce


class TestPfc(unittest.TestCase):
    def test_cable_delay(self):
        self.assertAlmostEqual(roce.cable_delay(100) * 1e9, 489.7, places=1)

    def test_headroom_grows_with_rate_and_length(self):
        base = roce.pfc_headroom(100e9, 10)
        self.assertGreater(roce.pfc_headroom(400e9, 10), base)
        self.assertGreater(roce.pfc_headroom(100e9, 300), base)

    def test_headroom_components(self):
        h = roce.pfc_headroom(100e9, 0, mtu_bytes=1000, response_s=0)
        self.assertAlmostEqual(h, 2 * 1000 + 64)

    def test_pause_quanta(self):
        self.assertAlmostEqual(roce.pause_time(65535, 100e9), 65535 * 512 / 100e9)


class TestEcn(unittest.TestCase):
    def test_red_curve(self):
        self.assertEqual(roce.ecn_mark_probability(50, 100, 400, 0.2), 0.0)
        self.assertAlmostEqual(roce.ecn_mark_probability(250, 100, 400, 0.2), 0.1)
        self.assertEqual(roce.ecn_mark_probability(500, 100, 400, 0.2), 1.0)
