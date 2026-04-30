"""Spanning Tree: timers, port costs, bridge IDs and root election.

IEEE 802.1D derives the timers from the network diameter (bridges across)
and the hello time::

    max_age       = 4 * hello + 2 * diameter - 2
    forward_delay = ceil((4 * hello + 3 * diameter) / 2)

With hello = 2 s and diameter = 7 this gives the familiar 20 s / 15 s, and
classic STP needs up to ``max_age + 2 * forward_delay`` = 50 s to converge
after an indirect failure. RSTP (802.1w) converges in about three hellos.

Usage::

    python -m netcalc.ccna.stp timers --diameter 7 --hello 2
    python -m netcalc.ccna.stp cost 10G
    python -m netcalc.ccna.stp root 32768:0011.2233.4455 4096:00aa.bbcc.ddee
"""

import argparse
import math

from netcalc.units import parse_rate

SHORT_COSTS = [(10e9, 2), (1e9, 4), (100e6, 19), (10e6, 100)]


def timers(diameter=7, hello=2):
    """Recommended 802.1D timers (seconds) and worst-case convergence."""
    max_age = 4 * hello + 2 * diameter - 2
    forward_delay = math.ceil((4 * hello + 3 * diameter) / 2)
    return {
        "hello": hello,
        "max_age": max_age,
        "forward_delay": forward_delay,
        "stp_convergence": max_age + 2 * forward_delay,
        "rstp_convergence": 3 * hello,
    }


def port_cost_short(bandwidth_bps):
    """802.1D-1998 16-bit ("short") path cost."""
    for rate, cost in SHORT_COSTS:
        if bandwidth_bps >= rate:
            return cost
    return 100


def port_cost_long(bandwidth_bps):
    """802.1t 32-bit ("long") path cost: 20 Tbps / bandwidth, minimum 1."""
    return max(1, int(20e12 // bandwidth_bps))


def bridge_priority(priority, vlan=1):
    """Bridge priority field with the extended system ID (priority + VLAN).

    Priority must be a multiple of 4096 when the extended system ID is used.
    """
    if priority % 4096 or not 0 <= priority <= 61440:
        raise ValueError("priority must be a multiple of 4096 between 0 and 61440")
    return priority + vlan


def _mac_int(mac):
    return int(mac.replace(".", "").replace(":", "").replace("-", ""), 16)


def elect_root(bridges):
    """Root bridge among ``"priority:mac"`` strings: lowest priority, then MAC."""
    def key(b):
        prio, _, mac = b.partition(":")
        return int(prio), _mac_int(mac)
    return min(bridges, key=key)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("timers")
    p.add_argument("--diameter", type=int, default=7)
    p.add_argument("--hello", type=float, default=2)
    p = sub.add_parser("cost")
    p.add_argument("bandwidth")
    p = sub.add_parser("root")
    p.add_argument("bridges", nargs="+", help="PRIORITY:MAC")
    args = parser.parse_args(argv)

    if args.cmd == "timers":
        for key, value in timers(args.diameter, args.hello).items():
            print(f"{key:>17}: {value:g} s")
    elif args.cmd == "cost":
        bw = parse_rate(args.bandwidth)
        print(f"short (802.1D): {port_cost_short(bw)}, long (802.1t): {port_cost_long(bw)}")
    else:
        print(f"root bridge: {elect_root(args.bridges)}")


if __name__ == "__main__":
    main()
