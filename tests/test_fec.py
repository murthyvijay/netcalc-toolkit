import unittest

from netcalc.layer1 import fec


class TestCodeParameters(unittest.TestCase):
    def test_presets(self):
        self.assertEqual(fec.correctable_symbols(fec.get_code("kr4")), 7)
        self.assertEqual(fec.correctable_symbols(fec.get_code("kp4")), 15)

    def test_custom_code(self):
        code = fec.get_code("255,239,8")
        self.assertEqual(fec.correctable_symbols(code), 8)
        self.assertAlmostEqual(fec.code_rate(code), 239 / 255)

    def test_overhead_and_burst(self):
        kp4 = fec.get_code("kp4")
        self.assertAlmostEqual(fec.overhead_pct(kp4), 30 / 514 * 100)
        self.assertEqual(fec.max_burst_bits(kp4), 141)


class TestPostFec(unittest.TestCase):
    def test_zero_errors(self):
        self.assertEqual(fec.post_fec_ber(0, "kp4"), 0.0)

    def test_fec_improves_ber(self):
        for code in ("kr4", "kp4"):
            self.assertLess(fec.post_fec_ber(1e-5, code), 1e-5)

    def test_kp4_stronger_than_kr4(self):
        self.assertLess(fec.post_fec_ber(1e-4, "kp4"), fec.post_fec_ber(1e-4, "kr4"))

    def test_monotonic(self):
        self.assertLess(fec.codeword_error_ratio(1e-5, "kp4"),
                        fec.codeword_error_ratio(1e-4, "kp4"))


class TestThresholdAndMargin(unittest.TestCase):
    def test_kp4_threshold_order_of_magnitude(self):
        threshold = fec.pre_fec_threshold("kp4", 1e-13)
        self.assertTrue(1e-4 < threshold < 1e-3)
        self.assertAlmostEqual(fec.post_fec_ber(threshold, "kp4") / 1e-13, 1, places=1)

    def test_margin(self):
        good = fec.fec_margin(1e-6, "kp4")
        bad = fec.fec_margin(1e-3, "kp4")
        self.assertTrue(good["pass"])
        self.assertGreater(good["q_margin_db"], 0)
        self.assertFalse(bad["pass"])
        self.assertLess(bad["decades"], 0)

    def test_coding_gain_positive(self):
        self.assertGreater(fec.net_coding_gain_db("kp4"), fec.net_coding_gain_db("kr4"))


if __name__ == "__main__":
    unittest.main()
