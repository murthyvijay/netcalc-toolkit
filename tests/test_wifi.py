import unittest

from netcalc.wireless import wifi


class TestPhyRate(unittest.TestCase):
    def test_wifi6_headline_rates(self):
        self.assertAlmostEqual(wifi.phy_rate_mbps("ax", 11, 80), 600.5, places=1)
        self.assertAlmostEqual(wifi.phy_rate_mbps("ax", 11, 160, nss=2), 2402.0, places=0)

    def test_wifi5_and_wifi4(self):
        self.assertAlmostEqual(wifi.phy_rate_mbps("ac", 9, 80), 390.0)
        self.assertAlmostEqual(wifi.phy_rate_mbps("n", 7, 40, gi_us=0.4), 150.0)

    def test_invalid_mcs(self):
        with self.assertRaises(ValueError):
            wifi.phy_rate_mbps("ac", 11, 80)

    def test_table(self):
        table = wifi.rate_table("ac", 20)
        self.assertEqual(len(table), 10)
        self.assertEqual([m for m, _ in table], list(range(10)))
