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


class TestPlans(unittest.TestCase):
    def test_c_band_channel_counts(self):
        self.assertEqual(len(dwdm.band_plan("C", 100)), 49)
        self.assertEqual(len(dwdm.band_plan("C", 50)), 97)

    def test_plan_is_ordered_and_in_band(self):
        plan = dwdm.band_plan("L", 100)
        freqs = [f for _, f, _ in plan]
        self.assertEqual(freqs, sorted(freqs))
        self.assertGreaterEqual(freqs[0], 186.0 - 1e-9)
        self.assertLessEqual(freqs[-1], 190.8 + 1e-9)

    def test_flex_slots(self):
        self.assertEqual(dwdm.flex_slot(64, 0.1), (6, 75.0))
        self.assertEqual(dwdm.flex_slot(32, 0.1), (3, 37.5))
        self.assertEqual(dwdm.flex_slot(130, 0.1), (12, 150.0))


if __name__ == "__main__":
    unittest.main()
