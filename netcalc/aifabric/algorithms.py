"""Collective algorithms compared: ring, tree, recursive halving-doubling and hierarchical all-reduce.

The alpha-beta model charges ``alpha`` per message (latency) and ``S / B``
per byte stream. For an all-reduce of S bytes over n ranks:

* **Ring**: ``2 (n - 1) alpha + 2 (n - 1) / n * S / B``. Bandwidth optimal,
  but latency grows linearly with n.
* **Double binary tree** (pipelined): ``2 log2(n) alpha + 2 S / B``
  approximately. Latency grows only with log n.
* **Recursive halving-doubling** (Rabenseifner): ``2 log2(n) alpha +
  2 (n - 1) / n * S / B``, for power-of-two n.
* **Hierarchical**: reduce-scatter inside each server over the fast
  scale-up link, all-reduce the 1/g shards across servers, all-gather
  inside again.

In this first-order model the tree's bandwidth term is only slightly worse
than the ring's, so trees win up to very large messages. Real pipelined trees
reach less than full link bandwidth; the ``efficiency`` factor models that and
pulls the ring/tree crossover down to practical sizes.

Usage::

    python -m netcalc.aifabric.algorithms compare --size 64MB --ranks 512 --bw 400G --alpha 5us
    python -m netcalc.aifabric.algorithms crossover --ranks 512 --bw 400G --alpha 5us
    python -m netcalc.aifabric.algorithms hierarchical --size 1GB --servers 64 --gpus 8 --bw 400G --intra-bw 3.6T
"""

import argparse
import math

from netcalc.units import fmt_size, fmt_time, parse_rate, parse_size, parse_time


def ring_time(size_bytes, ranks, bw_bps, alpha_s=0.0):
    """Ring all-reduce time (s)."""
    return 2 * (ranks - 1) * alpha_s + 2 * (ranks - 1) / ranks * size_bytes * 8 / bw_bps


def tree_time(size_bytes, ranks, bw_bps, alpha_s=0.0, efficiency=1.0):
    """Pipelined double-binary-tree all-reduce time (s), first-order model.

    ``efficiency`` is the fraction of link bandwidth the pipelined tree achieves.
    """
    return 2 * math.log2(ranks) * alpha_s + 2 * size_bytes * 8 / (bw_bps * efficiency)


def halving_doubling_time(size_bytes, ranks, bw_bps, alpha_s=0.0):
    """Recursive halving-doubling (Rabenseifner) all-reduce time (s).

    >>> halving_doubling_time(1e6, 2, 8e6, 0.0)
    1.0
    """
    return 2 * math.log2(ranks) * alpha_s + 2 * (ranks - 1) / ranks * size_bytes * 8 / bw_bps


def hierarchical_time(size_bytes, servers, gpus_per_server, inter_bps, intra_bps, alpha_s=0.0,
                      intra_alpha_s=0.0):
    """Hierarchical all-reduce: intra reduce-scatter, inter ring on shards, intra all-gather."""
    g = gpus_per_server
    intra = 2 * ((g - 1) * intra_alpha_s + (g - 1) / g * size_bytes * 8 / intra_bps)
    inter = ring_time(size_bytes / g, servers, inter_bps, alpha_s) if servers > 1 else 0.0
    return intra + inter
