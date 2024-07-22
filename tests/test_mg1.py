import unittest

from netcalc.queueing import mg1


class TestPollaczekKhinchine(unittest.TestCase):
    def test_mm1_special_case(self):
        self.assertAlmostEqual(mg1.pk_wait(0.8, 1.0), 4.0)

    def test_md1_is_half_of_mm1(self):
        self.assertAlmostEqual(mg1.md1_wait(0.8, 1.0), 2.0)

    def test_rejects_saturation(self):
        with self.assertRaises(ValueError):
            mg1.pk_wait(1.0, 1.0)


class TestKingman(unittest.TestCase):
    def test_poisson_matches_pk(self):
        self.assertAlmostEqual(mg1.kingman_wait(0.7, 1.0, 1.0, 0.5), mg1.pk_wait(0.7, 1.0, 0.5))

    def test_bursty_arrivals_wait_longer(self):
        self.assertAlmostEqual(mg1.kingman_wait(0.5, 1.0, 4.0, 0.0), 2.0)


class TestPacketMix(unittest.TestCase):
    def test_moments(self):
        mean, cs2 = mg1.size_mix_moments({64: 7, 576: 4, 1500: 1})
        self.assertAlmostEqual(mean, 354.33, places=2)
        self.assertAlmostEqual(cs2, 1.3933, places=4)

    def test_fixed_size_mix(self):
        self.assertAlmostEqual(mg1.mix_wait(1e9, 0.5, {1000: 1}), mg1.md1_wait(0.5, 8e-6))

    def test_parse(self):
        self.assertEqual(mg1.parse_mix(["64:7", "1500:1"]), {64: 7.0, 1500: 1.0})


if __name__ == "__main__":
    unittest.main()
