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
