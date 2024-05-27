import unittest

from netcalc.wireless import rf


class TestPathLoss(unittest.TestCase):
    def test_fspl(self):
        self.assertAlmostEqual(rf.fspl_db(1, 2400), 100.04, places=2)
        self.assertAlmostEqual(rf.fspl_db(10, 5800), 127.71, places=2)

    def test_doubling_distance_adds_6db(self):
        self.assertAlmostEqual(rf.fspl_db(2, 5800) - rf.fspl_db(1, 5800), 6.02, places=2)


class TestLinkBudget(unittest.TestCase):
    def test_eirp_and_dbd(self):
        self.assertEqual(rf.eirp_dbm(20, 23, 2), 41)
        self.assertAlmostEqual(rf.dbd_to_dbi(3), 5.15)

    def test_received_and_margin(self):
        rx = rf.received_power_dbm(20, 23, 23, 10, 5800)
        self.assertAlmostEqual(rx, -61.71, places=2)
        self.assertAlmostEqual(rf.fade_margin_db(rx, -75), 13.29, places=2)

    def test_max_range_inverts_budget(self):
        km = rf.max_range_km(20, 23, 23, 5800, -75, margin_db=10)
        rx = rf.received_power_dbm(20, 23, 23, km, 5800)
        self.assertAlmostEqual(rf.fade_margin_db(rx, -75), 10.0)
