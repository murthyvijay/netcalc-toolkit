"""Multipath reliable connection (MRC) sizing.

A multipath reliable connection keeps one reliable transport session but
sends its packets over many network paths, usually by varying an entropy
value (for example the UDP source port) that switches hash on. The design
questions are arithmetic:

* How many entropy values do I need so that every path is used?
  (coupon collector: about ``P * H(P)`` random values for P paths)
* What capacity remains when some paths fail?
* How big must the receiver's reorder buffer be, given the delay skew
  between the fastest and slowest path?

Usage::

    python -m netcalc.aifabric.mrc entropy --paths 64
    python -m netcalc.aifabric.mrc coverage --paths 64 --values 256
    python -m netcalc.aifabric.mrc failover --paths 8 --path-rate 400G --failed 1
    python -m netcalc.aifabric.mrc reorder --rate 800G --skew 4us --mtu 4096
"""

import argparse
import math

from netcalc.units import fmt_rate, fmt_size, parse_rate, parse_size, parse_time


def harmonic(n):
    """n-th harmonic number H(n) = 1 + 1/2 + ... + 1/n."""
    return sum(1 / i for i in range(1, n + 1))


def expected_entropies_to_cover(paths):
    """Expected random entropy values until every path has been hit: P * H(P)."""
    return paths * harmonic(paths)


def coverage_probability(paths, values):
    """Probability that ``values`` random entropies hit all ``paths``.

    Inclusion-exclusion: ``sum_k (-1)^k C(P, k) (1 - k/P)^V``.
    """
    total = sum((-1) ** k * math.comb(paths, k) * (1 - k / paths) ** values
                for k in range(paths + 1))
    return min(1.0, max(0.0, total))


def expected_paths_used(paths, values):
    """Expected number of distinct paths hit by ``values`` entropies."""
    return paths * (1 - (1 - 1 / paths) ** values)


def failover_capacity(paths, path_rate_bps, failed=0):
    """Aggregate capacity with ``failed`` paths removed from the spray set."""
    if failed > paths:
        raise ValueError("more failed paths than paths")
    return (paths - failed) * path_rate_bps


def reorder_buffer_bytes(rate_bps, delay_skew_s, mtu_bytes=0):
    """Receiver buffer to absorb path delay skew: rate * skew (+ one MTU)."""
    return rate_bps * delay_skew_s / 8 + mtu_bytes


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("entropy", help="entropy values needed to cover all paths")
    p.add_argument("--paths", type=int, required=True)
    p = sub.add_parser("coverage")
    p.add_argument("--paths", type=int, required=True)
    p.add_argument("--values", type=int, required=True)
    p = sub.add_parser("failover")
    p.add_argument("--paths", type=int, required=True)
    p.add_argument("--path-rate", required=True)
    p.add_argument("--failed", type=int, default=1)
    p = sub.add_parser("reorder")
    p.add_argument("--rate", required=True)
    p.add_argument("--skew", required=True, help="max minus min path delay, e.g. 4us")
    p.add_argument("--mtu", default="4096")
    args = parser.parse_args(argv)

    if args.cmd == "entropy":
        print(f"expected entropy values to touch all {args.paths} paths: "
              f"{expected_entropies_to_cover(args.paths):.0f}")
    elif args.cmd == "coverage":
        print(f"P(all paths used) = {coverage_probability(args.paths, args.values):.2%}, "
              f"expected paths used = {expected_paths_used(args.paths, args.values):.1f}")
    elif args.cmd == "failover":
        rate = parse_rate(args.path_rate)
        full = failover_capacity(args.paths, rate)
        left = failover_capacity(args.paths, rate, args.failed)
        print(f"{fmt_rate(left)} of {fmt_rate(full)} ({left / full:.1%}) after "
              f"{args.failed} path failure(s)")
    else:
        b = reorder_buffer_bytes(parse_rate(args.rate), parse_time(args.skew),
                                 parse_size(args.mtu))
        print(f"reorder buffer >= {fmt_size(b)}")


if __name__ == "__main__":
    main()
