import unittest

from netcalc.routing import bfd


class TestNegotiation(unittest.TestCase):
    def test_slower_side_wins(self):
        self.assertEqual(bfd.negotiated_interval(0.05, 0.3), 0.3)
        self.assertEqual(bfd.negotiated_interval(0.3, 0.05), 0.3)

    def test_detection_time(self):
        self.assertAlmostEqual(bfd.detection_time(3, 0.05, 0.05), 0.15)
