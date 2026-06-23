"""Collective communication: algorithm bandwidth, bus bandwidth, ring time.

NCCL-style benchmarks report two numbers:

* **algbw** = data size / time
* **busbw** = algbw * factor, where the factor converts to the per-link
  load of an optimal algorithm so results compare against link speed:

=================  ====================
collective         busbw factor
=================  ====================
all_reduce         2 (n - 1) / n
all_gather         (n - 1) / n
reduce_scatter     (n - 1) / n
all_to_all         (n - 1) / n
broadcast, reduce  1
=================  ====================

Ring all-reduce time with the alpha-beta model (alpha = per-step latency,
B = per-rank bandwidth)::

    T = 2 (n - 1) * alpha + 2 (n - 1) / n * S / B

Usage::

    python -m netcalc.aifabric.collectives busbw --op all_reduce --size 1GB --time 25ms --ranks 64
    python -m netcalc.aifabric.collectives ring --size 1GB --ranks 64 --bw 400G --alpha 5us
"""

import argparse

from netcalc.units import fmt_rate, fmt_time, parse_rate, parse_size, parse_time

BUSBW_FACTORS = {
    "all_reduce": lambda n: 2 * (n - 1) / n,
    "all_gather": lambda n: (n - 1) / n,
    "reduce_scatter": lambda n: (n - 1) / n,
    "all_to_all": lambda n: (n - 1) / n,
    "broadcast": lambda n: 1.0,
    "reduce": lambda n: 1.0,
}


def algbw(size_bytes, time_s):
    """Algorithm bandwidth in bits per second."""
    return size_bytes * 8 / time_s


def busbw(op, size_bytes, time_s, ranks):
    """Bus bandwidth in bits per second for collective ``op``."""
    return algbw(size_bytes, time_s) * BUSBW_FACTORS[op](ranks)


def ring_allreduce_time(size_bytes, ranks, bw_bps, alpha_s=0.0):
    """Alpha-beta estimate of ring all-reduce time in seconds."""
    steps = 2 * (ranks - 1)
    return steps * alpha_s + 2 * (ranks - 1) / ranks * size_bytes * 8 / bw_bps


def bytes_per_rank(op, size_bytes, ranks):
    """Bytes each rank sends for ``op`` with an optimal algorithm."""
    return size_bytes * BUSBW_FACTORS[op](ranks)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("busbw")
    p.add_argument("--op", choices=sorted(BUSBW_FACTORS), default="all_reduce")
    p.add_argument("--size", required=True)
    p.add_argument("--time", required=True)
    p.add_argument("--ranks", type=int, required=True)
    p = sub.add_parser("ring")
    p.add_argument("--size", required=True)
    p.add_argument("--ranks", type=int, required=True)
    p.add_argument("--bw", required=True, help="per-rank network bandwidth")
    p.add_argument("--alpha", default="0", help="per-step latency")
    args = parser.parse_args(argv)
    size = parse_size(args.size)

    if args.cmd == "busbw":
        t = parse_time(args.time)
        print(f"algbw = {fmt_rate(algbw(size, t))}, "
              f"busbw = {fmt_rate(busbw(args.op, size, t, args.ranks))}")
    else:
        t = ring_allreduce_time(size, args.ranks, parse_rate(args.bw), parse_time(args.alpha))
        print(f"ring all-reduce = {fmt_time(t)}")


if __name__ == "__main__":
    main()
