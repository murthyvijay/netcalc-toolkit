import unittest

from netcalc.routing import evpn


class TestRoutes(unittest.TestCase):
    def test_type2(self):
        self.assertEqual(evpn.type2_routes(40000), 80000)
        self.assertEqual(evpn.type2_routes(40000, ip_per_mac=2), 120000)

    def test_type3(self):
        self.assertEqual(evpn.type3_routes(64, 500), 32000)
