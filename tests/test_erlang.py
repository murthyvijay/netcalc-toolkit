import unittest

from netcalc.queueing import erlang


class TestErlangB(unittest.TestCase):
    def test_textbook_value(self):
        self.assertAlmostEqual(erlang.erlang_b(10, 15), 0.0365, places=4)

    def test_edge_cases(self):
        self.assertEqual(erlang.erlang_b(5, 0), 1.0)
        self.assertAlmostEqual(erlang.erlang_b(1, 1), 0.5)

    def test_sizing(self):
        self.assertEqual(erlang.servers_for_blocking(10, 0.01), 18)
        self.assertLessEqual(erlang.erlang_b(10, 18), 0.01)
        self.assertGreater(erlang.erlang_b(10, 17), 0.01)

    def test_offered_traffic(self):
        self.assertEqual(erlang.offered_traffic(300, 120), 10.0)


class TestErlangC(unittest.TestCase):
    def test_probability_of_waiting(self):
        self.assertAlmostEqual(erlang.erlang_c(10, 12), 0.4494, places=4)
        self.assertEqual(erlang.erlang_c(10, 10), 1.0)

    def test_single_server_is_mm1(self):
        self.assertAlmostEqual(erlang.erlang_c(0.8, 1), 0.8)
        self.assertAlmostEqual(erlang.mean_wait(0.8, 1, 1.0), 4.0)

    def test_service_level(self):
        self.assertAlmostEqual(erlang.service_level(10, 12, 180, 20), 0.640, places=3)
        self.assertEqual(erlang.service_level(10, 9, 180, 20), 0.0)
        self.assertEqual(erlang.mean_wait(10, 9, 180), float("inf"))


if __name__ == "__main__":
    unittest.main()
