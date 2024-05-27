import unittest

from netcalc.wireless import rf


class TestPathLoss(unittest.TestCase):
    def test_fspl(self):
        self.assertAlmostEqual(rf.fspl_db(1, 2400), 100.04, places=2)
        self.assertAlmostEqual(rf.fspl_db(10, 5800), 127.71, places=2)

    def test_doubling_distance_adds_6db(self):
        self.assertAlmostEqual(rf.fspl_db(2, 5800) - rf.fspl_db(1, 5800), 6.02, places=2)
