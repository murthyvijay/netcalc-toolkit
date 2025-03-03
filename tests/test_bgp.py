import unittest

from netcalc.routing import bgp


class TestBestPath(unittest.TestCase):
    def test_weight_beats_local_pref(self):
        a = {"name": "a", "weight": 100, "local_pref": 50}
        b = {"name": "b", "local_pref": 300}
        self.assertEqual(bgp.best_path([a, b]), (a, "weight"))

    def test_local_pref_then_as_path(self):
        a = {"name": "a", "local_pref": 200, "as_path": (1, 2, 3)}
        b = {"name": "b", "as_path": (1,)}
        self.assertEqual(bgp.best_path([b, a])[0]["name"], "a")
        c = {"name": "c", "as_path": (7, 8)}
        self.assertEqual(bgp.best_path([c, b]), (b, "as_path length"))

    def test_origin(self):
        a = {"name": "a", "origin": "?"}
        b = {"name": "b", "origin": "i"}
        self.assertEqual(bgp.best_path([a, b]), (b, "origin"))

    def test_med_only_from_same_neighbor_as(self):
        a = {"name": "a", "as_path": (65001, 9), "med": 50}
        b = {"name": "b", "as_path": (65001, 8), "med": 10}
        self.assertEqual(bgp.best_path([a, b]), (b, "med"))
        c = {"name": "c", "as_path": (65002, 8), "med": 10, "router_id": "9.9.9.9"}
        self.assertEqual(bgp.best_path([a, c]), (a, "router id"))
        self.assertEqual(bgp.best_path([a, c], always_compare_med=True), (c, "med"))

    def test_ebgp_igp_and_router_id(self):
        a = {"name": "a", "ebgp": False}
        b = {"name": "b"}
        self.assertEqual(bgp.best_path([a, b]), (b, "ebgp over ibgp"))
        c = {"name": "c", "igp_metric": 20}
        d = {"name": "d", "igp_metric": 10}
        self.assertEqual(bgp.best_path([c, d]), (d, "igp metric"))
        e = {"name": "e", "router_id": "10.0.0.2"}
        f = {"name": "f", "router_id": "10.0.0.10"}
        self.assertEqual(bgp.best_path([f, e]), (e, "router id"))


class TestSessions(unittest.TestCase):
    def test_full_mesh(self):
        self.assertEqual(bgp.full_mesh_sessions(50), 1225)
        self.assertEqual(bgp.full_mesh_sessions(1), 0)

    def test_route_reflectors(self):
        self.assertEqual(bgp.route_reflector_sessions(50, 2), 97)

    def test_timers(self):
        self.assertEqual(bgp.negotiated_timers(180, 90), (90, 30))


class TestAsn(unittest.TestCase):
    def test_asdot(self):
        self.assertEqual(bgp.to_asdot(65000), "65000")
        self.assertEqual(bgp.to_asdot(65536), "1.0")
        self.assertEqual(bgp.from_asdot("1.10"), 65546)
        self.assertEqual(bgp.from_asdot(bgp.to_asdot(4200000001)), 4200000001)

    def test_private(self):
        self.assertTrue(bgp.is_private_asn(64512))
        self.assertTrue(bgp.is_private_asn(4200000001))
        self.assertFalse(bgp.is_private_asn(13335))


class TestParsing(unittest.TestCase):
    def test_parse_route(self):
        r = bgp.parse_route("A:lp=200,path=65001 65002,med=5,ibgp,rid=1.1.1.1")
        self.assertEqual(r["local_pref"], 200)
        self.assertEqual(r["as_path"], (65001, 65002))
        self.assertFalse(r["ebgp"])
        self.assertEqual(r["router_id"], "1.1.1.1")

    def test_unknown_attribute(self):
        with self.assertRaises(ValueError):
            bgp.parse_route("A:color=blue")


if __name__ == "__main__":
    unittest.main()
