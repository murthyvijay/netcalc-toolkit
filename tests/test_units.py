import unittest

from netcalc import units


class TestParseRate(unittest.TestCase):
    def test_prefixes(self):
        self.assertEqual(units.parse_rate("100G"), 100e9)
        self.assertEqual(units.parse_rate("25Gbps"), 25e9)
        self.assertEqual(units.parse_rate("1.5 Mb/s"), 1.5e6)
        self.assertEqual(units.parse_rate("9600"), 9600)

    def test_rejects_garbage(self):
        with self.assertRaises(ValueError):
            units.parse_rate("fast")


class TestParseSizeAndTime(unittest.TestCase):
    def test_sizes(self):
        self.assertEqual(units.parse_size("1500"), 1500)
        self.assertEqual(units.parse_size("9KB"), 9000)
        self.assertEqual(units.parse_size("2MiB"), 2 * 1024 ** 2)
        self.assertEqual(units.parse_size("8kb"), 1000)

    def test_times(self):
        self.assertAlmostEqual(units.parse_time("10ms"), 0.01)
        self.assertAlmostEqual(units.parse_time("250ns"), 250e-9)
        self.assertEqual(units.parse_time("3"), 3.0)


class TestFormatting(unittest.TestCase):
    def test_fmt(self):
        self.assertEqual(units.fmt_rate(4e11), "400 Gbps")
        self.assertEqual(units.fmt_size(1.25e6), "1.25 MB")
        self.assertEqual(units.fmt_time(2.5e-6), "2.5 us")
        self.assertEqual(units.fmt_time(0), "0 s")

    def test_db_round_trip(self):
        self.assertAlmostEqual(units.linear_to_db(units.db_to_linear(13.0)), 13.0)
        self.assertAlmostEqual(units.dbm_to_mw(0), 1.0)
        self.assertAlmostEqual(units.mw_to_dbm(10), 10.0)


if __name__ == "__main__":
    unittest.main()
