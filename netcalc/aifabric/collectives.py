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
