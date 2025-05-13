import unittest

from netcalc.routing import mpls


class TestOverhead(unittest.TestCase):
    def test_stack(self):
        self.assertEqual(mpls.stack_overhead(3), 12)

    def test_mtu(self):
        self.assertEqual(mpls.required_mtu(1500, 3), 1512)
        self.assertEqual(mpls.required_mtu(1500, 2, l2_overhead=14), 1522)


class TestScale(unittest.TestCase):
    def test_label_space(self):
        self.assertEqual(mpls.usable_labels(), 1_048_560)

    def test_rsvp_mesh(self):
        self.assertEqual(mpls.rsvp_full_mesh_lsps(200), 39_800)

    def test_msd(self):
        self.assertTrue(mpls.sr_path_fits(5, 10))
        self.assertFalse(mpls.sr_path_fits(12, 10))
