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
