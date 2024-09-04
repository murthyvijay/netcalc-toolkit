import unittest

from netcalc.traffic import marker


class TestSrTcm(unittest.TestCase):
    def test_back_to_back_burst(self):
        self.assertEqual(marker.srtcm([(0, 1500)] * 3, 1e6, 1500, 1500), ["green", "yellow", "red"])

    def test_refill_goes_to_committed_bucket_first(self):
        trace = [(0, 1500)] * 3 + [(0.01, 1500)]
        self.assertEqual(marker.srtcm(trace, 1e6, 3000, 3000), ["green", "green", "yellow", "yellow"])

    def test_steady_rate_stays_green(self):
        trace = [(i * 0.0125, 1500) for i in range(20)]
        self.assertEqual(set(marker.srtcm(trace, 1e6, 1500, 0)), {"green"})


class TestTrTcm(unittest.TestCase):
    def test_colours(self):
        colors = marker.trtcm([(0, 1500)] * 3, 1e6, 1500, 2e6, 3000)
        self.assertEqual(colors, ["green", "yellow", "red"])

    def test_pir_below_cir(self):
        with self.assertRaises(ValueError):
            marker.trtcm([(0, 64)], 2e6, 1500, 1e6, 1500)
