"""BGP best-path selection, iBGP session counts and ASN formats.

Routes are compared attribute by attribute until one wins (Cisco order)::

    1. highest weight (local to the router)
    2. highest LOCAL_PREF
    3. locally originated
    4. shortest AS_PATH
    5. lowest ORIGIN (IGP < EGP < incomplete)
    6. lowest MED (only between routes from the same neighbouring AS)
    7. eBGP over iBGP
    8. lowest IGP metric to the next hop
    9. lowest router ID

A full iBGP mesh of n routers needs ``n (n - 1) / 2`` sessions; with route
reflectors each client peers only with the reflectors, and the reflectors
mesh among themselves. 4-byte AS numbers (RFC 6793) are written as plain
integers or in asdot ``high.low`` form.

Usage::

    python -m netcalc.routing.bgp best "A:lp=200,path=65001 65002" B:lp=100,path=65003
    python -m netcalc.routing.bgp sessions --routers 50 --reflectors 2
    python -m netcalc.routing.bgp asn 4200000001
"""

import argparse

ORIGIN_RANK = {"i": 0, "e": 1, "?": 2}
PRIVATE_ASN_RANGES = ((64512, 65534), (4_200_000_000, 4_294_967_294))
DEFAULTS = {"weight": 0, "local_pref": 100, "local": False, "as_path": (), "origin": "i",
            "med": 0, "ebgp": True, "igp_metric": 0, "router_id": "0.0.0.0"}


def _attr(route, key):
    return route.get(key, DEFAULTS[key])


def _router_id_key(rid):
    return tuple(int(octet) for octet in str(rid).split("."))


def compare(a, b, always_compare_med=False):
    """Return ``(winner, step)`` for two routes; ``step`` names the deciding rule."""
    steps = (
        ("weight", lambda r: -_attr(r, "weight")),
        ("local_pref", lambda r: -_attr(r, "local_pref")),
        ("locally originated", lambda r: not _attr(r, "local")),
        ("as_path length", lambda r: len(_attr(r, "as_path"))),
        ("origin", lambda r: ORIGIN_RANK[_attr(r, "origin")]),
    )
    for name, key in steps:
        if key(a) != key(b):
            return (a if key(a) < key(b) else b), name
    path_a, path_b = _attr(a, "as_path"), _attr(b, "as_path")
    same_neighbor = path_a[:1] == path_b[:1]
    if (always_compare_med or same_neighbor) and _attr(a, "med") != _attr(b, "med"):
        return (a if _attr(a, "med") < _attr(b, "med") else b), "med"
    if _attr(a, "ebgp") != _attr(b, "ebgp"):
        return (a if _attr(a, "ebgp") else b), "ebgp over ibgp"
    if _attr(a, "igp_metric") != _attr(b, "igp_metric"):
        return (a if _attr(a, "igp_metric") < _attr(b, "igp_metric") else b), "igp metric"
    ra, rb = _router_id_key(_attr(a, "router_id")), _router_id_key(_attr(b, "router_id"))
    return (a if ra <= rb else b), "router id"


def best_path(routes, always_compare_med=False):
    """Best route of a list, with the rule that decided the final comparison."""
    best, reason = routes[0], "only path"
    for route in routes[1:]:
        best, reason = compare(best, route, always_compare_med)
    return best, reason


def full_mesh_sessions(routers):
    """iBGP sessions in a full mesh.

    >>> full_mesh_sessions(50)
    1225
    """
    return routers * (routers - 1) // 2


def route_reflector_sessions(routers, reflectors):
    """iBGP sessions when ``reflectors`` (fully meshed) serve every other router."""
    clients = routers - reflectors
    return full_mesh_sessions(reflectors) + clients * reflectors


def to_asdot(asn):
    """asdot notation of a 4-byte ASN (``65536 -> "1.0"``); 2-byte ASNs stay plain.

    >>> to_asdot(4200000001)
    '64086.59905'
    """
    return str(asn) if asn < 65536 else f"{asn >> 16}.{asn & 0xFFFF}"


def from_asdot(text):
    """Parse ``"1.10"`` or ``"65546"`` into an integer ASN."""
    if "." in str(text):
        high, low = (int(x) for x in str(text).split("."))
        return (high << 16) | low
    return int(text)


def is_private_asn(asn):
    """True for private-use ASNs (RFC 6996)."""
    return any(lo <= asn <= hi for lo, hi in PRIVATE_ASN_RANGES)


def negotiated_timers(local_hold, peer_hold):
    """Hold time both sides use (the lower) and the matching keepalive (hold / 3)."""
    hold = min(local_hold, peer_hold)
    return hold, hold // 3


def parse_route(spec):
    """Parse ``"name:lp=200,path=65001 65002,med=10,ibgp,rid=1.1.1.1"`` into a route dict."""
    name, _, attrs = spec.partition(":")
    route = {"name": name}
    keys = {"w": "weight", "lp": "local_pref", "med": "med", "igp": "igp_metric"}
    for item in filter(None, attrs.split(",")):
        key, _, value = item.partition("=")
        if key in keys:
            route[keys[key]] = int(value)
        elif key == "path":
            route["as_path"] = tuple(int(x) for x in value.split())
        elif key == "origin":
            route["origin"] = value
        elif key == "rid":
            route["router_id"] = value
        elif key == "ibgp":
            route["ebgp"] = False
        elif key == "local":
            route["local"] = True
        else:
            raise ValueError(f"unknown attribute {key!r}")
    return route


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("best", help="run best-path selection")
    p.add_argument("routes", nargs="+",
                   help="name:lp=..,w=..,path=AS AS,origin=i|e|?,med=..,igp=..,rid=..,ibgp,local")
    p.add_argument("--always-compare-med", action="store_true")
    p = sub.add_parser("sessions", help="full-mesh vs route-reflector session count")
    p.add_argument("--routers", type=int, required=True)
    p.add_argument("--reflectors", type=int, default=2)
    p = sub.add_parser("asn", help="convert an ASN between asplain and asdot")
    p.add_argument("asn")
    args = parser.parse_args(argv)

    if args.cmd == "best":
        best, reason = best_path([parse_route(r) for r in args.routes], args.always_compare_med)
        print(f"best path: {best['name']} (decided by {reason})")
    elif args.cmd == "sessions":
        mesh = full_mesh_sessions(args.routers)
        rr = route_reflector_sessions(args.routers, args.reflectors)
        print(f"full mesh {mesh} sessions; with {args.reflectors} route reflectors {rr}")
    else:
        asn = from_asdot(args.asn)
        kind = "private" if is_private_asn(asn) else "public"
        print(f"asplain {asn}, asdot {to_asdot(asn)} ({kind})")


if __name__ == "__main__":
    main()
