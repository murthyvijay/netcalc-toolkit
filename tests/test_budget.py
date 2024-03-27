import unittest

from netcalc.optics import budget


class TestSpanLoss(unittest.TestCase):
    def test_typical_span(self):
        self.assertAlmostEqual(budget.span_loss(40, 0.25, connectors=4, splices=8), 12.8)

    def test_defaults_include_two_connectors(self):
        self.assertAlmostEqual(budget.span_loss(10, 0.35), 4.5)
