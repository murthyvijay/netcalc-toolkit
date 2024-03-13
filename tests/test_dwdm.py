import unittest

from netcalc.optics import dwdm


class TestGrid(unittest.TestCase):
    def test_anchor_and_offsets(self):
        self.assertAlmostEqual(dwdm.frequency_thz(0), 193.1)
        self.assertAlmostEqual(dwdm.frequency_thz(-10, 50), 192.6)
        self.assertAlmostEqual(dwdm.frequency_thz(3, 100), 193.4)

    def test_channel_number(self):
        n, offset = dwdm.channel_number(193.4, 50)
        self.assertEqual(n, 6)
        self.assertAlmostEqual(offset, 0.0)
        n, offset = dwdm.channel_number(193.41, 50)
        self.assertEqual(n, 6)
        self.assertAlmostEqual(offset, 10.0, places=6)


class TestWavelength(unittest.TestCase):
    def test_anchor_wavelength(self):
        self.assertAlmostEqual(dwdm.thz_to_nm(193.1), 1552.524, places=3)

    def test_round_trip(self):
        self.assertAlmostEqual(dwdm.thz_to_nm(dwdm.nm_to_thz(1550.12)), 1550.12)

    def test_100ghz_is_0p8nm(self):
        self.assertAlmostEqual(dwdm.nm_spacing(100), 0.80, places=2)
