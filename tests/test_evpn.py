import unittest

from netcalc.routing import evpn


class TestRoutes(unittest.TestCase):
    def test_type2(self):
        self.assertEqual(evpn.type2_routes(40000), 80000)
        self.assertEqual(evpn.type2_routes(40000, ip_per_mac=2), 120000)

    def test_type3(self):
        self.assertEqual(evpn.type3_routes(64, 500), 32000)

    def test_total(self):
        self.assertEqual(evpn.total_routes(64, 500, 40000, 1, prefixes=1000), 113000)


class TestReplication(unittest.TestCase):
    def test_ingress_replication(self):
        self.assertEqual(evpn.ingress_replication_bps(100e6, 64), 6.3e9)
        self.assertEqual(evpn.ingress_replication_bps(100e6, 1), 0)
