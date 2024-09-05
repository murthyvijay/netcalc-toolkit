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


class TestHelpers(unittest.TestCase):
    def test_summary(self):
        trace = [(0, 100), (0, 200), (0, 300)]
        summary = marker.color_summary(trace, ["green", "red", "green"])
        self.assertEqual(summary, {"green": 400, "yellow": 0, "red": 200})

    def test_conforming_bytes(self):
        self.assertAlmostEqual(marker.conforming_bytes(10e6, 15000, 0.01), 27500)

    def test_parse_trace(self):
        self.assertEqual(marker.parse_trace(["0:1500", "0.5:9KB"]), [(0.0, 1500), (0.5, 9000)])


if __name__ == "__main__":
    unittest.main()
