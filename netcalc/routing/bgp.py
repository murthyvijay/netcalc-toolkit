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
