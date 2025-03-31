import unittest

from netcalc.routing import bfd


class TestNegotiation(unittest.TestCase):
    def test_slower_side_wins(self):
        self.assertEqual(bfd.negotiated_interval(0.05, 0.3), 0.3)
        self.assertEqual(bfd.negotiated_interval(0.3, 0.05), 0.3)

    def test_detection_time(self):
        self.assertAlmostEqual(bfd.detection_time(3, 0.05, 0.05), 0.15)

    def test_asymmetric_session(self):
        at_local, at_remote = bfd.session_detection_times(0.05, 0.05, 0.1, 0.05, 3, 3)
        self.assertAlmostEqual(at_local, 0.3)
        self.assertAlmostEqual(at_remote, 0.15)


class TestLoad(unittest.TestCase):
    def test_packets_per_second(self):
        self.assertAlmostEqual(bfd.packets_per_second(0.05, 400), 16000)
        self.assertAlmostEqual(bfd.packets_per_second(0.05, 400, both_directions=False), 8000)
