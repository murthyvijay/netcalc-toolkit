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


def type3_routes(vteps, vnis_per_vtep):
    """Inclusive-multicast type-3 routes: one per VNI per VTEP."""
    return vteps * vnis_per_vtep


def total_routes(vteps, vnis_per_vtep, hosts, ip_per_mac=1, prefixes=0):
    """EVPN routes a route reflector carries (type-2 + type-3 + type-5)."""
    return type2_routes(hosts, ip_per_mac) + type3_routes(vteps, vnis_per_vtep) + prefixes


def ingress_replication_bps(bum_bps, vteps_in_vni):
    """Uplink load (b/s) of head-end replicating ``bum_bps`` to every other VTEP.

    >>> ingress_replication_bps(100e6, 64)
    6300000000.0
    """
    return bum_bps * (vteps_in_vni - 1)


def fits_local_vlans(vnis_per_switch):
    """True if a switch can map this many L2 VNIs to local VLAN IDs."""
    return vnis_per_switch <= USABLE_VLANS


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("routes", help="EVPN route counts")
    p.add_argument("--vteps", type=int, required=True)
    p.add_argument("--vnis", type=int, required=True, help="L2 VNIs per VTEP")
    p.add_argument("--hosts", type=int, required=True)
    p.add_argument("--ip-per-mac", type=int, default=1)
    p.add_argument("--prefixes", type=int, default=0, help="type-5 prefixes")
    p = sub.add_parser("bum", help="ingress replication load")
    p.add_argument("--rate", required=True, help="BUM traffic sourced by one VTEP")
    p.add_argument("--vteps", type=int, required=True, help="VTEPs in the VNI")
    args = parser.parse_args(argv)

    if args.cmd == "routes":
        t2 = type2_routes(args.hosts, args.ip_per_mac)
        t3 = type3_routes(args.vteps, args.vnis)
        print(f"type-2 {t2:,}, type-3 {t3:,}, type-5 {args.prefixes:,}: "
              f"{total_routes(args.vteps, args.vnis, args.hosts, args.ip_per_mac, args.prefixes):,} total")
        if not fits_local_vlans(args.vnis):
            print(f"warning: {args.vnis} L2 VNIs exceed {USABLE_VLANS} local VLANs per switch")
    else:
        load = ingress_replication_bps(parse_rate(args.rate), args.vteps)
        print(f"{fmt_rate(load)} of replicated BUM traffic leaves the source VTEP")


if __name__ == "__main__":
    main()
