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


class TestChannels(unittest.TestCase):
    def test_centre_frequencies(self):
        self.assertEqual(wifi.channel_mhz("2.4", 6), 2437)
        self.assertEqual(wifi.channel_mhz("2.4", 14), 2484)
        self.assertEqual(wifi.channel_mhz("5", 36), 5180)
        self.assertEqual(wifi.channel_mhz("6", 37), 6135)

    def test_non_overlapping(self):
        self.assertEqual(wifi.non_overlapping_24ghz(), [1, 6, 11])


class TestAirtime(unittest.TestCase):
    def test_frame_airtime(self):
        self.assertAlmostEqual(wifi.frame_airtime_us(1500, 600), 60.0)
        self.assertAlmostEqual(wifi.frame_airtime_us(1500, 6, overhead_us=0), 2000.0)


if __name__ == "__main__":
    unittest.main()
