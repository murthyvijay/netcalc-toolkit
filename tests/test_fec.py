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
