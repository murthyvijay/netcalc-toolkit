"""OSPF interface cost and path cost.

OSPF derives interface cost from bandwidth::

    cost = max(1, floor(reference_bandwidth / interface_bandwidth))

Cisco's default reference bandwidth is 100 Mbps, so every link at
100 Mbps or faster gets cost 1 and OSPF cannot tell 1G from 400G. Raise
``auto-cost reference-bandwidth`` (identically on every router) above the
fastest link you will ever deploy.

Usage::

    python -m netcalc.ccna.ospf cost 10G --ref 100G
    python -m netcalc.ccna.ospf table --ref 400G
    python -m netcalc.ccna.ospf path 10G 10G 1G --ref 100G
"""

import argparse

from netcalc.units import fmt_rate, parse_rate

DEFAULT_REF_BPS = 100e6
COMMON_RATES = ["10M", "100M", "1G", "10G", "25G", "40G", "100G", "400G", "800G"]
MAX_COST = 65535


def interface_cost(bandwidth_bps, reference_bps=DEFAULT_REF_BPS):
    """OSPF cost of an interface (1..65535)."""
    return min(MAX_COST, max(1, int(reference_bps // bandwidth_bps)))


def path_cost(bandwidths_bps, reference_bps=DEFAULT_REF_BPS):
    """Sum of outgoing interface costs along a path."""
    return sum(interface_cost(bw, reference_bps) for bw in bandwidths_bps)


def recommended_reference(fastest_bps, headroom=10):
    """Reference bandwidth leaving ``headroom``x room above the fastest link."""
    return fastest_bps * headroom


def cost_table(reference_bps=DEFAULT_REF_BPS, rates=COMMON_RATES):
    """List of ``(rate string, cost)`` for common link speeds."""
    return [(r, interface_cost(parse_rate(r), reference_bps)) for r in rates]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("cost")
    p.add_argument("bandwidth")
    p.add_argument("--ref", default="100M")
    p = sub.add_parser("table")
    p.add_argument("--ref", default="100M")
    p = sub.add_parser("path")
    p.add_argument("bandwidths", nargs="+")
    p.add_argument("--ref", default="100M")
    args = parser.parse_args(argv)
    ref = parse_rate(args.ref)

    if args.cmd == "cost":
        print(interface_cost(parse_rate(args.bandwidth), ref))
    elif args.cmd == "table":
        print(f"reference bandwidth {fmt_rate(ref)}")
        for rate, cost in cost_table(ref):
            print(f"{rate:>6}: {cost}")
    else:
        print(path_cost([parse_rate(b) for b in args.bandwidths], ref))


if __name__ == "__main__":
    main()
