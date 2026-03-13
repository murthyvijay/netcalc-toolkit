import unittest

from netcalc.layer1 import osnr


class TestReferenceBandwidth(unittest.TestCase):
    def test_0p1nm_is_12p5ghz(self):
        self.assertAlmostEqual(osnr.ref_bandwidth_hz() / 1e9, 12.48, places=2)
