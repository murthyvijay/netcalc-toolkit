import unittest

from netcalc.layer1 import qfactor


class TestQToBer(unittest.TestCase):
    def test_known_points(self):
        self.assertAlmostEqual(qfactor.q_to_ber(6) / 9.87e-10, 1, places=2)
        self.assertAlmostEqual(qfactor.q_to_ber(7) / 1.28e-12, 1, places=2)

    def test_inverse(self):
        for target in (1e-3, 1e-9, 1e-15):
            self.assertAlmostEqual(qfactor.q_to_ber(qfactor.ber_to_q(target)) / target, 1, places=6)

    def test_out_of_range(self):
        with self.assertRaises(ValueError):
            qfactor.ber_to_q(0.7)


class TestQdB(unittest.TestCase):
    def test_db(self):
        self.assertAlmostEqual(qfactor.q_to_db(10), 20.0)
        self.assertAlmostEqual(qfactor.db_to_q(qfactor.q_to_db(7.03)), 7.03)

    def test_eye(self):
        self.assertAlmostEqual(qfactor.q_from_eye(1.0, 0.0, 0.07, 0.07), 1 / 0.14)


if __name__ == "__main__":
    unittest.main()
