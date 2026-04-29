"""EIGRP classic composite metric and the feasibility condition.

With K values (K1..K5) the classic metric is::

    BW    = 10^7 / minimum bandwidth along the path (kbps)
    DELAY = sum of interface delays (microseconds) / 10
    metric = 256 * (K1*BW + K2*BW/(256 - load) + K3*DELAY)
    if K5 != 0: metric *= K5 / (reliability + K4)

Defaults are K1 = K3 = 1, K2 = K4 = K5 = 0, so the metric reduces to
``256 * (BW + DELAY)``. Integer division follows IOS behaviour.

Usage::

    python -m netcalc.ccna.eigrp metric --bw-kbps 100000 1000000 --delay-us 100 10
    python -m netcalc.ccna.eigrp fs --fd 28160 --rd 25600 30720
"""

import argparse

DEFAULT_K = (1, 0, 1, 0, 0)


def classic_metric(bandwidths_kbps, delays_us, k=DEFAULT_K, load=1, reliability=255):
    """EIGRP classic composite metric for a path."""
    k1, k2, k3, k4, k5 = k
    bw = 10 ** 7 // min(bandwidths_kbps)
    delay = sum(delays_us) // 10
    metric = k1 * bw + (k2 * bw) // (256 - load) + k3 * delay
    if k5:
        metric = metric * k5 // (reliability + k4)
    return 256 * metric


def is_feasible_successor(reported_distance, feasible_distance):
    """Feasibility condition: RD must be strictly less than the current FD."""
    return reported_distance < feasible_distance


def feasible_successors(feasible_distance, reported_distances):
    """Filter neighbours whose reported distance passes the feasibility condition."""
    return [rd for rd in reported_distances if is_feasible_successor(rd, feasible_distance)]


def variance_paths(best_metric, metrics, variance=1):
    """Paths eligible for unequal-cost load balancing with ``variance``."""
    return [m for m in metrics if m <= best_metric * variance]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("metric")
    p.add_argument("--bw-kbps", type=int, nargs="+", required=True)
    p.add_argument("--delay-us", type=int, nargs="+", required=True)
    p.add_argument("--k", type=int, nargs=5, default=list(DEFAULT_K))
    p.add_argument("--load", type=int, default=1)
    p.add_argument("--reliability", type=int, default=255)
    p = sub.add_parser("fs", help="feasibility condition check")
    p.add_argument("--fd", type=int, required=True)
    p.add_argument("--rd", type=int, nargs="+", required=True)
    args = parser.parse_args(argv)

    if args.cmd == "metric":
        print(classic_metric(args.bw_kbps, args.delay_us, tuple(args.k), args.load,
                             args.reliability))
    else:
        for rd in args.rd:
            ok = is_feasible_successor(rd, args.fd)
            print(f"RD {rd}: {'feasible successor' if ok else 'not feasible'}")


if __name__ == "__main__":
    main()
