"""IGP convergence budget: detect, flood, compute, program, and the traffic lost meanwhile.

Link-state convergence after a failure is roughly the sum of::

    detection  (BFD: interval x multiplier, or loss of light ~ 10s of ms)
  + origination and flooding  (LSA/LSP generation delay + hops x per-hop flood delay)
  + SPF delay and run time    (initial SPF throttle wait + computation)
  + FIB programming           (prefixes x per-prefix update time)

FIB programming often dominates on large tables, which is why prefix
independent convergence (BGP PIC, pre-computed backup next hops) matters:
it switches every affected prefix by updating one shared next-hop object.
Traffic lost during convergence is simply ``rate x outage``.

Usage::

    python -m netcalc.routing.convergence budget --detect 150ms --hops 4 --prefixes 20000 --per-prefix 20us
    python -m netcalc.routing.convergence loss --outage 300ms --rate 100G
"""

import argparse

from netcalc.units import fmt_size, fmt_time, parse_rate, parse_time


def flooding_delay(hops, per_hop_s=0.01, origination_s=0.05):
    """Time (s) for the failure news to reach the router ``hops`` away."""
    return origination_s + hops * per_hop_s


def fib_update_time(prefixes, per_prefix_s=20e-6, pic=False, next_hops=1):
    """Time (s) to reprogram the FIB; with PIC only the shared next hops change."""
    return (next_hops if pic else prefixes) * per_prefix_s


def convergence_budget(detect_s, hops=3, per_hop_s=0.01, origination_s=0.05, spf_delay_s=0.05,
                       spf_run_s=0.01, prefixes=1000, per_prefix_s=20e-6, pic=False):
    """Each convergence component and their total, as a dict of seconds."""
    parts = {
        "detection": detect_s,
        "flooding": flooding_delay(hops, per_hop_s, origination_s),
        "spf": spf_delay_s + spf_run_s,
        "fib": fib_update_time(prefixes, per_prefix_s, pic),
    }
    parts["total"] = sum(parts.values())
    return parts


def prefixes_within(budget_s, per_prefix_s=20e-6):
    """How many prefixes can be reprogrammed within ``budget_s``."""
    return int(budget_s / per_prefix_s)


def traffic_lost(outage_s, rate_bps):
    """Bytes black-holed while a path carrying ``rate_bps`` is converging.

    >>> traffic_lost(0.3, 100e9)
    3750000000.0
    """
    return outage_s * rate_bps / 8


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("budget", help="convergence time budget")
    p.add_argument("--detect", default="150ms")
    p.add_argument("--hops", type=int, default=3)
    p.add_argument("--per-hop", default="10ms")
    p.add_argument("--origination", default="50ms")
    p.add_argument("--spf-delay", default="50ms")
    p.add_argument("--spf-run", default="10ms")
    p.add_argument("--prefixes", type=int, default=1000)
    p.add_argument("--per-prefix", default="20us")
    p.add_argument("--pic", action="store_true", help="prefix-independent convergence")
    p = sub.add_parser("loss", help="traffic lost during an outage")
    p.add_argument("--outage", required=True)
    p.add_argument("--rate", required=True)
    args = parser.parse_args(argv)

    if args.cmd == "budget":
        parts = convergence_budget(
            parse_time(args.detect), args.hops, parse_time(args.per_hop), parse_time(args.origination),
            parse_time(args.spf_delay), parse_time(args.spf_run), args.prefixes,
            parse_time(args.per_prefix), args.pic)
        for name, seconds in parts.items():
            print(f"{name:>10}: {fmt_time(seconds)}")
    else:
        print(f"{fmt_size(traffic_lost(parse_time(args.outage), parse_rate(args.rate)))} lost")


if __name__ == "__main__":
    main()
