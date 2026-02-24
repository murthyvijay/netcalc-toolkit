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
