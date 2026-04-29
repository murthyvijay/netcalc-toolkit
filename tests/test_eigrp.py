import unittest

from netcalc.ccna import eigrp


class TestMetric(unittest.TestCase):
    def test_fast_ethernet(self):
        self.assertEqual(eigrp.classic_metric([100000], [100]), 28160)

    def test_path(self):
        self.assertEqual(eigrp.classic_metric([100000, 1000000], [100, 10]), 28416)

    def test_t1_serial(self):
        self.assertEqual(eigrp.classic_metric([1544], [20000]), 2169856)

    def test_k5_reliability(self):
        k = (1, 0, 1, 0, 1)
        self.assertEqual(eigrp.classic_metric([100000], [100], k=k, reliability=255), 0)
        self.assertEqual(eigrp.classic_metric([100000], [100], k=(1, 0, 1, 1, 1),
                                              reliability=255), 256 * (110 * 1 // 256))


class TestFeasibility(unittest.TestCase):
    def test_condition(self):
        self.assertTrue(eigrp.is_feasible_successor(25600, 28160))
        self.assertFalse(eigrp.is_feasible_successor(28160, 28160))
        self.assertEqual(eigrp.feasible_successors(28160, [25600, 30720]), [25600])

    def test_variance(self):
        self.assertEqual(eigrp.variance_paths(100, [100, 150, 250], variance=2), [100, 150])


if __name__ == "__main__":
    unittest.main()
