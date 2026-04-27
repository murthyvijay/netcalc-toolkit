import unittest

from netcalc.ccna import summarize

FOUR = ["172.16.0.0/24", "172.16.1.0/24", "172.16.2.0/24", "172.16.3.0/24"]


class TestSummaries(unittest.TestCase):
    def test_exact(self):
        self.assertEqual(summarize.exact_aggregate(FOUR), ["172.16.0.0/22"])

    def test_single(self):
        self.assertEqual(summarize.single_summary(FOUR), "172.16.0.0/22")
        self.assertEqual(summarize.summary_waste(FOUR), 0)

    def test_gap_is_reported(self):
        nets = ["10.1.4.0/24", "10.1.5.0/24", "10.1.7.0/24"]
        self.assertEqual(summarize.exact_aggregate(nets), ["10.1.4.0/23", "10.1.7.0/24"])
        self.assertEqual(summarize.single_summary(nets), "10.1.4.0/22")
        self.assertEqual(summarize.summary_waste(nets), 256)


if __name__ == "__main__":
    unittest.main()
