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
