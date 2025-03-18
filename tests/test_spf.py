import unittest

from netcalc.routing import spf

SQUARE = ["A-B:10", "B-D:10", "A-C:10", "C-D:10"]


class TestGraph(unittest.TestCase):
    def test_parse_is_bidirectional(self):
        g = spf.parse_edges(["A-B:5"])
        self.assertEqual(g, {"A": {"B": 5.0}, "B": {"A": 5.0}})

    def test_directed(self):
        g = spf.parse_edges(["A-B:5"], directed=True)
        self.assertEqual(g["B"], {})


class TestDijkstra(unittest.TestCase):
    def test_distances(self):
        dist, _ = spf.dijkstra(spf.parse_edges(SQUARE + ["A-D:30"]), "A")
        self.assertEqual(dist["D"], 20)

    def test_ecmp_paths(self):
        _, preds = spf.dijkstra(spf.parse_edges(SQUARE), "A")
        self.assertEqual(spf.all_paths(preds, "A", "D"), [["A", "B", "D"], ["A", "C", "D"]])
        self.assertEqual(spf.next_hops(spf.parse_edges(SQUARE), "A", "D"), ["B", "C"])

    def test_unreachable(self):
        g = spf.parse_edges(["A-B:1", "C-D:1"])
        self.assertEqual(spf.next_hops(g, "A", "D"), [])


class TestLfa(unittest.TestCase):
    def test_node_protecting_lfa(self):
        g = spf.parse_edges(["S-E:10", "E-D:10", "S-N:10", "N-D:15"])
        self.assertEqual(spf.loop_free_alternates(g, "S", "D"), [("N", True)])

    def test_link_protecting_only(self):
        g = spf.parse_edges(["S-E:10", "E-D:10", "S-N:10", "N-E:5"])
        self.assertEqual(spf.loop_free_alternates(g, "S", "D"), [("N", False)])
