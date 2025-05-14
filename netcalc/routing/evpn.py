"""VXLAN EVPN scale: route counts, ingress replication load and VNI/VLAN limits.

In a BGP EVPN fabric every VTEP advertises:

* a type-2 (MAC/IP) route per locally learned host, received by every VTEP
  that imports the VNI, so a route reflector holds about
  ``hosts * (1 + ip_per_mac)`` type-2 routes;
* a type-3 (inclusive multicast) route per VNI per VTEP, used to build the
  flood list for BUM traffic;
* type-5 (IP prefix) routes per tenant prefix.

With **ingress replication** each broadcast, unknown-unicast or multicast
frame is copied once per remote VTEP in the VNI, so ``BUM rate * (VTEPs - 1)``
leaves the source's uplinks. VNIs are 24 bits (16 million) while a switch
still maps them to a 12-bit local VLAN space (4094).

Usage::

    python -m netcalc.routing.evpn routes --vteps 64 --vnis 500 --hosts 40000 --ip-per-mac 1
    python -m netcalc.routing.evpn bum --rate 100M --vteps 64
"""

import argparse

from netcalc.units import fmt_rate, parse_rate

VNI_SPACE = 2 ** 24
USABLE_VLANS = 4094


def type2_routes(hosts, ip_per_mac=1):
    """MAC and MAC+IP type-2 routes for ``hosts`` endpoints."""
    return hosts * (1 + ip_per_mac)
